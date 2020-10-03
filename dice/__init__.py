import random

from .core import *
from . import ua
from . import coc

if __name__ == "__main__":
    skill, difficulty = map(int, input(">> ").split(" "))
    print(skill, difficulty)

    for _ in range(10):
        print(ua.roll(skill, difficulty))

    n = 10000
    l = [ua.roll(skill, difficulty) for _ in range(n)]
    p_success = 1 / n * sum(map(lambda x: x[0] >= 1, l))
    e_success = 1 / n * sum(map(lambda x: x[0], l))
    print(f"p_success: {p_success},  e_success: {e_success}")
    p_adv = 1 / n * sum(map(lambda x: x[1] >= 1, l))
    p_disadv = 1 / n * sum(map(lambda x: x[1] <= -1, l))
    p_none = 1 / n * sum(map(lambda x: x[1] == 0, l))
    e_adv = 1 / n * sum(map(lambda x: x[1], l))
    print(f"p_adv: {p_adv},  p_disadv: {p_disadv},  p_none: {p_none},  e_adv: {e_adv}")

    p_success_with_adv = 1 / n * sum(map(lambda x: x[0] >= 1 and x[1] >= 1, l))
    p_success_with_none = 1 / n * sum(map(lambda x: x[0] >= 1 and x[1] == 0, l))
    p_success_with_disadv = 1 / n * sum(map(lambda x: x[0] >= 1 and x[1] <= -1, l))
    p_failure_with_adv = 1 / n * sum(map(lambda x: x[0] <= 0 and x[1] >= 1, l))
    p_failure_with_none = 1 / n * sum(map(lambda x: x[0] <= 0 and x[1] == 0, l))
    p_failure_with_disadv = 1 / n * sum(map(lambda x: x[0] <= 0 and x[1] <= -1, l))
    print(
        "success:",
        round(p_success_with_adv, 2),
        round(p_success_with_none, 2),
        round(p_success_with_disadv, 2),
        "  failure:",
        round(p_failure_with_adv, 2),
        round(p_failure_with_none, 2),
        round(p_failure_with_disadv, 2)
    )
