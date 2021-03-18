import enum
import math

from dice import *

import re
import dice
from .colors import *


mini_help_message = """\
Use `!improve <skill value> <skill name>` for skill rolls (modifiers are optional)
E.g.: `!improve 90 spot hidden`, `!improve 20`
"""

# Improvement rolls:
#   - 1d100 for each skill, improve skill if roll >95 or >skill level
#   - to improve: add 1d10 to the skill
#     - gain 2d6 sanity when skill goes >=90
    
# Mothership Dice roll
def improvement(message):
    match = re.match(r"^\s*(?P<skill>\d+)\s*(?:!?\s*(?P<reason>.*))?$", message)
    if match:
        skill = int(match.group('skill'))
        reason = match.group('reason') or ""

        try:
            total, tens, units = dice.coc.d100()

            # skill_desc = f"\"{reason}\" with value of {skill}" if reason else f"{skill}"
            # description = f"Improving {skill_desc}:\n\n"
            title = f"Improving: {reason}" if reason else None
            description = ""
            color = None
            if total > skill or total > 95:
                description += f"**Improvement succeeded!** *(rolled {total})*\n"
                color = C_CRITICAL_SUCCESS
                increase = dice.d(10)
                new_skill = skill + increase
                description += f"New skill value: **{new_skill}** *(increased by {increase})*\n"

                # check for sanity gain
                if new_skill >= 90 and skill < 90:
                    sanity_gain = dice.d(6, times=2)
                    description += f"\nYou also **gained {sanity_gain} sanity** from increasing your skill beyond 90%!"
            
            else:
                description += f"**Improvement failed** *({total})*\n"
                color = C_FAILURE

            return {'title': title, 'description': description, 'color': color}

        except dice.DiceError as error:
            return error.message

    else:
        return {'title': "Improvement Command Usage:", 'description': mini_help_message}
