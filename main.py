import discord
import os
import datetime
import asyncio
import aiohttp
from bs4 import BeautifulSoup
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
CHANNEL_ID_BLOG = 906300174148726785
ROLE_ID_RAIDS = 1164782256418721853
ROLE_ID_BLOG = 1378092973086212116

pause_until = None
cog = None  #prevents duplicate task starts


@client.event
async def on_ready():
    global cog
    if cog is None:
        print(f"Logged in as {client.user}")
        cog = MyCog(client)


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

        self.seen_blog_urls = set()
        self.last_ping_date = None

        self.daily_ping_task.start()
        self.blog_check_task.start()

    #Daily

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

    #Blog

    @tasks.loop(minutes=1)
    async def blog_check_task(self):
        url = "https://blog-en.lordofheroes.com"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return

                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    posts = soup.select(
                        "article.post-card a.post-card-image-link"
                    )[:5]

                    # Notify oldest → newest
                    for post in reversed(posts):
                        post_url = post.get("href")

                        if not post_url:
                            continue

                        if not post_url.startswith("http"):
                            post_url = f"https://blog-en.lordofheroes.com{post_url}"

                        if post_url in self.seen_blog_urls:
                            continue

                        self.seen_blog_urls.add(post_url)

                        channel = self.client.get_channel(CHANNEL_ID_BLOG)
                        if channel:
                            await channel.send(
                                f"<@&{ROLE_ID_BLOG}> (=＾● ⋏ ●＾=)づﾉ 📰\n{post_url}"
                            )

        except Exception as e:
            logger.error(f"Error in blog_check_task: {e}")

    @blog_check_task.before_loop
    async def before_blog_check(self):
        await self.client.wait_until_ready()


client.run(TOKEN)
