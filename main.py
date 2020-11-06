import os
import random
import asyncio
import discord
import commands

client = discord.Client()

bot = commands.Bot()

# main commands
bot.register_command(commands.roll.roll, ["!r"])
# this is just to avoid it also responding to !roll 
@bot.command(["!roll"])
def placeholder_roll(message):
    return None
bot.register_command(commands.coc.roll, ["!cocroll", "!coc", "!croll", "!c"])
bot.register_command(commands.ua.roll, ["!uaroll", "!ua"])
bot.register_command(commands.dark.roll, ["!dark", "!cdark"])
bot.register_command(commands.npc.generate_npc, ["!npc"], add_footer=False)
bot.register_command(commands.npc.generate_name, ["!names", "!name"], add_footer=False)
bot.register_command(commands.npc.roll_stats, ["!rollstats", "!rollstat", "!stats"], add_footer=False)

# little help message for people who are used to the old bot ^^
@bot.command(["/croll"])
def new_bot_help(message):
    return "This no longer works, try: `!coc <skill>` instead!\n For more details, try: `!coc help`."


#cinnamon roll!
async def cinnamon(message, ctx):
    images = list(filter(lambda f: f.startswith("cinnamon"), os.listdir("images")))
    random_image = random.choice(images)
    await ctx.channel.send(file=discord.File(f'images/{random_image}'))

bot.register_command(cinnamon, ["!cinnamon"], add_footer=False, fancy=True)

async def mention_handler(ctx):
    print("I've been mentioned!")
    if "cinnamon" in ctx.content.lower():
        await(cinnamon(ctx.content, ctx))



# TODO: For new channels
#  - print help message in new channels
#  - !new_channel <name> command to make a new channel and make the caller the owner
#    - ask for confirmation? with reactions potentially
#  - !invite @<user> command to invite people to the channel

# new permissions required:
#  - guild intents
#  - manage roles

enabled_channel_categories = list(map(lambda i: i.lower(), ["test", "channels for one-shots", "campaigns", "the weaver's den"]))

# Channel shenanigans
@client.event
async def on_guild_channel_create(channel):
    if not isinstance(channel, discord.TextChannel):
        return
    if not channel.category.name.lower() in enabled_channel_categories: #TODO: update this!
        return

    await channel.send("Hello!\nYou can invite people to this channel by typing: `!invite @Name`")

async def invite(message, meta_message):
    if not meta_message.channel.category.name.lower() in enabled_channel_categories: #TODO: update this!
        return "This command can't be used in this channel."

    if len(meta_message.mentions) == 0:
        return "You must mention (@Name) a person to invite."

    # make sure the user has the right permissions
    owner = meta_message.author
    owner_permissions = meta_message.channel.permissions_for(owner)
    if not owner_permissions.manage_channels:
        return "You are not allowed to invite people to this channel."

    # add the invite-ee to the channel
    user = meta_message.mentions[0]
    await meta_message.channel.set_permissions(user, 
        read_messages=True,
        send_messages=True
    )

    # remove the permissions from all other keepers and give them to the owner
    # first give them to the owner:
    await meta_message.channel.set_permissions(owner, 
        manage_channels=True,
        manage_permissions=True,
        manage_messages=True,
        read_messages=True,
        send_messages=True
    )
    # find the Keeper role
    keeper_role = list(filter(lambda role: role.name in ["Test", "Keeper of Arcane Lore"], meta_message.guild.roles))[0]
    # and delete the permissions for them
    await meta_message.channel.set_permissions(keeper_role, overwrite=None)

    return f"Welcome to {meta_message.channel.mention}, {user.mention}!"

bot.register_command(invite, ["!invite"], add_footer=False, fancy=True)



@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    # check for mentions
    if client.user.id in map(lambda m: m.id, message.mentions):
        await mention_handler(message)

    # handle commands
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
        # (discord.ActivityType.listening, "screams of the damned"),
        (discord.ActivityType.watching, "the shadows advance"),
        (discord.ActivityType.watching, "the stars align"),
        (discord.ActivityType.watching, "your deepest regrets"),
        (discord.ActivityType.listening, "incessant whispers"),
        (discord.ActivityType.listening, "mad pipers"),
        (discord.ActivityType.watching, "your sanity fade"),
        (discord.ActivityType.listening, "approaching footsteps"),
        (discord.ActivityType.listening, "your rushing heart"),
        (discord.ActivityType.watching, "the flames rise"),
        (discord.ActivityType.watching, "you sleep"),
        (discord.ActivityType.playing, "with your life"),
    ])
    await client.change_presence(activity=discord.Activity(type=playing_message[0], name=playing_message[1]))
    await asyncio.sleep(random.randint(60,300))
    
token = os.environ['BOT_TOKEN']
client.run(token)
