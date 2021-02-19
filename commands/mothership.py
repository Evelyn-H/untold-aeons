import enum
import math

from dice import *

import re
import dice
from .colors import *


ms_mini_help_message = """\
Use `!ms <skill value> <modifiers>` for skill rolls (modifiers are optional)
E.g.: `!ms 70`, `!ms 45+`, `!ms 30-`
"""
    
# Mothership Dice roll
def roll_command(message):
    match = re.match(r"^\s*(?P<skill>\d+)\s*(?P<modifiers>(?:[+-]\s*)*)(?:!\s*(?P<reason>.*))?$", message)
    if match:
        skill = int(match.group('skill'))
        positive_modifiers = match.group('modifiers').count('+')
        negative_modifiers = match.group('modifiers').count('-')
        total_modifiers = positive_modifiers - negative_modifiers

        reason = match.group('reason')

        try:
            total, tens, units, success_level, results = roll(skill, total_modifiers)
            embed = build_ms_roll_embed(total, tens, units, success_level, results, reason=reason)
            return embed

        except dice.DiceError as error:
            return error.message

    else:
        return {'title': "Mothership Dice Roll Usage:", 'description': ms_mini_help_message}

def build_ms_roll_embed(total, tens, units, success_level, results, reason=None):
   
    if success_level == SuccessLevel.CRITICAL_SUCCESS:
        title = "Critical Success!"
        color = C_CRITICAL_SUCCESS
    elif success_level == SuccessLevel.SUCCESS:
        title = "Success"
        color = C_SUCCESS
    elif success_level == SuccessLevel.FAILURE:
        title = "Failure"
        color = C_FAILURE
    elif success_level == SuccessLevel.CRITICAL_FAILURE:
        title = "Critical Failure!"
        color = C_FAILURE_DISADV

    description = f"**{total - units}** + **{units}** = **{total}** {' '+str(results) if len(results) > 1 else ''}"
    # description = f"**{total}**{' '+str(results) if len(results) > 1 else ''}"
    
    if reason:
        description += f"\n**Reason**: {reason}"
    
    return {'title': title, 'description': description, 'color': color}



class SuccessLevel(enum.IntEnum):
    CRITICAL_FAILURE = 0
    FAILURE = 1
    SUCCESS = 2
    CRITICAL_SUCCESS = 5

# d100 in mothership is 0-99 instead of 1-100 like in CoC or DG
def d100():
    units = d(10) - 1
    tens = 10 * (d(10) - 1)  # the -1 ensures that it's in the range [0-9] instead of  [1-10]
    return tens + units, tens, units

def get_success_level(skill, total, tens, units):
    is_double = tens/10 == units
    is_success = total < skill # as far as I can tell Mothership uses < instead of <= for skill checks

    success_level = None
    # crits
    if total == 0 or (is_success and is_double):
        success_level = SuccessLevel.CRITICAL_SUCCESS
    elif total == 99 or (not is_success and is_double):
        success_level = SuccessLevel.CRITICAL_FAILURE
    # regular
    elif is_success:
        success_level = SuccessLevel.SUCCESS
    else:
        success_level = SuccessLevel.FAILURE

    return success_level

def roll(skill, modifiers=0):
    if skill < 1:
        raise DiceError("Skill is too low, I know you can do better than that!")
    if skill > 200:
        raise DiceError("Skill is too high. No one is *that* good, not even you.")
    if abs(modifiers) > 20:
        raise DiceError("Modifier is too high (or low).")

    results = [d100() for _ in range(abs(modifiers) + 1)]
    # add success level to the tuple
    results = [(get_success_level(skill, *r), *r) for r in results]

    if modifiers >= 0:
        best = max(results)
    else:
        best = min(results)

    success_level, total, tens, units = best

    # success_level = get_success_level(skill, total, tens, units)

    return total, tens, units, success_level, [r[1] for r in results]

if __name__ == "__main__":
    for _ in range(10):
        print(roll(40, -1))
