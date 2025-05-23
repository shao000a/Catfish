import discord
import os
import datetime
import asyncio
from discord.ext import tasks
import pytz
import logging


token = os.getenv("DISCORD_TOKEN")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents, max_messages=1000)

maint_mode = False
target_time_str = "03:00:00"

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    MyCog(client)
characters = {
    "LJohan": {"buffs": {"atk+": "self", "defup": "self"}, "debuffs": {"atkdown": "all", "provoke": "single"}, "other": {"ag+": "all"}},
    "DMikhail": {"buffs": {"atk+": "all", "spdup": "self", "agup": "self"}, "debuffs": {"agdown": "all"}, "other": {}},
    "ECharlotte": {"buffs": {"shield": "all", "agup": "self"}, "debuffs": {"atkdown": "single"}, "other": {"ag+": "all"}},
    "WFram": {"buffs": {"atkup": "self"}, "debuffs": {"atkdown": "AoE", "stun": "AoE", "defdown": "single"}, "other": {"ag+": "all"}},
    "WKrom": {"buffs": {"regen": "all"}, "debuffs": {}, "other": {"ag+": "all"}},
}

@client.event 
async def on_message(message):
    global maint_mode, target_time_str
    if message.author == client.user:
        return
    if message.content.startswith('$hello'):
        await message.channel.send('*catfish noises*')

    if message.content.startswith('$🦴'):
        await message.channel.send('nom-nom *burp* (っ˘ڡ˘ς)')
        maint_mode = True
        target_time_str = "02:00:00"
    if message.content.startswith('$🍗'):
        await message.channel.send('nom-nom *burp* (っ˘ڡ˘ς)')
        maint_mode = False

    if message.content.startswith('#'):
        query = message.content[1:].strip()  # Remove the '#' character
        command_parts = query.split()
        
        if len(command_parts) == 0:
            await message.channel.send("Invalid command format. Use '#buff_type' or '#<buff_type> <target_type>'")
            return
        
        filter_type = command_parts[0].lower()  # e.g., 'atk+'
        target_type = command_parts[1].lower() if len(command_parts) > 1 else None  # e.g., 'self'

        results = []
        for name, data in characters.items():
            for category in ['buffs', 'debuffs', 'other']:
                if filter_type in data[category]:
                    if target_type:
                        if data[category][filter_type] == target_type:
                            results.append(name)
                            break
                    else:
                        results.append(name)
                        break
        
        if results:
            if target_type:
                result_message = f"ฅ⁠^⁠•⁠ﻌ⁠•⁠^⁠ฅ {filter_type} {target_type}: " + ", ".join(results)
            else:
                result_message = f"ฅ⁠^⁠•⁠ﻌ⁠•⁠^⁠ฅ {filter_type}: " + ", ".join(results)
        else:
            if target_type:
                result_message = f"Catfish could not find anybody with '{filter_type}' {target_type} (⁠｡⁠ŏ⁠﹏⁠ŏ⁠)"
            else:
                result_message = f"Catfish could not find anybody with '{filter_type}' (⁠｡⁠ŏ⁠﹏⁠ŏ⁠)"
        
        await message.channel.send(result_message)

class MyCog:
    global maint_mode, target_time_str
    def __init__(self, client):
        self.client = client
        self.my_task.start()

    def cog_unload(self):
        self.my_task.cancel()

    @tasks.loop(seconds=1)
    async def my_task(self):
        global maint_mode
        if maint_mode == True: 
            target_time_str = "02:00:00"
        else: 
            target_time_str = "03:00:00"
        today_utc = datetime.datetime.now(pytz.utc)
        if 1 <= today_utc.weekday() < 7:
            current_time_str = today_utc.strftime("%H:%M:%S")
            if current_time_str == target_time_str:
                channel_id = 856978188974030858
                channel = self.client.get_channel(channel_id)
                if channel:
                    role_id = 1164782256418721853
                    await channel.send(f"<@&{role_id}> woof woof bark! GRR.... ヽ(ｏ`皿′ｏ)ﾉ ")
                    maint_mode = False
    @my_task.before_loop
    async def before_my_task(self):
        await self.client.wait_until_ready()

# Start the bot with a running event loop
client.run(token)
