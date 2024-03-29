import os
import re
import random
import asyncio
from fuzzywuzzy import fuzz
import discord
import commands


intents = discord.Intents.default()
intents.members = True
intents.reactions = True

client = discord.Client(intents=intents)

bot = commands.Bot()

# main commands
bot.register_command(commands.roll.roll, ["!roll", "!r", "/roll", "/r"], fancy=True)
bot.register_command(commands.roll.roll_simple, ["!d"], fancy=True, require_space=False)
bot.register_command(commands.coc.roll, ["!cocroll", "!coc", "!croll", "!c"])
bot.register_command(commands.coc.roll_multiple, ["!c+"])
bot.register_command(commands.ua.roll, ["!uaroll", "!ua"])
bot.register_command(commands.dark.roll, ["!dark", "!cdark"])
bot.register_command(commands.dg.roll, ["!dgroll", "!dg"])
bot.register_command(commands.mothership.roll_command, ["!mothership", "!ms"])
bot.register_command(commands.npc.generate_npc, ["!npc"], add_footer=False)
bot.register_command(commands.npc.generate_name, ["!names", "!name"], add_footer=False)
bot.register_command(commands.npc.roll_stats, ["!rollstats", "!rollstat", "!stats"], add_footer=False)
bot.register_command(commands.improvement.improvement, ["!improvement", "!improve"])

# little help message for people who are used to the old bot ^^
@bot.command(["/croll"])
def new_bot_help(message):
    return "This no longer works, try: `!coc <skill value>` instead!\n For more details, try: `!coc help`."

# lists all available commands
@bot.command(["!commands", "!plzhalp", "!plzhelp", "!plshalp", "!plshelp", "!pleasehelp"], add_footer=False)
def list_commands(message):
    return {'title': "Available Commands:", 'description': """\
`!coc <skill value> <modifiers (optional)>`: Call of Cthulhu skill check roller
`!roll <dice>`: generic dice roller (e.g. damage rolls and such)
`!name`: generate a random name
`!names <amount> <gender (optional)>`: generate multiple names, optionally only male / female names
`!npc`: simple NPC generator
`!stats` or `!rollstats`: roll stats for CoC character creation
"""}

# coin flip
@bot.command(["!coinflip", "!coin", "!flip"])
def coinflip(message):
    return {"title": random.choice(["+","-"])}


# random card
@bot.command(["!card", "!draw"])
def randomcard(message):
    # return {"title": random.choice(["+","-"])}
    n = random.randint(1, 13)
    suit = random.choice(["C", "S", "D", "H"])

    r_desc = {1: "Ace", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Jack", 12: "Queen", 13: "King"}
    r_desc_suits = {"C": "Clubs", "S": "Spades", "D": "Diamonds", "H": "Hearts"}
    description = f"{r_desc[n]} of {r_desc_suits[suit]}"

    replacements = {1: "A", 10: "T", 11: "J", 12: "Q", 13: "K"}
    number = replacements[n] if n in replacements else str(n) 
    url = f"https://raw.githubusercontent.com/Xadeck/xCards/master/png/face/{number}{suit}%401x.png"
    print(url)
    return {"title": description, "image": {"url": url}}


# major arcana
def get_tarot_card(include_reverse=False):
    card = random.randint(0, 21)
    reversed = include_reverse and (random.randint(0, 1) == 1)
    file = f"{card}.jpg" if not reversed else f"reverse-{card}.jpg"
    return f'images/tarot/{file}'

async def majorarcana(message, ctx):
    await ctx.channel.send(file=discord.File(get_tarot_card(include_reverse=True)))

async def tarot(message, ctx):
    await ctx.channel.send(file=discord.File((get_tarot_card(include_reverse=False))))

bot.register_command(majorarcana, ["!majorarcana"], add_footer=False, fancy=True)
bot.register_command(tarot, ["!tarot"], add_footer=False, fancy=True)


# quick command to link the amazing 100 CoC tips guide
@bot.command(["!100"], add_footer=False)
def tips_100(message):
    return {
        "title": "/r/callofcthulhu - 100 tips for any non-functioning Call of Cthulhu Keeper",
        "description": "",
        "url": "https://www.reddit.com/r/callofcthulhu/comments/8gb0fc/100_tips_for_any_nonfunctioning_call_of_cthulhu/"
    }

@bot.command(["!whalefacts", "!whalefact"])
def tips_100(message):
    return random.choice([
        "Male humpback whales found in U.S. waters sing complex songs in winter breeding areas in waters near Hawaii, in the Caribbean, and elsewhere that can last up to 20 minutes and be heard miles away.",
        "The blue whale is the largest animal that ever lived and can grow to 90 or more feet and weigh as much as 24 elephants! That’s more than 330,000 pounds (150,000 kg).",
        "Some species of whales are among the longest lived mammals. Scientists estimate bowhead whales (a baleen whale found in the Arctic) can live for more than 200 years, and killer whales (a toothed whale found in various habitats worldwide) can live for more than 100 years.",
        "Killer whales are highly social and often travel in groups that are matrifocal—a family unit focused or centered on the mother",
        "Beluga whales have flexible necks, allowing them to move their heads. Their complex communication repertoire of whistles, clicks, and chirps has prompted the nickname “canaries of the sea.",
        "Gray whales make one of the longest annual migrations of any mammal: they travel about 10,000 miles (16,000 km) round trip!",
        "The minke whale is the smallest baleen whale in North American waters.",
        "North Atlantic right whales gather small organisms near the water surface, straining seawater with their long baleen plates. The whales’ surface feeding behavior and buoyancy make them vulnerable to collisions.",
        "Sperm whales were almost driven to extinction by commercial whalers who sought the whales’ blubber and the unique oil derived from the “spermaceti organ” found in their massive heads. The spermaceti organ is a key part of their echolocation system.with ships.",
        "In 2014, a Cuvier’s beaked whale made the deepest and longest dive ever recorded for a cetacean when it reached a depth of 1.9 miles (2,992 m) and stayed submerged for more than 2 hours.",
        "Loud noises produced by industrial activities at sea, like drilling for oil, can damage whales’ hearing.",
        "The heart of a blue whale is as big as a small car.",
    ])

@bot.command(["!coffeeplease", "!coffee"])
def tips_100(message):
    return "☕"

@bot.command(["!teaplease", "!tea"])
def tips_100(message):
    return random.choice(["🍵", "☕"])


@bot.command(["!beerplease", "!beer", "!craftbeerplease", "!craftbeer"])
def tips_100(message):
    return "🍺"

@bot.command(["!spacemeadplease", "!spacemead"])
def tips_100(message):
    return random.choice(["🍹","🧋","🧉","🍶"])

@bot.command(["!hotchocplease", "!hotchoc"])
def tips_100(message):
    return random.choice(["<:hotchoc:809943795985809423>"])
 
# (hopefully) temporary fix for the Friend Time bot change / confusion 
# @bot.command(["-ft set"])
async def friendtime_help(message, ctx):
    if len(message.strip()) > 0:
        # make sure this message comes after the Friend Time error message
        await asyncio.sleep(1.0)
        return "The timezone bot was updated.\nTry using `-ft set` (without a timezone) instead and it'll guide you through the setup."
bot.register_command(friendtime_help, ["-ft set"], fancy=True)



# for the pub-quiz
async def answer(message, ctx):
    out_channel = discord.utils.get(ctx.guild.channels, name='quiz-answers')
    if not out_channel:
        return "No answer channel found."

    in_channel = ctx.channel
    match = re.match(r"^\s*(?P<number>\d+)\s*(?P<answer>.+)$", message)
    if not match:
        return "Please specify the number of the question and the answer.\n E.g. `!answer 4 cthulhu`"
    
    print(match.group('number'), "---", match.group('answer'))

    await out_channel.send(f"({match.group('number')}) **{in_channel.name}**: {match.group('answer')}")
    return "Answer recorded!"
 
bot.register_command(answer, ["!answer"], add_footer=False, fancy=True, locked=True)




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

enabled_channel_categories = list(map(lambda i: i.lower(), ["test", "channels for one-shots", "campaigns", "the weaver's den", "pub quiz", "Play By Post", "one shots to be completed"]))

# Channel shenanigans
@client.event
async def on_guild_channel_create(channel):
    if not isinstance(channel, discord.TextChannel):
        return
    if not channel.category.name.lower() in enabled_channel_categories:
        return

    await channel.send(
"""Hello!
You can invite people to this channel by typing: `!invite @Name`
Due to a Discord limitation names usually won't get autocompleted if you try to @mention them.
Just do your best to write out most of the name anyway and it'll still work!
""")

async def invite(message, meta_message, try_matching=True, owner_override=None):
    print(meta_message.guild.name, meta_message.guild.id)


    if not meta_message.channel.category.name.lower() in enabled_channel_categories:
        return "This command can't be used in this channel."

    # make sure the user has the right permissions
    owner = owner_override or meta_message.author
    owner_permissions = meta_message.channel.permissions_for(owner)
    if not owner_permissions.manage_channels:
        return "You are not allowed to invite people to this channel."

    if len(meta_message.mentions) == 0:
        if try_matching:
            # first try to manually "autocomplete" the user
            all_users = meta_message.guild.members
            # all_usernames = [(u.name, u) for u in all_users]
            # all_nicknames = [(u.nick, u) for u in all_users if u.nick]
            # print(all_usernames)
            # print(all_nicknames)

            all_usernames = [(u.name, u) for u in all_users] + [(u.nick, u) for u in all_users if u.nick]

            names = list(filter(None, map(str.strip, message.split('@'))))
            if len(names) == 0:
                return "You must mention (@Name) a person to invite."

            ratios = [(fuzz.partial_ratio(nick, names[0]), user) for nick, user in all_usernames]
            ratios.sort(key=lambda u: u[0], reverse=True)
            print(list(map(lambda u: (u[0], u[1].display_name), ratios[:5])))

            # editing the message *should* avoid unnecessary user pings
            # await meta_message.channel.send(f"Did you mean: {ratios[0][1].mention}?")
            message = await meta_message.channel.send(f"Did you mean this user?")
            await asyncio.sleep(0.1) # not sure if this is entirely necessary, but just to be safe ^^
            await message.edit(content=f"Did you mean: {ratios[0][1].mention}?")
            await message.add_reaction('👍')
            await message.add_reaction('🚫')
            return

        else:
            # if that fails... well... too bad :p
            return "You must mention (@Name) a person to invite."

    for user in meta_message.mentions:
        # don't allow inviting goats
        if "Goat" in [r.name for r in user.roles]:
            return f"Couldn't invite {user.mention}, they need to pick a role first."

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
    keeper_role = list(filter(lambda role: role.name in ["Keeper of Arcane Lore"], meta_message.guild.roles))[0]
    # and delete the permissions for them
    if keeper_role:
        await meta_message.channel.set_permissions(keeper_role, overwrite=None)

    users = list(map(lambda u: u.mention, meta_message.mentions))
    users_str = ", ".join(users[:-1]) + " and " + users[-1] if len(users) > 1 else users[0]
    return f"Welcome to {meta_message.channel.mention}, {users_str}!"

bot.register_command(invite, ["!invite"], add_footer=False, fancy=True, locked=True)

@client.event
async def on_reaction_add(reaction, user):
    if user == client.user:
        return
    
    # this only runs if the *original* reaction was from the bot itself
    if reaction.me:
        print("reaction added:", repr(reaction))
        if reaction.emoji == '👍':
            users = await reaction.users().flatten()
            users = [u for u in users if u != client.user]
            owner = users[0]

            return_message = await invite(f"{user.mention}", reaction.message, try_matching=False, owner_override=owner)
            await reaction.message.channel.send(str(return_message))
            await reaction.message.delete()

        if reaction.emoji == '🚫':
            await reaction.message.delete()

    # if the message being reacted to is from the bot
    if reaction.message.author == client.user:
        print("reacted to me:", repr(reaction))
        if reaction.emoji == '🚫':
            await reaction.message.delete()



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
