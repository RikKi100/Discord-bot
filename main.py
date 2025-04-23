import discord
import aiohttp
import asyncio
import os

# Load your token and channel from Railway environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

# Set up intents for the bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Define your bot using a custom class
class CripzBot(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def setup_hook(self):
        print('[DEBUG] Running setup_hook...')
        self.bg_task = self.loop.create_task(self.fetch_online_players())

    async def on_ready(self):
        print(f'[DEBUG] Logged in as {self.user} (ID: {self.user.id})')

    async def fetch_online_players(self):
        await self.wait_until_ready()
        while True:
            print('[DEBUG] Starting CripZ check...')
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get('https://saesrpg.uk/server/live/') as resp:
                        if resp.status != 200:
                            print(f"[ERROR] Server returned status: {resp.status}")
                            await asyncio.sleep(30)
                            continue
                        data = await resp.json()

                print("[DEBUG] Successfully fetched player data.")

                online_cripz = []
                for player in data['players']:
                    name = player.get('name', '')
                    team = player.get('team', '')
                    if 'CripZ~' in name or 'CripZ~' in team:
                        class_spawn = player.get('class', 'Unknown')
                        print(f"[DEBUG] Found CripZ player: {name} ({class_spawn})")
                        online_cripz.append(f"{name} ({class_spawn})")

                channel = self.get_channel(CHANNEL_ID)
                if not channel:
                    print("[ERROR] Channel is None. Check your CHANNEL_ID.")
                    await asyncio.sleep(30)
                    continue

                if online_cripz:
                    message = "**CripZ Members Online:**\n" + "\n".join(online_cripz)
                else:
                    message = "No CripZ members online."

                await channel.send(message)
                print("[DEBUG] Message sent.")

            except Exception as e:
                print(f"[ERROR] Exception occurred: {e}")

            await asyncio.sleep(30)

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.lower() == '!test':
            await message.channel.send('Bot is working!')

# Start the bot
client = CripzBot(intents=intents)
client.run(TOKEN)
