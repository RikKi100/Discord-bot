import discord
from discord.ext import tasks
import aiohttp
import asyncio
import os

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

if not TOKEN or not CHANNEL_ID:
    print("[ERROR] DISCORD_TOKEN or CHANNEL_ID is not set.")
    exit()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

client = discord.Client(intents=intents)

last_message = ""

@tasks.loop(seconds=30)
async def fetch_online_players():
    global last_message
    await client.wait_until_ready()
    print('[DEBUG] Starting CripZ check...')

    try:
        headers = {'Accept': 'application/json'}
        async with aiohttp.ClientSession() as session:
            async with session.get('https://saesrpg.uk/server/live/', headers=headers) as resp:
                if resp.status != 200:
                    print(f"[ERROR] Server returned status: {resp.status}")
                    return
                
                try:
                    data = await resp.json()
                except aiohttp.ContentTypeError:
                    text = await resp.text()
                    print(f"[ERROR] Failed to parse JSON. Response content:\n{text}")
                    return

        print("[DEBUG] Successfully fetched player data.")

        online_cripz = []
        for player in data.get('players', []):
            name = player.get('name', '')
            team = player.get('team', '')
            print(f"[DEBUG] Player: {name} - Team: {team}")
            if 'CripZ~' in name or 'CripZ~' in team:
                class_spawn = player.get('class', 'Unknown')
                print(f"[DEBUG] Found CripZ player: {name} ({class_spawn})")
                online_cripz.append(f"{name} ({class_spawn})")

        channel = client.get_channel(CHANNEL_ID)
        if not channel:
            print("[ERROR] Channel is None. Check your CHANNEL_ID.")
            return

        message = "**CripZ Members Online:**\n" + "\n".join(online_cripz) if online_cripz else "No CripZ members online."

        if message != last_message:
            await channel.send(message)
            last_message = message
            print("[DEBUG] Message sent.")
        else:
            print("[DEBUG] No change in CripZ player list. Skipping message.")

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    if not fetch_online_players.is_running():
        fetch_online_players.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower() == '!test':
        await message.channel.send('Bot is working!')

client.run(TOKEN)
