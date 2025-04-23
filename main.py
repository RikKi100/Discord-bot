import discord
import aiohttp
import asyncio
import json
from discord.ext import tasks

# ========== CONFIGURATION ==========
DISCORD_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHANNEL_ID = YOUR_CHANNEL_ID_HERE  # Example: 123456789012345678
UPDATE_INTERVAL = 30  # seconds
CRIPZ_ORG_NAME = "CripZ~"
# ====================================

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

message_to_edit = None

async def fetch_online_cripz():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://saesrpg.uk/server/live/") as resp:
            if resp.status != 200:
                return []
            data = await resp.json()

            cripz_players = []
            for player in data.get('players', []):
                if player.get('team') == CRIPZ_ORG_NAME:
                    cripz_players.append({
                        'name': player.get('name'),
                        'class': player.get('team')
                    })
            return cripz_players

@tasks.loop(seconds=UPDATE_INTERVAL)
async def update_cripz_online():
    global message_to_edit
    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("Couldn't find the channel. Check the CHANNEL_ID.")
        return

    players = await fetch_online_cripz()

    if players:
        content = "**CripZ~ Members Currently Online:**\n\n"
        content += "| Player Name | Class (Team) |\n"
        content += "|-------------|--------------|\n"
        for p in players:
            content += f"| {p['name']} | {p['class']} |\n"
    else:
        content = "**No CripZ~ members currently online.**\n"

    content += f"\n(Last updated: <t:{int(discord.utils.utcnow().timestamp())}:R>)"

    try:
        if message_to_edit is None:
            message_to_edit = await channel.send(content)
        else:
            await message_to_edit.edit(content=content)
    except Exception as e:
        print(f"Error updating message: {e}")

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")
    update_cripz_online.start()

client.run(DISCORD_TOKEN)
