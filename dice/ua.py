from .core import *

def roll_one():
    conversion_map = {
        6: (2, 0),
        5: (1, 0),
        4: (1, 0),
        3: (0, 0),
        2: (0, 0),
        1: (0, 1)
    }
    return conversion_map[d(6)]

def roll_multiple(n):
    if n < 0:
        raise DiceError("Sadly I can't roll a negative amount of dice without waking Azathoth")
    if n > 500:
        raise DiceError("Please don't roll more than 500 dice at once")

    l = [roll_one() for _ in range(n)]
    return tuple([sum(x) for x in zip(*l)])

def roll(skill, difficulty, cancel_totals=True):
    if skill > 0:
        success, adv = roll_multiple(skill)
    elif skill == 0:
        success = roll_one()[0] // 2
        adv = 0
    else:
        success, adv = 0, 0

    failure, disadv = roll_multiple(difficulty) if difficulty > 0 else (0, 0)
    if cancel_totals:
        return (success - failure, adv - disadv)
    else: 
        return (success, failure, adv, disadv)
