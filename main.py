import discord
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 906300174148726785

intents = discord.Intents.default()
client = discord.Client(intents=intents)

sent = False  # prevents duplicates on reconnect


@client.event
async def on_ready():
    global sent
    if sent:
        return

    sent = True
    print(f"Logged in as {client.user}")

    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("how could you ((유∀유|||))")


client.run(TOKEN)
