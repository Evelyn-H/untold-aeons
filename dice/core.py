import random

class DiceError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

def d(n, times=1, total=True):
    if n < 2:
        raise DiceError("Please only use dice with at least two faces")
    if n > 200:
        raise DiceError("Please only use dice with at most 200 faces")
    if times < 0:
        raise DiceError("Sadly I can't roll a negative amount of dice without waking Azathoth")
    if times > 500:
        raise DiceError("Please don't roll more than 500 dice at once")

    l = [random.randint(1, n) for _ in range(times)]
    if total:
        return sum(l)
    else:
        return l
