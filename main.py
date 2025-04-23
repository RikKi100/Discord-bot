import discord
import aiohttp
import asyncio
import os

# Load environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

# Set up bot intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

client = discord.Client(intents=intents)

# Background task to fetch online CripZ~ players
async def fetch_online_players():
    while True:
        await client.wait_until_ready()
        print('Checking for online CripZ members...')

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://saesrpg.uk/server/live/') as resp:
                    data = await resp.json()

            online_cripz = []
            for player in data['players']:
                if 'CripZ~' in player.get('team', '') or 'CripZ~' in player.get('name', ''):
                    name = player['name']
                    class_spawn = player.get('class', 'Unknown')
                    online_cripz.append(f"{name} ({class_spawn})")

            channel = client.get_channel(CHANNEL_ID)

            if online_cripz:
                message = "**CripZ Members Online:**\n" + "\n".join(online_cripz)
            else:
                message = "No CripZ members online."

            await channel.send(message)

        except Exception as e:
            print(f"Error fetching players: {e}")

        await asyncio.sleep(30)  # Check every 30 seconds

# When bot is ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    print('Starting background task...')
    client.loop.create_task(fetch_online_players())

# Listen for !test command
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == '!test':
        await message.channel.send('Bot is working!')

# Run bot
client.run(TOKEN)
