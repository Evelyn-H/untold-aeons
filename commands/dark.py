import re
import dice
from .colors import *

# Cthulhu Dark Dice roll
def roll(message):
    dice_pattern = r"(white|w|green|g|red|r|yellow|y|blue|b|human|h|occupation|o|insight|insanity|i|failure|f|\s+)"
    match = re.match(r"^\s*(?P<dice>" + dice_pattern + r"*)(?:!\s*(?P<reason>.*))?$", message)
    match_insight = re.match(r"^\s*(?P<insight>\d)\s*(?:!\s*(?P<reason>.*))?$", message)
    
    if match_insight:
        target = int(match_insight.group('insight'))
        roll = dice.d(6)
        print(roll)
        if roll > target:
            if target == 5:
                title = "You understand... *everything*"
                description = "You understand the full horror behind the Universe and leave everyday life behind."
            else:
                title = "Increase Insight by one"
                description = f"You rolled a {roll}"
        else:
            title = "No change"
            description = f"You rolled a {roll}"
        color = 0x9947eb

        return {'title': title, 'description': description, 'color': color}


    elif match and match.group('dice') and len(message.strip()) > 0:
        split = list(filter(None, re.split(dice_pattern, match.group('dice'))))
        print(split)

        #for brevity
        def count(data, l):
            return sum([data.count(s) for s in l])

        white_n = count(split, ['white', 'w', 'human', 'h', 'occupation', 'o'])
        green_n = count(split, ['green', 'g', 'insight', 'insanity', 'i'])
        red_n = count(split, ['red', 'r', 'failure', 'f'])
        yellow_n = count(split, ['yellow', 'y'])
        blue_n = count(split, ['blue', 'b'])

        try:
            # don't do success level checks and just output a dice roll number
            white_d6 = dice.d(6, times=white_n, total=False)
            green_d6 = dice.d(6, times=green_n, total=False)
            red_d6 = dice.d(6, times=red_n, total=False)
            yellow_d6 = dice.d(6, times=yellow_n, total=False)
            blue_d6 = dice.d(6, times=blue_n, total=False)

            if white_n > 20 or green_n > 20 or red_n > 20 or yellow_n > 20 or blue_n > 20:
                raise dice.DiceError("Azathoth curses you for using too many dice!")

            # Interpretation
            # quick helper function
            def highest(l):
                return max(l) if len(l) > 0 else 0

            if yellow_n > 0 or blue_n > 0:
                title = "Custom"
                color = 0x202225
            
            elif highest(red_d6) > highest(white_d6 + green_d6):
                title = "Failure!"
                color = C_FAILURE_DISADV

            else:
                title, color = {
                    6: ("More than you wanted!", C_CRITICAL_SUCCESS),
                    5: ("Success, and...", C_SUCCESS_ADV),
                    4: ("Success", C_SUCCESS),
                    3: ("Partial Success", C_SUCCESS_DISADV),
                    2: ("Partial Success, but...", C_FAILURE_ADV),
                    1: ("*Juuuust* Barely", C_FAILURE),
                }[highest(white_d6 + green_d6)]

            def format_dice_list(l):
                if len(l) == 0:
                    return ""
                elif len(l) == 1:
                    return f"**{l[0]}**"
                else:
                    return f"**{l[0]}**, {', '.join(map(str, l[1:]))}"

            description =  ""
            if white_n > 0:
                description += f":white_circle: {format_dice_list(sorted(white_d6, reverse=True))}\n"
            if green_n > 0:
                description += f":green_circle: {format_dice_list(sorted(green_d6, reverse=True))}\n"
            if red_n > 0:
                description += f":red_circle: {format_dice_list(sorted(red_d6, reverse=True))}\n"
            if yellow_n > 0 or blue_n > 0:
                description += "\n"
            if yellow_n > 0:
                description += f":yellow_circle: {format_dice_list(sorted(yellow_d6, reverse=True))}\n"
            if blue_n > 0:
                description += f":blue_circle: {format_dice_list(sorted(blue_d6, reverse=True))}\n"

            if highest(green_d6) > highest(white_d6):
                description += f"\n**!Please make an Insight Roll!**\n"


            if match.group('reason'):
                description += f"\n**Reason**: {match.group('reason')}"
        
            return {'title': title, 'description': description, 'color': color}
        
        except dice.DiceError as error:
            return error.message


    else:
        return "Incorrect syntax"
