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
        print(f"[DEBUG] Full player data received: {data}")

        # TEMP: Send all online players, not just CripZ
        player_list = [f"{p.get('name', 'Unknown')} ({p.get('team', 'Unknown')})" for p in data.get('players', [])]
        message = "**All Online Players:**\n" + "\n".join(player_list[:20])  # Limit to 20 to avoid spam

        print(f"[DEBUG] CHANNEL_ID = {CHANNEL_ID}")
        channel = client.get_channel(CHANNEL_ID)
        print(f"[DEBUG] Channel object: {channel}")
        if not channel:
            print("[ERROR] Could not find channel. Check CHANNEL_ID and bot's access.")
            return

        await channel.send(message)
        print("[DEBUG] Message sent.")

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    
    # Test message on startup to confirm it can send
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("Bot is online and watching SAES players!")
    else:
        print("[ERROR] Could not find the channel on startup.")
    
   
