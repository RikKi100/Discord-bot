import discord
import aiohttp
import asyncio
import os

TOKEN = os.getenv('DISCORD_TOKEN')  # or hardcode for testing
CHANNEL_ID = 1364554409627095060  # your real channel id

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

client = discord.Client(intents=intents)

# Save the message object globally
bot_message = None

async def fetch_online_players():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    print(f"Channel fetched: {channel}")

    global bot_message

    while not client.is_closed():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://saesrpg.uk/server/live/') as resp:
                    print(f"API status: {resp.status}")
                    data = await resp.json()
                    print(f"Data fetched.")

            online_cripz = []
            for player in data.get('players', []):
                if 'CripZ~' in player.get('team', '') or 'CripZ~' in player.get('name', ''):
                    name = player['name']
                    class_spawn = player.get('class', 'Unknown')
                    online_cripz.append(f"{name} ({class_spawn})")

            if online_cripz:
                new_message = "**CripZ Members Online:**\n" + "\n".join(online_cripz)
            else:
                new_message = "No CripZ members online."

            # If it's the first time
            if bot_message is None:
                bot_message = await channel.send(new_message)
                print("Initial message sent.")
            else:
                await bot_message.edit(content=new_message)
                print("Message updated.")

        except Exception:
            import traceback
            traceback.print_exc()

        await asyncio.sleep(30)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    client.loop.create_task(fetch_online_players())

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower() == '!test':
        await message.channel.send('Bot is working!')

client.run(TOKEN)
