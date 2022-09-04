import requests
import discord
from discord.ext import commands
import os
import asyncio
import aiohttp
import logging
import argparse
import datetime
from datetime import timezone

from sqlalchemy import create_engine
from constants import SQLITE_DB_PREFIX
from sqlalchemy.orm import Session
from sqlalchemy import MetaData
from dbschema import mapper_registry, CalendarSubscription

from campusgroups import *

from icalendar import Calendar, Event

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)
# client = discord.Client()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

COMMAND_PREFIX="cg"
COOKIES_FILE = "cookies.txt"


session = requests.Session() 



@bot.event
async def on_ready():
	logger.info('We have logged in as {0.user}'.format(bot))

def resolve_group_argument(queryarg: str, dbsession=None) -> int:
	"""takes a group argument (either a number or a string) and tries to resolve
	it to the group id.

	Returns a (boolean, List[String]) tuple indicating whether there was an error
	"""

	responsemsg = []
	if queryarg.isnumeric():
		groups = dbsession.query(CampusGroups).where(CampusGroups.identifier== int(queryarg)).all()
		return groups
	else:

		if dbsession is None:
			raise ValueError("dbsession argument should not be null when trying to resolve group ID")
		
		groups = dbsession.query(CampusGroups).filter(CampusGroups.name.contains(queryarg)).all()
		return groups


def generate_groups_list(groups) -> str:
	groupList = [g.name + " (" + str(g.identifier) + ")"  for g in groups]
	groupList = "\n - ".join(groupList)
	grouplistmsg = " - " + groupList
	if len(grouplistmsg) > 2000:
		grouplistmsg = grouplistmsg[:1500] + "\n ..."
	
	return grouplistmsg
		
async def check_groups_size(ctx, groups, queryarg) -> bool:
	"""validate the number of groups returned by the query and inform the user
	if the expected number was not received 

	Args:
		ctx (_type_): the discord message context for sending messages to the user
		groups (_type_): the list of groups returned by the query

	Returns:
		bool: True if group size was valid, False if it wasnt and the user was notified
	"""
	if len(groups) > 1:
		await ctx.send("search query \"{}\" returned more than one group. Please try another search term or enclose the group name in quotes".format(queryarg))
		
		await ctx.send("***groups returned:*** \n" + generate_groups_list(groups))
		return False
	elif len(groups) == 0:
		await ctx.send("search query {} returned no groups. Please try another search term".format(queryarg))
		return False

	return True

def get_subscription(group_id, server_id, dbsession=None):
	if dbsession is None:
		raise ValueError("dbsession argument should not be null when looking up a subscription")
	return dbsession.query(CalendarSubscription).filter(CalendarSubscription.group_id== group_id).filter(CalendarSubscription.server_id == server_id)


def get_event_id_from_ical(component):
	return component.get('summary')# + component.get('dtstart').dt

def get_event_id_from_scheduled_event(event):
	return event.name

@bot.command()
async def sync(ctx, *args):
	logger.info('sync')
	await ctx.send("Synchronizing events...")
	with Session(engine) as dbsession:
		subs = dbsession.query(CalendarSubscription).where(CalendarSubscription.server_id == ctx.message.guild.id).all()

		logger.info("beginning calendar sync")
		logger.debug("fetching existing discord events")

		events_scheduled = await ctx.message.guild.fetch_scheduled_events()
		logger.debug("filtering existing discord events")
		events_scheduled = filter(lambda e: e.creator.id==bot.user.id, events_scheduled)

		logger.debug("converting existing discord events to id form")
		existing_event_ids = [get_event_id_from_scheduled_event(e) for e in events_scheduled]


		logger.debug("fetching new campusgroups events")

		for sub in subs:
			ics_url = get_ics_url_for_group_id(sub.group.identifier)

			calendar = requests.get(ics_url)
			caldata = Calendar.from_ical(calendar.content)
			for component in caldata.walk("VEVENT"):
				if get_event_id_from_ical(component) not in existing_event_ids:
					logger.debug("found new event " +component.get('summary'))

					starttime = component.get('dtstart').dt
					
					now = datetime.datetime.now(timezone.utc)
					
					if starttime < now:
						logger.debug("event too old")
						continue
					await ctx.message.guild.create_scheduled_event(name=component.get('summary'), description=component.get('description'), start_time=component.get('dtstart').dt, end_time=component.get('dtend').dt, entity_type=discord.EntityType.external, location=component.get('location'))
	logger.debug("done")
	await ctx.send("Done synchronizing events.")


@bot.command(name="list")
async def list_subs(ctx, *args):
	logger.info('list')
	with Session(engine) as dbsession:
		groups = dbsession.query(CalendarSubscription).where(CalendarSubscription.server_id == ctx.message.guild.id).all()
		await ctx.send("***You are subscribed to the following groups:*** \n" + generate_groups_list([g.group for g in groups]))

@bot.command()
async def subscribe(ctx, *args):
	logger.info('sub')

	if len(args) < 0:
		await ctx.send("you need to specify which CampusGroups group you want so subscribe to")
		return
		
	queryarg = " ".join(args)

	logger.info("subscription arg: " + queryarg)
	with Session(engine) as dbsession:
		groups = resolve_group_argument(queryarg, dbsession=dbsession)
		logger.info(groups)
		
		if(await check_groups_size(ctx,groups,queryarg)):
			group_id = groups[0].identifier
			# https://stackoverflow.com/a/32952421/
			exists = get_subscription(group_id, ctx.message.guild.id, dbsession=dbsession).scalar() is not None

			if not exists:
				newsub = CalendarSubscription()
				newsub.group = dbsession.query(CampusGroups).where(CampusGroups.identifier == group_id).scalar()
				newsub.server_id = ctx.message.guild.id 
				dbsession.add(newsub)
				dbsession.commit()
				await ctx.send("Successfuly subscribed to {} (id: {})".format(groups[0].name, groups[0].identifier))
			else:
				await ctx.send("Subscription to {} (id: {}) already exists".format(groups[0].name, groups[0].identifier))
		


@bot.command()
async def unsubscribe(ctx, *args):
	logger.info('usub')
	if len(args) < 0:
		await ctx.send("you need to specify which CampusGroups group you want so unsubscribe from")
		return
		
	queryarg = " ".join(args)

	logger.info("unsubscription arg: " + queryarg)
	with Session(engine) as dbsession:
		groups = resolve_group_argument(queryarg, dbsession=dbsession)
		logger.info(groups)
		
		if(await check_groups_size(ctx,groups, queryarg)):
			group_id = groups[0].identifier
			
			sub = get_subscription(group_id, ctx.message.guild.id, dbsession=dbsession).scalar()
			logger.debug(sub)
			
			if sub is not None:
				sub.delete()
				dbsession.commit()
				await ctx.send("Successfuly unsubscribed from {} (id: {})".format(groups[0].name, groups[0].identifier))
			else:
				await ctx.send("Subscription to {} (id: {}) does not exist".format(groups[0].name, groups[0].identifier))
			

# @bot.command()
# async def help(ctx, arg):
#     await ctx.send("a full list of commands can be found at https://github.com/MoralCode/cg-discord-event-sync/")


if __name__ == '__main__':

	global engine

	parser = argparse.ArgumentParser(description='runs a discord bot that can sync campusgroups events with discord events')
	parser.add_argument('--database',
		default="cgsubscriptions.db",
		help='the path to the sqlite database to use. defaults to "cgsubscriptions.db" in the current directory')
	# parser.add_argument('--cached', action='store_true',
	# 					help='whether caching should be used')
	parser.add_argument('--show-cookies', action='store_true',
		help='whether to print the session id in the cookies')
	parser.add_argument('--createdb', action='store_true',
		help='whether to create a new DB')
	parser.add_argument('--importgroups', action='store_true',
		help='whether to scrape and import all groups from campusgroups')
	parser.add_argument('--debug', action='store_true',
		help='print debugging output')
	args = parser.parse_args()

	if args.debug:
		logger.setLevel(logging.DEBUG)

	# see https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#connect-strings 
	db_url = SQLITE_DB_PREFIX + args.database
	if args.debug:
		print(db_url)
	engine = create_engine(db_url, future=True)#, echo=True

	
	if args.createdb:
		mapper_registry.metadata.create_all(engine)

		# then, load the Alembic configuration and generate the
		# version table, "stamping" it with the most recent rev:
		from alembic.config import Config
		from alembic import command
		alembic_cfg = Config("./alembic.ini")
		alembic_cfg.set_main_option("sqlalchemy.url", db_url)
		command.stamp(alembic_cfg, "head")
	
	elif args.importgroups:
		all_groups = get_all_campus_groups()
		with Session(engine) as dbsession:
			for group in all_groups:
				if args.debug:
					logger.debug(group)
				dbsession.merge(group)
			dbsession.commit()


	else:
		bot.run(os.getenv('DISCORD_TOKEN'))


