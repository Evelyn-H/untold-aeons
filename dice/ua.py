from .core import *

def roll_one():
    conversion_map = {
        6: (2, 0),
        5: (1, 0),
        4: (0, 0),
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


# if __name__ == "__main__":
#     from dice import *

#     skill, difficulty = map(int, input(">> ").split(" "))
#     print(skill, difficulty)

#     for _ in range(10):
#         print(ua.roll(skill, difficulty))

#     n = 10000
#     l = [ua.roll(skill, difficulty) for _ in range(n)]
#     p_success = 1 / n * sum(map(lambda x: x[0] >= 1, l))
#     e_success = 1 / n * sum(map(lambda x: x[0], l))
#     print(f"p_success: {p_success},  e_success: {e_success}")
#     p_adv = 1 / n * sum(map(lambda x: x[1] >= 1, l))
#     p_disadv = 1 / n * sum(map(lambda x: x[1] <= -1, l))
#     p_none = 1 / n * sum(map(lambda x: x[1] == 0, l))
#     e_adv = 1 / n * sum(map(lambda x: x[1], l))
#     print(f"p_adv: {p_adv},  p_disadv: {p_disadv},  p_none: {p_none},  e_adv: {e_adv}")

#     p_success_with_adv = 1 / n * sum(map(lambda x: x[0] >= 1 and x[1] >= 1, l))
#     p_success_with_none = 1 / n * sum(map(lambda x: x[0] >= 1 and x[1] == 0, l))
#     p_success_with_disadv = 1 / n * sum(map(lambda x: x[0] >= 1 and x[1] <= -1, l))
#     p_failure_with_adv = 1 / n * sum(map(lambda x: x[0] <= 0 and x[1] >= 1, l))
#     p_failure_with_none = 1 / n * sum(map(lambda x: x[0] <= 0 and x[1] == 0, l))
#     p_failure_with_disadv = 1 / n * sum(map(lambda x: x[0] <= 0 and x[1] <= -1, l))
#     print(
#         "success:",
#         round(p_success_with_adv, 2),
#         round(p_success_with_none, 2),
#         round(p_success_with_disadv, 2),
#         "  failure:",
#         round(p_failure_with_adv, 2),
#         round(p_failure_with_none, 2),
#         round(p_failure_with_disadv, 2)
#     )
