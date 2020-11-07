import re
import dice

help_message = """\
Not written yet.
"""

#TODO: make this less janky
original_rolls = []

#TODO: add !reason functionality


# Custom Dice roll
def roll(message):
    match = re.match(r"^\s*(?P<dice_expr>[^~!]+) \s* (?P<modifiers>(~[^!]*\s*)*)? \s* (?:!\s*(?P<reason>.*))?$", message, re.UNICODE | re.VERBOSE | re.IGNORECASE)
    if match:
        modifiers = []
        if match.group('modifiers'):
            modifiers = list(filter(None, map(str.lower, map(str.strip, match.group('modifiers').split('~')))))
            print(modifiers)

        try:
            #TODO: make this less janky too
            global original_rolls
            original_rolls = []
            
            ast = grammar.parse(match.group('dice_expr'))
            print(ast)
            result = ast.eval()
            # if isinstance(result, DiceRoll):
            #     result = result.total
            print(result)

        except Exception as error:
            return error

        def format_dice_list(rolls):
            return f"`[{', '.join(str(r) for r in rolls)}]`"

        if "sort" in modifiers or "sorted" in modifiers:
            original_rolls = [sorted(l, reverse=True) for l in original_rolls]

        description = ' '.join(map(format_dice_list, original_rolls))
        if match.group('reason'):
            description += f"\n**Reason**: {match.group('reason')}"

        return {'title': str(result), 'description': description}

    # else:
    #     return {'title': "Dice Roll Usage:", 'description': help_message}


import pratt
import dice
# TOKENIZER

# REMEMBER, DON'T ALLOW A `!` IN HERE!
# (or it'll break the !reason feature, maybe...)
TOKEN_PATTERNS = (
    ('whitespace',  r"\s+"),
    ('dice',        r"\d*d\d+ (\s* (kl|kh|k|dl|dh|d)\d+)*"),  # a "dice" expression, e.g. "3d6"
    ('fudge_dice',  r"\d*df"),
    # ('drop_keep',   r"(kl|kh|k|dl|dh|d)\d+"), # k == kh, d == dl
    ('decimal',     r"\d*\.\d+"),  # either decimal or integer
    ('integer',     r"\d+"),  # either decimal or integer
    ('operator',    r"//|[+\-*x×/÷\^]"),
    ('parens',      r"[()]"),
    ('times',       r"times"), # e.g. `6 times 3d6`
    ('comma',       r","), # e.g. `3d6, 2d6+6`
)

# DEFINITION

#TODO: from tooboots:
# Definitely! The most important is keep highest x and keep lowest x
# Also lots of games use, of dice pool, how many are above target # 
# There are a few others that I see used too

# Also the reverse of keep highest/lowest: drop highest/lowest x
# Dicemaiden also has an unsort command. But most other dicebots keep the tally unsorted by default 
# and require a special command to sort it. Imho keeping it unsorted by default is the better way to do it
# There are a bunch more specialty commands but those are the basic ones I use the most  @Evelyn 

import operator
grammar = pratt.Parser(TOKEN_PATTERNS)

grammar.define_literal("<integer>", eval=int)
grammar.define_literal("<decimal>", eval=float)

class DiceRoll:
    def __init__(self, d, n=1):
        self.d = d
        self.n = n
        self.original = dice.d(d, n, total=False)
        # self.total = sum(self.original)
    
    @property
    def total(self):
        return sum(self.original)

    # # add
    # def __add__(self, right):
    #     return self.total + right
    # def __radd__(self, left):
    #     return left + self.total
    # # sub
    # def __sub__(self, right):
    #     return self.total - right
    # def __rsub__(self, left):
    #     return left - self.total
    # # neg
    # def __neg__(self):
    #     return -self.total
    # # mul
    # def __mul__(self, right):
    #     return self.total * right
    # def __rmul__(self, left):
    #     return left * self.total
    # # truediv
    # def __truediv__(self, right):
    #     return self.total / right
    # def __rtruediv__(self, left):
    #     return left / self.total
    # # floordiv
    # def __floordiv__(self, right):
    #     return self.total // right
    # def __rfloordiv__(self, left):
    #     return left // self.total
    # # pow
    # def __pow__(self, right):
    #     return self.total ** right
    # def __rpow__(self, left):
    #     return left ** self.total

@grammar.define_literal("<dice>")
def roll_dice(expr):
    # n, d = expr.split('d')

    # I know... So much regex jank...
    matches = re.findall(r"(\d*)d(\d+) ((?:\s* (?:kl|kh|k|dl|dh|d)\d+)*)", expr, re.UNICODE | re.VERBOSE | re.IGNORECASE)[0]
    n = int(matches[0] or 1)
    d = int(matches[1])
    modifiers = re.findall(r"\s* ((?:kl|kh|k|dl|dh|d)\d+)", matches[2], re.UNICODE | re.VERBOSE | re.IGNORECASE)

    roll = DiceRoll(d, n)
    original_rolls.append(list(roll.original))  # the `list()` ensures that the list is copied and it's not a reference
    print(roll.original)

    # little helper function for removing items from a list
    def remove_n(l, n, func): # func should be `min` or `max`
        for _ in range(n):
            if len(l) == 0:
                break
            m = func(l)
            l.remove(m)

    for mod in modifiers:
        matches = re.findall(r"(.*?)(\d+)", mod)[0]
        operation = matches[0]
        op_n = int(matches[1])

        if operation == 'd' or operation == 'dl':
            remove_n(roll.original, op_n, min)
        elif operation == 'dh':
            remove_n(roll.original, op_n, max)
        elif operation == 'k' or operation == 'kh':
            remove_n(roll.original, len(roll.original) - op_n, min)
        elif operation == 'kl':
            remove_n(roll.original, len(roll.original) - op_n, max)

    print(roll.original)
    return roll.total

@grammar.define_literal("<fudge_dice>")
def roll_fudge_dice(expr):
    n, _ = expr.split('d')
    roll = dice.d(3, int(n or 1), total=False)
    roll = list(map(lambda d: d-2, roll))
    def format_fate_die(die):
        return {1: '+', 0: ' ', -1: '-'}[die]
    original_rolls.append(list(map(format_fate_die, roll)))
    return sum(roll)

# ('drop_keep',   r"kl|kh|k|dl|dh|d"), # k == kh, d == dl
# @grammar.define_postfix("<drop_keep>", lbp=120)
# def drop_keep(right):
#     if not isinstance(right, DiceRoll):
#         raise SyntaxError("Can only drop/keep dice after a dice expression.")
#     return ...

# @grammar.define_custom("<drop_keep>", lbp=120)
# class DropKeep(pratt.Postfix):
#     def infix(self, left):
#         matches = re.findall(r"(.*?)(\d+)", self.value)[0]
#         self.operation = matches[0]
#         self.n = int(matches[1])
#         self.right = left
#         return self

#     def eval(self):
#         # little helper function for removing items from a list
#         def remove_n(l, n, func): # func should be `min` or `max`
#             for _ in range(n):
#                 m = func(l)
#                 l.remove(m)

#         right = self.right.eval()
#         if not isinstance(right, DiceRoll):
#             raise SyntaxError("Can only drop/keep dice after a dice expression.")

#         if self.operation == 'd':
#             remove_n(right.original, self.n, min)
#             return right



grammar.define_infix("+", lbp=20, eval=operator.add)

grammar.define_infix("-", lbp=20, eval=operator.sub)
grammar.define_prefix("-", rbp=100, eval=operator.neg)

grammar.define_infix("*", lbp=30, eval=operator.mul)
grammar.define_infix("x", lbp=30, eval=operator.mul)
grammar.define_infix("×", lbp=30, eval=operator.mul)
grammar.define_infix("/", lbp=30, eval=operator.truediv)
grammar.define_infix("÷", lbp=30, eval=operator.truediv)
grammar.define_infix("//", lbp=30, eval=operator.floordiv)

grammar.define_infix("^", lbp=40, right_assoc=True, eval=operator.pow)

# just defining the symbol without any functionality
grammar.define_symbol(")")

@grammar.define_custom("(")
class LeftParens(pratt.Symbol):
    def prefix(self):
        expr = self.expression(0)
        self.parser.advance(")")
        return expr

class MultipleResults:
    def __init__(self, results=None):
        self.results = list(results) if results else []

    def append(self, result):
        self.results.append(result)

    def __str__(self):
        def format_result(r):
            return f"({str(r)})" if isinstance(r, MultipleResults) else str(r)
            
        return ", ".join(map(format_result, self.results))

@grammar.define_custom(",", lbp=5)
class Comma(pratt.Symbol):
    def infix(self, left):
        # self.left = left
        # self.right = self.expression(0)

        self.left = [left]
        rbp = 5
        self.left.append(self.expression(rbp))
        print('value:', type(self.parser.symbol))
        while self.parser.symbol.value == ",":
            self.parser.advance(",")
            self.left.append(self.expression(rbp))

        return self

    def eval(self):
        return MultipleResults([l.eval() for l in self.left])

    def __repr__(self):
        return f"(multiple {' '.join(map(repr, self.left))})"

@grammar.define_custom("times", lbp=10)
class Times(pratt.Infix):
    def eval(self):
        n = self.left.eval()
        if not (isinstance(n, int) or (isinstance(n, float) and n.is_integer)):
            raise SyntaxError("The `times` operator must have an integer as the left argument.")
        if n > 20:
            raise dice.DiceError("Please don't roll more than 20 dice at once")
        return MultipleResults([self.right.eval() for _ in range(int(n))])



# @grammar.define_custom("<number>")
# class Number(Literal):
#     def eval(self):
#         return int(self.value)

# @grammar.define("+", lbp=20)
# class Add(Infix):
#     def eval(self):
#         return self.left.eval() + self.right.eval()

# @grammar.define("-", lbp=20, rbp=100)
# class Minus(Infix, Prefix):
#     def eval(self):
#         if self.right is None:
#             return -self.left.eval()
#         return self.left.eval() - self.right.eval()



# @grammar.define("*", lbp=30)
# class Multiply(Infix):
#     def eval(self):
#         return self.left.eval() * self.right.eval()

# class Divide(Infix):
#     def eval(self):
#         return self.left.eval() / self.right.eval()

# @grammar.define("^", lbp=40, right_assoc=True)
# class Exponent(Infix):
#     def eval(self):
#         return self.left.eval() ** self.right.eval()

# just defining the symbol without any functionality
# @grammar.define_custom(")", lbp=0)
# class RightParens(Symbol):
#     pass


if __name__ == "__main__":
    # Testing REPL
    while True:
        expr = input(">>> ")
        try:
            ast = grammar.parse(expr)
            print(ast)
            result = ast.eval()
            # if isinstance(result, DiceRoll):
            #     result = result.total
            print(result)
        except SyntaxError as error:
            print(error)
