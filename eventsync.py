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
from dbschema import mapper_registry

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

@bot.event
async def on_message(message):
	if message.author == client.user:
		return

	if message.content.startswith(COMMAND_PREFIX + ' sync'):
		pass
	elif message.content.startswith(COMMAND_PREFIX + ' subscribe'):
		pass
	elif message.content.startswith(COMMAND_PREFIX + ' unsubscribe'):
		pass
	elif message.content.startswith(COMMAND_PREFIX + ' help'):
		await message.channel.send("a full list of commands can be found at https://github.com/MoralCode/cg-discord-event-sync/")




if __name__ == '__main__':

	global engine

	parser = argparse.ArgumentParser(description='runs a discord bot that can sync campusgroups events with discord events')
	parser.add_argument('database', default="cgsubscriptions.db",
						help='the path to the sqlite database to use. defaults to "cgsubscriptions.db" in the current directory')
	# parser.add_argument('--cached', action='store_true',
	# 					help='whether caching should be used')
	parser.add_argument('--show-cookies', action='store_true',
						help='whether to print the session id in the cookies')
	parser.add_argument('--createdb', action='store_true',
						help='whether to create a new DB')
	parser.add_argument('--debug', action='store_true',
						help='print debugging output')
	args = parser.parse_args()



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
	
	else:
		bot.run(os.getenv('DISCORD_TOKEN'))
