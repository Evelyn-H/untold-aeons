import os
import re
import discord
import dice
import npc

client = discord.Client()

C_SUCCESS_ADV = 0x47eb47
C_SUCCESS = 0x4799eb
C_SUCCESS_DISADV = 0xebeb47
C_FAILURE_ADV = 0xeb9947
C_FAILURE = 0xe61919
C_FAILURE_DISADV = 0x8a0f0f

# additional colors for CoC
C_HARD_SUCCESS = 0x47ebeb
C_CRITICAL_SUCCESS = C_SUCCESS_ADV #0x99eb47 #0xeb47eb

coc_help_message = """\
`!coc <modifiers>`: a d100 roll with optional bonus / penalty dice
`!coc <skill> <modifiers>`: a skill check with the given skill value and optional bonus / penalty dice
(alternatively, you can also use `!croll`, and `!cocroll` instead of `!coc`)

Modifiers (i.e. bonus and penalty dice) can be added as follows:
  - bonus dice: `bonus`, `b`, or `+`
  - penalty dice: `penalty`, `p`, or `-`
Modifiers will cancel out automatically if you include both bonus and penalty dice

Examples:
    `!coc`: simple d100 roll
    `!coc +`: simple d100 roll with a bonus die
    `!coc 72`: skill check with a skill of 72
    `!coc 50+`: skill check with a bonus die
    `!coc 20 penalty`: skill check with a penalty die
    `!coc 50 ++-`: skill check with 2 bonus die and a penalty die, resulting in a single bonus die after cancelling out
"""

def build_ua_roll_embed(success, failure, adv, disadv):
    total_success = success - failure
    total_adv = adv - disadv
    if total_success > 0 and total_adv > 0:
        title = "Success with Advantage"
        colour = C_SUCCESS_ADV
    elif total_success > 0 and total_adv == 0:
        title = "Success"
        colour = C_SUCCESS
    elif total_success > 0 and total_adv < 0:
        title = "Success with Drawback"
        colour = C_SUCCESS_DISADV
    elif total_success <= 0 and total_adv > 0:
        title = "Failure with Advantage"
        colour = C_FAILURE_ADV
    elif total_success <= 0 and total_adv == 0:
        title = "Failure"
        colour = C_FAILURE
    elif total_success <= 0 and total_adv < 0:
        title = "Failure with Drawback"
        colour = C_FAILURE_DISADV


    def format_plural(n, singular, plural):
        return (singular if abs(n) == 1 else plural)

    description = ""
    description += f"{success} - {failure} = **"
    if total_success > 0:
        description += str(total_success) + "** " + format_plural(total_success, "success", "successes")
    else:
        description += str(-total_success) + "** " + format_plural(total_success, "failure", "failures")
    # description += f"  *({success}/{failure})*\n"
    description += f"\n{adv} - {disadv} = **"
    if total_adv >= 0:
        description += str(total_adv) + "** " + format_plural(total_adv, "advantage", "advantages")
    else:
        description += str(-total_adv) + "** " + format_plural(total_adv, "drawback", "drawbacks")
    # description += f"  *({adv}/{disadv})*"
    
    embed = discord.Embed(title=title, description=description, colour=colour)
    # embed.set_footer(text=footer)
    return embed

def build_coc_roll_embed(total, tens, units, success_level=None, reason=None):
   
    if success_level is not None:
        if success_level == dice.coc.SuccessLevel.CRITICAL_SUCCESS:
            title = "Critical Success!"
            colour = C_CRITICAL_SUCCESS
        elif success_level == dice.coc.SuccessLevel.EXTREME_SUCCESS:
            title = "Extreme Success!"
            colour = C_SUCCESS_ADV
        elif success_level == dice.coc.SuccessLevel.HARD_SUCCESS:
            title = "Hard Success!"
            colour = C_HARD_SUCCESS
        elif success_level == dice.coc.SuccessLevel.REGULAR_SUCCESS:
            title = "Success"
            colour = C_SUCCESS
        elif success_level == dice.coc.SuccessLevel.FAILURE:
            title = "Failure"
            colour = C_FAILURE
        elif success_level == dice.coc.SuccessLevel.FUMBLE:
            title = "Fumble!"
            colour = C_FAILURE_DISADV
    else:
        title = f"{total}"
        colour = 0x202225

    description = f"**{total - units}**{' '+str(tens) if len(tens) > 1 else ''} + **{units}** = **{total}**"
    if reason:
        description += f"\n**Reason**: {reason}"
    
    embed = discord.Embed(title=title, description=description, colour=colour)
    # embed.set_footer(text=footer)
    return embed

def parse_command(message, prefix):
    # allow for "synonymous" commands
    # print(message.content, prefix)
    if isinstance(prefix, list):
        for p in prefix:
            if (value := parse_command(message, p)) is not None: # yay recursion!
                return value
    else:
        if message.content.startswith(prefix):
            return message.content[len(prefix)+1:]

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    # set status message
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="accursed flutes"))
    

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # CoC Dice roll
    if (arguments := parse_command(message, ["!cocroll", "!coc", "!croll"])) is not None:
        print("test")
        match = re.match(r"^\s*(?P<skill>\d*)\s*(?P<modifiers>(?:bonus|b|\+|penalty|p|-|\s+)*)(?:!\s*(?P<reason>.*))?$", arguments)
        if match:
            print(match.group('skill'), "---", match.group('modifiers'))
            # this is kinda janky, but if you just count 'b', 'p', '+', and '-'
            # and ignore other letters it'll work, cause 'bonus' and 'penalty' only contain a single of those letters each
            positive_modifiers = match.group('modifiers').count('b') + match.group('modifiers').count('+')
            negative_modifiers = match.group('modifiers').count('p') + match.group('modifiers').count('-')
            total_modifiers = positive_modifiers - negative_modifiers

            try:
                # see if a skill value was given or not
                if match.group('skill'):
                    # roll and also check what type of success it was
                    skill = int(match.group('skill'))
                    total, tens, units, success_level = dice.coc.roll(skill, total_modifiers)
                    # await message.channel.send(f"{success_level.__class__.__repr__(success_level)},  {tens} + {units} = {total}")
                    embed = build_coc_roll_embed(total, tens, units, success_level, reason=match.group('reason'))

                else:
                    # don't do success level checks and just output a dice roll number
                    total, tens, units = dice.coc.d100(total_modifiers)
                    # await message.channel.send(f"{tens} + {units} = {total}")
                    embed = build_coc_roll_embed(total, tens, units, reason=match.group('reason'))

                embed.set_footer(text=f"@{message.author.display_name}")
                await message.channel.send(embed=embed)
            
            except dice.DiceError as error:
                await message.channel.send(error.message)


        else:
            #TODO: add mini-tutorial here
            embed = discord.Embed(title="Dice Roll Usage:", description=coc_help_message)
            await message.channel.send(embed=embed)
            # await message.channel.send("Incorrect syntax.\n\n" + coc_help_message)

    # UA dice roll
    if (arguments := parse_command(message, ["!uaroll", "!ua"])) is not None:
        skill, difficulty = map(int, filter(None, map(str.strip, arguments.split(" "))))

        try:
            success, failure, adv, disadv = dice.ua.roll(skill, difficulty, cancel_totals=False)
        except dice.DiceError as error:
            await message.channel.send(error.message)
            return
        
        embed = build_ua_roll_embed(success, failure, adv, disadv)
        # embed = discord.Embed(title="Test title", description="Some random text goes here...", colour=C_SUCCESS_ADV)
        embed.set_footer(text=f"@{message.author.display_name}")

        await message.channel.send(embed=embed)
        

    # NPG generation
    if (arguments := parse_command(message, "!npc")) is not None:
        print("generating npc")
        character = npc.Character()
        await message.channel.send(embed=character.generate_embed())

    # NPG generation
    if (arguments := parse_command(message, ["!rollstats", "!rollstat", "!stats"])) is not None:
        print("rolling stats")

        low_stats = [dice.d(6, 3) * 5 for _ in range(5)]
        high_stats = [(dice.d(6, 2) + 6) * 5 for _ in range(3)]

        total = sum(low_stats) + sum(high_stats)
        expected_total = 91.5  # expected "average"
        std_dev = 16.5 #ish

        print(total / 5)

        if expected_total - std_dev * 0.5 < total / 5 < expected_total + std_dev * 0.5:
            averageness = None
        elif expected_total - std_dev * 1.0 < total / 5 < expected_total - std_dev * 0.5:
            averageness = "below average"
        elif total / 5 < expected_total - std_dev * 1.0:
            averageness = "*well* below average"
        elif expected_total + std_dev * 0.5 < total / 5 < expected_total + std_dev * 1.0:
            averageness = "above average"
        elif expected_total + std_dev * 1.0 < total / 5:
            averageness = "*well* above average"


        title = "Random PC stats"
        description =  f"3d6 x 5: **{low_stats}**\n"
        description += f"2d6+6 x 5: **{high_stats}**\n"
        description += f"These rolls are {averageness}.\n\n" if averageness is not None else "\n"
        description += f"Use the first set of numbers for STR, DEX, CON, APP, and POW.\nUse the second set for SIZ, INT, and EDU."

        embed = discord.Embed(title=title, description=description)
        await message.channel.send(embed=embed)


    
token = os.environ['BOT_TOKEN']
client.run(token)
