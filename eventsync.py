import discord
import os
import asyncio
import aiohttp
import logging
@client.event
async def on_ready():
	logger.info('We have logged in as {0.user}'.format(client))

@client.event
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


client.run(os.getenv('DISCORD_TOKEN'))
