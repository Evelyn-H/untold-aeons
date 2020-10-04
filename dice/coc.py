import enum
import math

from .core import *


class SuccessLevel(enum.IntEnum):
    FUMBLE = 0
    FAILURE = 1
    REGULAR_SUCCESS = 2
    HARD_SUCCESS = 3
    EXTREME_SUCCESS = 4
    CRITICAL_SUCCESS = 5

def d100(modifiers=0):
    """
    modifiers > 0: bonus dice
    modifiers = 0: regular roll
    modifiers < 0: penalty dice
    """
    units = d(10)

    tens = [
        10 * (d(10) - 1)  # the -1 ensures that it's in the range [0-9] instead of  [1-10]
        for _ in range(abs(modifiers) + 1)  # always need one extra dice per modifier
    ]
    
    if modifiers >= 0:
        total = units + min(tens)
    else:
        total = units + max(tens)

    return total, tens, units

def roll(skill, modifiers=0):
    if skill < 1:
        raise DiceError("Skill is too low, I know you can do better than that!")
    if skill > 500:
        raise DiceError("Skill is too high. No one is *that* good, not even you.")
    if abs(modifiers) > 20:
        raise DiceError("If you need that many bonus / penalty dice I think something has gone horribly wrong (or right)...")

    total, tens, units = d100(modifiers)

    fumble_threshold = 100 if skill >= 50 else 96

    if total == 1:
        success_level = SuccessLevel.CRITICAL_SUCCESS
    elif total >= fumble_threshold:
        success_level = SuccessLevel.FUMBLE
    elif total <= math.floor(skill / 5):
        success_level = SuccessLevel.EXTREME_SUCCESS
    elif total <= math.floor(skill / 2):
        success_level = SuccessLevel.HARD_SUCCESS
    elif total <= skill:
        success_level = SuccessLevel.REGULAR_SUCCESS
    else:
        success_level = SuccessLevel.FAILURE

    return total, tens, units, success_level

if __name__ == "__main__":
    skill, modifiers = map(int, input(">> ").split(" "))
    print(skill, modifiers)

    for _ in range(10):
        print(roll(skill, modifiers))

    n = 10000
    l = [roll(skill, modifiers) for _ in range(n)]

    p_critical_success = 1 / n * sum(map(lambda x: x[3] >= SuccessLevel.CRITICAL_SUCCESS, l))
    p_extreme_success = 1 / n * sum(map(lambda x: x[3] >= SuccessLevel.EXTREME_SUCCESS, l))
    p_hard_success = 1 / n * sum(map(lambda x: x[3] >= SuccessLevel.HARD_SUCCESS, l))
    p_regular_success = 1 / n * sum(map(lambda x: x[3] >= SuccessLevel.REGULAR_SUCCESS, l))
    p_failure = 1 / n * sum(map(lambda x: x[3] <= SuccessLevel.FAILURE, l))
    p_fumble = 1 / n * sum(map(lambda x: x[3] <= SuccessLevel.FUMBLE, l))

    print(
        f"p_critical_success: {round(p_critical_success, 2)}",
        f"p_extreme_success: {round(p_extreme_success, 2)}",
        f"p_hard_success: {round(p_hard_success, 2)}",
        f"p_regular_success: {round(p_regular_success, 2)}",
        f"p_failure: {round(p_failure, 2)}",
        f"p_fumble: {round(p_fumble, 2)}",
        sep='\n'
    )
