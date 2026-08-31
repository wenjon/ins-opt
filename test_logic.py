import random
def seeded_random(seed):
    if not seed:
        return random.random
    s = int(seed)
    def rng():
        nonlocal s
        s = (s * 9301 + 49297) % 233280
        return s / 233280
    return rng
def shuffle(arr, rng):
    a = list(arr)
    for i in range(len(a)-1, 0, -1):
        j = int(rng() * (i + 1))
        a[i], a[j] = a[j], a[i]
    return a
rng = seeded_random(None)
print("no-seed type:", type(rng).__name__)
out = shuffle(["a","b","c","d","e"], rng)
print("no-seed result:", out)
rng2 = seeded_random("12345")
out2 = shuffle(["a","b","c","d","e"], rng2)
print("seeded result:", out2)