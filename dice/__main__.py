# from . import core

# def roll_OMT(d4=False, d8=False, d12=False, d6=False, d10=False, d20=False):
#     rolls = [
#         core.d(4) if d4 else 0,
#         core.d(8) if d8 else 0,
#         core.d(12) if d12 else 0,
#         core.d(6) if d6 else 0,
#         core.d(10) if d10 else 0,
#         core.d(20) if d20 else 0,
#     ]
#     # return rolls
#     best = max(rolls)
#     if best < 4:
#         return 0
#     else:
#         return (best-4)//2 + 1

# i = input(">> ")

# r = roll_OMT('6' in i, '10' in i, '20' in i)
# # print(r)


# def calc_averages(d4=False, d8=False, d12=False, d6=False, d10=False, d20=False):
#     n = 1000000
#     counts = [0] * 10
#     for _ in range(n):
#         r = roll_OMT(d4, d8, d12, d6, d10, d20)
#         counts[r] += 1
#     percentages = [round(c/n*100, 1) for c in counts]

#     print(
#         ('[ ' + ('d6 ' if d6 else '') + ('d10 ' if d10 else '') + ('d20 ' if d20 else '') + ']').ljust(16), 
#         ',  '.join([str(i) + ': ' + str(p).rjust(4) for i, p in enumerate(percentages)])
#     )
#     return percentages

# for i in range(3):
#     print('d' + str(i*4+4), ':')
#     if i == 0:
#         args = (1, 0, 0)
#     elif i == 1:
#         args = (0, 1, 0)
#     elif i == 2:
#         args = (0, 0, 1)

#     calc_averages(*args, 0, 0, 0)
#     calc_averages(*args, 1, 0, 0)
#     calc_averages(*args, 0, 1, 0)
#     calc_averages(*args, 0, 0, 1)
#     calc_averages(*args, 1, 1, 0)
#     calc_averages(*args, 0, 1, 1)
#     calc_averages(*args, 1, 0, 1)
#     calc_averages(*args, 1, 1, 1)
#     print()

# calc_averages(0, 0, 0)
# calc_averages(1, 0, 0)
# calc_averages(0, 1, 0)
# calc_averages(0, 0, 1)
# calc_averages(1, 1, 0)
# calc_averages(0, 1, 1)
# calc_averages(1, 0, 1)
# calc_averages(1, 1, 1)




from . import ua

# skill, difficulty = map(int, input(">> ").split(" "))
# # print(skill, difficulty)

# # for _ in range(10):
# #     print(ua.roll(skill, difficulty))

# n = 100000
# l = [ua.roll(skill, difficulty, cancel_totals=False) for _ in range(n)]


# base_damage = 5
# def damage(roll):
#     success, failure, adv, disadv = roll

#     # hit
#     if success > failure:
#         # crit
#         if adv > disadv:
#             return base_damage * 2 + success
#         # regular
#         else:
#             return base_damage + success

#     # miss
#     else:
#         return 0


# import collections

# d = map(damage, l)
# c = collections.Counter(d)
# data = sorted(c.items(), key=lambda i: i[0])
# for val, count in data:
#     print(f"{val}:\t{round(count/n*100, 1)}")


skill, difficulty = map(int, input(">> ").split(" "))
# print(skill, difficulty)

# for _ in range(10):
#     print(ua.roll(skill, difficulty))

n = 100000
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

p_all_blank = 1 / n * sum(map(lambda x: x[0] == 0 and x[1] == 0, l))

print(
    "success:",
    round(p_success_with_adv, 2),
    round(p_success_with_none, 2),
    round(p_success_with_disadv, 2),
    "  failure:",
    round(p_failure_with_adv, 2),
    round(p_failure_with_none, 2),
    round(p_failure_with_disadv, 2),
    "\nnothing:", round(p_all_blank, 2)
)
