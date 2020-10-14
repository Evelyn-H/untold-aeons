import re
import dice
from .colors import *

def format_plural(n, singular, plural):
        return (singular if abs(n) == 1 else plural)

    
# UA dice roll
def roll(message):
    # skill, difficulty = map(int, filter(None, map(str.strip, message.split(" "))))
    match = re.match(r"^\s*(?P<skill>\-?\d+)\s*(?P<difficulty>\d+)?\s*(?:!\s*(?P<reason>.*))?$", message)
    
    if not match:
        return "Incorrect syntax"

    # regular opposed-type roll
    if match.group('skill') and match.group('difficulty'):
        skill = int(match.group('skill'))
        difficulty = int(match.group('difficulty'))

        try:
            success, failure, adv, disadv = dice.ua.roll(skill, difficulty, cancel_totals=False)
        except dice.DiceError as error:
            return error.message
    
        return build_ua_roll_embed(success, failure, adv, disadv, match.group('reason'))

    # unopposed roll
    elif match.group('skill'):
        skill = int(match.group('skill'))

        if skill == 0:
            return "Skill can't be 0."

        try:
            success, adv = dice.ua.roll_multiple(abs(skill))
        except dice.DiceError as error:
            return error.message

        success_failure = format_plural(success, "success", "successes") if skill > 0 else format_plural(success, "failure", "failures")
        adv_disadv = format_plural(adv, "advantage", "advantages") if skill > 0 else format_plural(adv, "drawback", "drawbacks")
        title = f"**{success}** {success_failure}, **{adv}** {adv_disadv}"
        color = 0x202225
        if match.group('reason'):
            description = f"\n\n**Reason**: {match.group('reason')}"
        else:
            description = ""

        return {'title': title, 'description': description, 'color': color}


def build_ua_roll_embed(success, failure, adv, disadv, reason=None):
    total_success = success - failure
    total_adv = adv - disadv
    if total_success > 0 and total_adv > 0:
        title = "Success with Advantage"
        color = C_SUCCESS_ADV
    elif total_success > 0 and total_adv == 0:
        title = "Success"
        color = C_SUCCESS
    elif total_success > 0 and total_adv < 0:
        title = "Success with Drawback"
        color = C_SUCCESS_DISADV
    elif total_success <= 0 and total_adv > 0:
        title = "Failure with Advantage"
        color = C_FAILURE_ADV
    elif total_success <= 0 and total_adv == 0:
        title = "Failure"
        color = C_FAILURE
    elif total_success <= 0 and total_adv < 0:
        title = "Failure with Drawback"
        color = C_FAILURE_DISADV

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

    if reason:
        description += f"\n\n**Reason**: {reason}"

    return {'title': title, 'description': description, 'color': color}
