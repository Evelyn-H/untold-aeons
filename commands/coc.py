import re
import dice
from .colors import *


coc_mini_help_message = """\
Use `!coc <skill value> <modifiers>` for skill rolls (modifiers are optional)
E.g.: `!coc 70`, `!coc 20+`, `!coc 30-`

(Use `!coc help` for more details)
"""

coc_help_message = """\
`!coc <modifiers>`: a d100 roll with optional bonus / penalty dice
`!coc <skill value> <modifiers>`: a skill check with the given skill value and optional bonus / penalty dice
(alternatively, you can also use `!croll`, and `!cocroll` instead of `!coc`)

Additionally, you can specify a reason for the roll as follows:
`!coc <skill value> <modifiers> !<reason>`

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
    `!coc 70 !listen`: skill check with a skill of 70, with the reason "listen" 
"""
    
# CoC Dice roll
def roll(message):
    match = re.match(r"^\s*(?P<skill>\d*)\s*(?P<modifiers>(?:t|bonus|b|\+|penalty|p|-|\s+)*)(?:!\s*(?P<reason>.*))?$", message)
    if match:
        print(match.group('skill'), "---", match.group('modifiers'))
        # this is kinda janky, but if you just count 'b', 'p', '+', and '-'
        # and ignore other letters it'll work, cause 'bonus' and 'penalty' only contain a single of those letters each
        positive_modifiers = match.group('modifiers').count('b') + match.group('modifiers').count('+')
        negative_modifiers = match.group('modifiers').count('p') + match.group('modifiers').count('-')
        total_modifiers = positive_modifiers - negative_modifiers

        reason = match.group('reason')

        try:
            # see if a skill value was given or not
            if match.group('skill'):
                # roll and also check what type of success it was
                skill = int(match.group('skill'))
                total, tens, units, success_level = dice.coc.roll(skill, total_modifiers)
                # await message.channel.send(f"{success_level.__class__.__repr__(success_level)},  {tens} + {units} = {total}")
                embed = build_coc_roll_embed(total, tens, units, success_level, reason=reason)

            else:
                # don't do success level checks and just output a dice roll number
                total, tens, units = dice.coc.d100(total_modifiers)
                # await message.channel.send(f"{tens} + {units} = {total}")
                embed = build_coc_roll_embed(total, tens, units, reason=reason)

            return embed
        
        except dice.DiceError as error:
            return error.message


    elif "help" in message:
        return {'title': "Dice Roll Usage:", 'description': coc_help_message}

    else:
        return {'title': "", 'description': coc_mini_help_message}


def build_coc_roll_embed(total, tens, units, success_level=None, reason=None):
   
    if success_level is not None:
        if success_level == dice.coc.SuccessLevel.CRITICAL_SUCCESS:
            title = "Critical Success!"
            color = C_CRITICAL_SUCCESS
        elif success_level == dice.coc.SuccessLevel.EXTREME_SUCCESS:
            title = "Extreme Success!"
            color = C_SUCCESS_ADV
        elif success_level == dice.coc.SuccessLevel.HARD_SUCCESS:
            title = "Hard Success!"
            color = C_HARD_SUCCESS
        elif success_level == dice.coc.SuccessLevel.REGULAR_SUCCESS:
            title = "Success"
            color = C_SUCCESS
        elif success_level == dice.coc.SuccessLevel.FAILURE:
            title = "Failure"
            color = C_FAILURE
        elif success_level == dice.coc.SuccessLevel.FUMBLE:
            title = "Fumble!"
            color = C_FAILURE_DISADV
    else:
        title = f"{total}"
        color = 0x202225

    description = f"**{total - units}**{' '+str(tens) if len(tens) > 1 else ''} + **{units}** = **{total}**"
    if reason:
        description += f"\n**Reason**: {reason}"
    
    # embed = discord.Embed(title=title, description=description, color=color)
    # embed.set_footer(text=footer)
    # return embed
    return {'title': title, 'description': description, 'color': color}
