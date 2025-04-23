import discord
from discord.ext import tasks
import aiohttp
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    check_online.start()

@tasks.loop(seconds=30)
async def check_online():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://saesrpg.uk/server/live/') as response:
            if response.status != 200:
                print('Failed to fetch data')
                return
            data = await response.json()

            online_players = []
            for player in data["players"]:
                if player.get("team") == "Organization" and player.get("organisation", "").startswith("CripZ"):
                    online_players.append(f'{player["name"]} - Spawned as {player["class"]}')

            channel = client.get_channel(CHANNEL_ID)
            if channel:
                message_content = "**CripZ Members Online:**\n" + "\n".join(online_players) if online_players else "No CripZ members online."
                await channel.send(message_content)

client.run(TOKEN)
