import re
import dice
from .colors import *


dg_mini_help_message = """\
Use `!dg <skill value> <modifiers>` for skill rolls (modifiers are optional)
E.g.: `!dg 70`, `!dg 45+20`, `!dg 30-20`

(Use `!dg help` for more details)
"""

dg_help_message = """\
`!dg: a plain d100 roll
`!dg <skill value>`: a skill check with the given skill value
`!dg <skill value> <modifiers>`: a skill check with the given skill value and modifiers

Additionally, you can specify a reason for the roll as follows:
`!dg <skill value> <modifiers> !<reason>`

Modifiers (i.e. bonus and penalty dice) can be added as follows:
  - bonus: `+20`, `+5`, `+40`
  - penalty: `-20`, `-5`, `-40`
Modifiers will cancel out automatically if you include both bonuses and penalties

Examples:
    `!dg`: simple d100 roll
    `!dg 72`: skill check with a skill of 72
    `!dg 70 !listen`: skill check with a skill of 70, with the reason "listen" 
    `!dg 51 +20`: skill check with a bonus of 20
    `!dg 23 -10`: skill check with a penalty of 10
    `!dg 50 +20 -10`: skill check with bonus of 20 and a penalty of 10
"""
    
# DG Dice roll
def roll(message):
    match = re.match(r"^\s*(?P<skill>\d*)\s*(?P<modifiers>(?:[+-]\d+\s*)*)(?:!\s*(?P<reason>.*))?$", message)
    if match:
        modifiers = re.findall(r"([+-]\d+)", match.group('modifiers'))
        print(match.group('skill'), "---", modifiers)
        total_modifiers = sum([int(mod) for mod in modifiers])

        reason = match.group('reason')

        try:
            # see if a skill value was given or not
            if match.group('skill'):
                # roll and also check what type of success it was
                skill = int(match.group('skill'))
                total, tens, units, success_level = dice.dg.roll(skill, total_modifiers)
                # await message.channel.send(f"{success_level.__class__.__repr__(success_level)},  {tens} + {units} = {total}")
                embed = build_dg_roll_embed(total, tens, units, success_level, reason=reason)

            else:
                # don't do success level checks and just output a dice roll number
                total, tens, units = dice.dg.d100()
                # await message.channel.send(f"{tens} + {units} = {total}")
                embed = build_dg_roll_embed(total, tens, units, reason=reason)

            return embed
        
        except dice.DiceError as error:
            return error.message


    elif "help" in message:
        return {'title': "Dice Roll Usage:", 'description': dg_help_message}

    else:
        return {'title': "", 'description': dg_mini_help_message}


def build_dg_roll_embed(total, tens, units, success_level=None, reason=None):
   
    if success_level is not None:
        if success_level == dice.dg.SuccessLevel.CRITICAL_SUCCESS:
            title = "Critical Success!"
            color = C_CRITICAL_SUCCESS
        elif success_level == dice.dg.SuccessLevel.REGULAR_SUCCESS:
            title = "Success"
            color = C_SUCCESS
        elif success_level == dice.dg.SuccessLevel.FAILURE:
            title = "Failure"
            color = C_FAILURE
        elif success_level == dice.dg.SuccessLevel.FUMBLE:
            title = "Fumble!"
            color = C_FAILURE_DISADV
    else:
        title = f"{total}"
        color = 0x202225

    description = f"**{total - units}** + **{units}** = **{total}**"
    if reason:
        description += f"\n**Reason**: {reason}"
    
    # embed = discord.Embed(title=title, description=description, color=color)
    # embed.set_footer(text=footer)
    # return embed
    return {'title': title, 'description': description, 'color': color}
