import dice
import npc

# NPG generation
def generate_npc(message):
    character = npc.Character()
    return character.generate_embed()

    # n = 10000
    # d = {}
    # for _ in range(n):
    #     c = npc.Character()
    #     d[c.occupation.name] = d.get(c.occupation.name, 0) + 1

    # print(d)


def generate_name(message):
    try:
        amount = min(20, max(1, int(message.strip())))
    except Exception as error:
        amount = 1

    gender = None
    if message.strip() in ["female","woman"]:
        gender = "female"

    if message.strip() in ["male","man"]:
        gender = "male"

    names = [npc.Character.generate_name(gender=gender) for _ in range(amount)]
    if amount > 1:
        return {'title': "Random Names", 'description': "\n".join(names)}
    else:
        return {'title': f"{names[0]}"}


def roll_stats(message):
    # rolling PC stats
    low_stats = [dice.d(6, 3) * 5 for _ in range(5)]
    high_stats = [(dice.d(6, 2) + 6) * 5 for _ in range(3)]

    total = sum(low_stats) + sum(high_stats)
    expected_total = 91.5  # expected "average"
    std_dev = 16.5 #ish

    print(total / 5)

    if expected_total - std_dev * 0.5 < total / 5 < expected_total + std_dev * 0.5:
        averageness = None
    elif expected_total - std_dev * 1.0 < total / 5 < expected_total - std_dev * 0.5:
        averageness = "below average"
    elif total / 5 < expected_total - std_dev * 1.0:
        averageness = "*well* below average"
    elif expected_total + std_dev * 0.5 < total / 5 < expected_total + std_dev * 1.0:
        averageness = "above average"
    elif expected_total + std_dev * 1.0 < total / 5:
        averageness = "*well* above average"

    title = "Random PC stats"
    description =  f"3d6 x 5: **{low_stats}**\n"
    description += f"2d6+6 x 5: **{high_stats}**\n"
    description += f"Luck: **{dice.d(6, 3) * 5}**\n"
    description += f"\nThese rolls are {averageness}.\n\n" if averageness is not None else "\n"
    description += f"Use the first set of numbers for STR, DEX, CON, APP, and POW.\nUse the second set for SIZ, INT, and EDU."

    return {'title': title, 'description': description}
