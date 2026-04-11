import discord
import os
import datetime
import asyncio
from discord.ext import tasks
import pytz
import logging
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents, max_messages=1000)

DAILY_PING_HOUR = 3  # UTC
CHANNEL_ID = 856978188974030858
ROLE_ID_RAIDS = 1164782256418721853

pause_until = None
cog = None  # prevents duplicate task starts
startup_sent = False


@client.event
async def on_ready():
    global cog, startup_sent

    if cog is None:
        print(f"Logged in as {client.user}")
        cog = MyCog(client)

    # startup message (only once)
    if not startup_sent:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            await channel.send("Thank you (˃̣̣̥ᯅ˂̣̣̥)")
        startup_sent = True


@client.event
async def on_message(message):
    global pause_until

    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("*catfish noises*")

    if message.content.startswith("$pause"):
        pause_until = datetime.datetime.now(pytz.utc) + datetime.timedelta(hours=24)
        await message.channel.send("*sleeping for 24 hours*")

    if message.content.startswith("$unpause"):
        pause_until = None
        await message.channel.send("*waking up*")


class MyCog:
    def __init__(self, client: discord.Client):
        self.client = client
        self.last_ping_date = None

        self.daily_ping_task.start()

    # Daily
    @tasks.loop(seconds=30)
    async def daily_ping_task(self):
        global pause_until

        now = datetime.datetime.now(pytz.utc)

        if pause_until and now < pause_until:
            return

        # Tuesday–Sunday (Mon = 0)
        if not (1 <= now.weekday() <= 6):
            return

        target_time = now.replace(
            hour=DAILY_PING_HOUR,
            minute=0,
            second=0,
            microsecond=0,
        )

        if now >= target_time and self.last_ping_date != now.date():
            channel = self.client.get_channel(CHANNEL_ID)
            if channel:
                await channel.send(
                    f"<@&{ROLE_ID_RAIDS}> woof woof bark! GRR.... ヽ(ｏ`皿′ｏ)ﾉ "
                )
                self.last_ping_date = now.date()

    @daily_ping_task.before_loop
    async def before_daily_ping(self):
        await self.client.wait_until_ready()


client.run(TOKEN)
