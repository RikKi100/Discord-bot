import discord
from discord.ext import tasks
import aiohttp
import asyncio
import os

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

client = discord.Client(intents=intents)

@tasks.loop(seconds=30)
async def fetch_online_players():
    await client.wait_until_ready()
    print('[DEBUG] Starting CripZ check...')
    
    try:
        headers = {'Accept': 'application/json'}

        # Replace this URL with the correct one from saes.pro once you find it
        api_url = 'https://saes.pro/server/live/'  # <-- Replace this URL
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as resp:
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
            if 'CripZ~' in name or 'CripZ~' in team:
                class_spawn = player.get('class', 'Unknown')
                print(f"[DEBUG] Found CripZ player: {name} ({class_spawn})")
                online_cripz.append(f"{name} ({class_spawn})")

        channel = client.get_channel(CHANNEL_ID)
        if not channel:
            print("[ERROR] Channel is None. Check your CHANNEL_ID.")
            return

        if online_cripz:
            message = "**CripZ Members Online:**\n" + "\n".join(online_cripz)
        else:
            message = "No CripZ members online."

        await channel.send(message)
        print("[DEBUG] Message sent.")

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    fetch_online_players.start()

    # Test message to confirm bot is working on startup
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("Bot is online and checking players!")
    else:
        print("[ERROR] Could not find the channel on startup.")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower() == '!test':
        await message.channel.send('Bot is working!')

client.run(TOKEN)
