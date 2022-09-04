import requests
import discord
from discord.ext import commands
import os
import asyncio
import aiohttp
import logging
import argparse

from sqlalchemy import create_engine
from constants import SQLITE_DB_PREFIX
from sqlalchemy.orm import Session
from sqlalchemy import MetaData
from dbschema import mapper_registry, CalendarSubscription

from campusgroups import *

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

@bot.command()
async def sync(ctx, *args):
	logger.info('sync')
	await ctx.send("sync")

@bot.command()
async def subscribe(ctx, *args):
	logger.info('sub')
	if len(args) > 0:
		
		queryarg = " ".join(args)

		logger.info("subscription arg: " + queryarg)
		with Session(engine) as dbsession:
			if queryarg.isnumeric():
				group_id = int(queryarg)
			else:
				groups = dbsession.query(CampusGroups).filter(CampusGroups.name.contains(queryarg)).all()
				logger.debug(groups)
				if len(groups) > 1:
					await ctx.send("search query \"{}\" returned more than one group. Please try another search term or enclose the group name in quotes".format(queryarg))
					groupList = [g.name + " (" + str(g.identifier) + ")"  for g in groups]
					groupList = "\n - ".join(groupList)
					grouplistmsg = "***groups returned:*** \n" + " - " + groupList
					if len(grouplistmsg) > 2000:
						grouplistmsg = grouplistmsg[:1500] + "\n ..."
					await ctx.send(grouplistmsg)
				elif len(groups) == 0:
					await ctx.send("search query {} returned no groups. Please try another search term" % queryarg)

				group_id = groups[0].identifier
			logger.debug(group_id)
			logger.debug(ctx.message.guild.id)
			newsub = CalendarSubscription()
			newsub.group_id = group_id
			newsub.server_id = ctx.message.guild.id 
			dbsession.add(newsub)
			dbsession.commit()
			await ctx.send("Successfuly subscribed to {} (id: {})".format(groups[0].name, groups[0].identifier))
	else:
		await ctx.send("you need to specify which CampusGroups group you want so subscribe to")


@bot.command()
async def unsubscribe(ctx, *args):
	logger.info('usub')
	await ctx.send("unsubscribe")

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
