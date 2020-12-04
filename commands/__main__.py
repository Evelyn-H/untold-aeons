from . import npc

n = 10000

counts = [0] * 5

for _ in range(n):
    d = npc.roll_stats("")
    if "*well* below average" in d['description']:
        counts[0] += 1
    elif "below average" in d['description']:
        counts[1] += 1
    elif "*well* above average" in d['description']:
        counts[4] += 1
    elif "above average" in d['description']:
        counts[3] += 1
    else:
        counts[2] += 1

print([round(c/n*100,1) for c in counts])
