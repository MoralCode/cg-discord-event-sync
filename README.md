# CampusGroups -> Discord event sync bot

This is a discord bot that creates discord events from a calendar on CampusGroups.

This project is currently in a "proof of concept" phase, but it should be usable.

Features:
- subscribe to the calendars for groups on campus by name or id number ($subscribe and $unsubscribe commands)
- view a list of groups you are subscribed to ($list)
- pull new discord events from your subscribed campusgroups calendars with the $sync command


Because this is a proof of concept, it has a couple limitations:
- it can only sync events that are publicly visible without logging into campusgroups (i.e. set to "visible by everyone" )
- it cannot sync event locations (those also require authentication)
- it currently has no support for multiple campusgroups installations at the same time

If you know how to (legitimately) get API authentication and/or documentation information for campusgroups, please reach out!


## Set Up

1. install dependencies using `pipenv install`
2. create the database in the default location (the current directory) using `pipenv run python3 ./eventsync.py --createdb`
3. populate the list of groups by running `pipenv run python3 ./eventsync.py --importgroups`
4. create a discord bot account using the instructions [here](https://discordpy.readthedocs.io/en/stable/discord.html)
   - the bot will need these permissions:
     - manage events
     - read messages/view channels
   - the checkbox next to "Message Content Intent" (under Privileged Gateway Intents) also needs to be checked.
5. click the "reset token" button on the bot page to generate a bot token. Place this value in a file called `.env` in the root of this repository and ensure it contains the line `DISCORD_TOKEN=` followed by your token value
6. run the bot using `pipenv run python3 ./eventsync.py`


## Adding/using the bot

If you just want to use the bot and dont want to have to set everything up, you can use [this link](https://discord.com/api/oauth2/authorize?client_id=1015790312263778335&permissions=8589935616&scope=bot) to add the bot to your discord server. If you are using your own bot, you will want to use the oauth url you generated as part of the setup process above.


### Commands
Once the bot is added to the server, send a message to one of your channels using one of the following commands:

**$subscribe [club name or id]** - subscribe to a campusgroups group by name or ID 
**$unsubscribe [club name or id]** - unsubscribe from a campusgroups group by name or ID 
**$list** - show your currently active subscriptions
**$sync** - fetch calendar events from your subscriptions and create discord events for them

