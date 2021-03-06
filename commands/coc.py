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

def roll_multiple(message):
    roll_match = r"(?P<skill>\d+)\s*(?P<modifiers>(?:t|bonus|b|\+|penalty|p|-|\s+)*)"
    match = re.match(r"^\s*(?P<rolls>(" + roll_match + r"\s*,?\s*)*)(?:!\s*(?P<reason>.*))?$", message)
    print(match)
    if match:
        reason = match.group('reason')
        rolls = []
        print(match.group('rolls'))
        for roll in re.finditer(roll_match, match.group('rolls')):
            print(roll)
            print(roll.group('skill'), "---", roll.group('modifiers'))
            skill = int(roll.group('skill'))
            # this is kinda janky, but if you just count 'b', 'p', '+', and '-'
            # and ignore other letters it'll work, cause 'bonus' and 'penalty' only contain a single of those letters each
            positive_modifiers = roll.group('modifiers').count('b') + roll.group('modifiers').count('+')
            negative_modifiers = roll.group('modifiers').count('p') + roll.group('modifiers').count('-')
            total_modifiers = positive_modifiers - negative_modifiers
            rolls.append({
                'skill': skill,
                'total_modifiers': total_modifiers
            })
        print(rolls)

        if len(rolls) < 2:
            return "Please only use this command if you want to do multiple checks at once!"

        try:
            description = ""
            for roll in rolls:
                total, tens, units, success_level = dice.coc.roll(roll['skill'], roll['total_modifiers'])
                name, _ = success_level_str(success_level)
                roll_string = f"**{total - units}**{' '+str(tens) if len(tens) > 1 else ''} + **{units}** = **{total}**"
                description += f"{roll['skill']}: **{name}** *({total})*\n"
            description += "\n"
            if reason:
                description += f"**Reason**: {reason}"
            
            # return {'title': title, 'description': description, 'color': color}
            return {'title': "Multiple Rolls", 'description': description}
        
        except dice.DiceError as error:
            return error.message

    
# CoC Dice roll
def roll(message):
    match = re.match(r"^\s*(?P<skill>(?:\d*\s*,?\s*)*)\s*(?P<modifiers>(?:t|bonus|b|\+|penalty|p|-|\s+)*)(?:!\s*(?P<reason>.*))?$", message)
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
                # print(match.group('skill'), match.group('skill').split(","))
                # skill_list = [int(s) for s in match.group('skill').split(",") if s]
                skill_list = [int(s) for s in re.split(r",|\s+", match.group('skill')) if s]
                print(skill_list)
                if len(skill_list) == 1:
                    skill = min(skill_list)  #int(match.group('skill'))
                    total, tens, units, success_level = dice.coc.roll(skill, total_modifiers)
                    # await message.channel.send(f"{success_level.__class__.__repr__(success_level)},  {tens} + {units} = {total}")
                    embed = build_coc_roll_embed(total, tens, units, success_level, reason=reason)
                else:
                    dice_roll = dice.coc.d100(total_modifiers)
                    # skill_list.sort()
                    results = [(skill, dice.coc.roll(skill, total_modifiers, force_value=dice_roll)) for skill in skill_list]
                    print(results)
                    total, tens, units, success_level = sorted(results, key=lambda d: d[0])[0][1]
                    print(sorted(results, key=lambda d: d[0]))
                    # other_results = results[1:]
                    other_results = results[:]
                    embed = build_coc_roll_embed(total, tens, units, success_level, reason=reason, secondary_rolls=other_results)


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


def success_level_str(success_level):
    if success_level == dice.coc.SuccessLevel.CRITICAL_SUCCESS:
        return ("Critical Success!", C_CRITICAL_SUCCESS)
    elif success_level == dice.coc.SuccessLevel.EXTREME_SUCCESS:
        return ("Extreme Success!", C_SUCCESS_ADV)
    elif success_level == dice.coc.SuccessLevel.HARD_SUCCESS:
        return ("Hard Success!", C_HARD_SUCCESS)
    elif success_level == dice.coc.SuccessLevel.REGULAR_SUCCESS:
        return ("Success", C_SUCCESS)
    elif success_level == dice.coc.SuccessLevel.FAILURE:
        return ("Failure", C_FAILURE)
    elif success_level == dice.coc.SuccessLevel.FUMBLE:
        return ("Fumble!", C_FAILURE_DISADV)

def build_coc_roll_embed(total, tens, units, success_level=None, reason=None, secondary_rolls=None):
   
    if success_level is not None:
        title, color = success_level_str(success_level)
        # if success_level == dice.coc.SuccessLevel.CRITICAL_SUCCESS:
        #     title = "Critical Success!"
        #     color = C_CRITICAL_SUCCESS
        # elif success_level == dice.coc.SuccessLevel.EXTREME_SUCCESS:
        #     title = "Extreme Success!"
        #     color = C_SUCCESS_ADV
        # elif success_level == dice.coc.SuccessLevel.HARD_SUCCESS:
        #     title = "Hard Success!"
        #     color = C_HARD_SUCCESS
        # elif success_level == dice.coc.SuccessLevel.REGULAR_SUCCESS:
        #     title = "Success"
        #     color = C_SUCCESS
        # elif success_level == dice.coc.SuccessLevel.FAILURE:
        #     title = "Failure"
        #     color = C_FAILURE
        # elif success_level == dice.coc.SuccessLevel.FUMBLE:
        #     title = "Fumble!"
        #     color = C_FAILURE_DISADV
    else:
        title = f"{total}"
        color = 0x202225

    description = f"**{total - units}**{' '+str(tens) if len(tens) > 1 else ''} + **{units}** = **{total}**"
    if secondary_rolls:
        description += "\n"
        for skill, values in secondary_rolls:
            total, tens, units, success_level = values
            name, _ = success_level_str(success_level)
            description += f"\n{skill}: **{name}**"
        description += "\n"
    if reason:
        description += f"\n**Reason**: {reason}"
    
    # embed = discord.Embed(title=title, description=description, color=color)
    # embed.set_footer(text=footer)
    # return embed
    return {'title': title, 'description': description, 'color': color}
