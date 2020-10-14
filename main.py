import os
import random
import asyncio
import discord
import commands

client = discord.Client()

bot = commands.Bot()

bot.register_command(commands.coc.roll, ["!cocroll", "!coc", "!croll"])
bot.register_command(commands.ua.roll, ["!uaroll", "!ua"])
bot.register_command(commands.dark.roll, ["!dark", "!cdark"])
bot.register_command(commands.npc.generate_npc, ["!npc"], add_footer=False)
bot.register_command(commands.npc.generate_name, ["!names", "!name"], add_footer=False)
bot.register_command(commands.npc.roll_stats, ["!rollstats", "!rollstat", "!stats"], add_footer=False)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    await bot.on_message(message)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    # set status message
    # await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="accursed flutes"))
    while True:
        await asyncio.ensure_future(cycle_playing())
    

async def cycle_playing():
    playing_message = random.choice([
        (discord.ActivityType.listening, "accursed flutes"),
        (discord.ActivityType.listening, "Erich Zann"),
        (discord.ActivityType.watching, "the void"),
        (discord.ActivityType.playing, "with dice"),
        (discord.ActivityType.listening, "vanishing echoes"),
        (discord.ActivityType.playing, "with fate"),
        (discord.ActivityType.watching, "the end approach"),
        (discord.ActivityType.listening, "falling dice"),
        (discord.ActivityType.playing, "a dangerous game"),
    ])
    await client.change_presence(activity=discord.Activity(type=playing_message[0], name=playing_message[1]))
    await asyncio.sleep(random.randint(60,600))
    
token = os.environ['BOT_TOKEN']
client.run(token)
