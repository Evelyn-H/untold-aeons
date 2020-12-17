import re
import dice

help_message = """\
`!roll <dice>`: roll arbitrary dice expressions
`!roll <dice> !<reason>`: optionally give a reason for the dice roll

Features / Syntax:
  - `xdy`: roll x dice with y sides each
  - `+` `-` `*` `/`: simple arithmetic operators
  - `n times y`: roll the y expression n times

Dice modifiers:
These must always follow a dice expression (`xdy`) and modify the roll in some way. (`#` represents a number)
  - `t#`: target number for a success
  - `f#`: target number for a failure
  - `d#`: drop lowest dice
  - `dh#`: drop highest dice
  - `k#`: keep highest dice
  - `kl#`: keep lowest dice

Examples:
    `!roll 3d6`: simple 3d6 roll
    `!roll 6 times 3d6`: roll 6 sets of 3d6
    `!roll (2d6+6)*5`: CoC characteristic roll
    `!roll 4d6k3`: roll 4d6, keep highest 3
    `!roll 4d3 t3 f1`: 4d3 with successes on 3s, failures on 1s (Fudge dice!)
    `!roll 4df`: shorthand for fudge dice, same as above
"""

async def roll_simple(message, ctx):
    try:
        d = int(message)
    except:
        return None
        
    return await roll("d" + message, ctx)

#TODO: make this less janky
original_rolls = []

# Custom Dice roll
async def roll(message, ctx):
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
            # print("ast:", repr(ast.name), repr(ast.value), ast.left, ast.right)

            # Error checking the user instead of the code :p
            try:
                if ast.name == "<dice>" and ("d100" in ast.value or "1d100" in ast.value):
                    await ctx.channel.send("If you want to do CoC skill checks, try using `!coc <skill>` instead!")
                if ast.name == "<integer>":
                    print("it's d100")
                    await ctx.channel.send(f"If you want to roll a dice, try `!roll d{ast.value}` instead of `!roll {ast.value}`.")
            except:
                pass

            # check if it's a straight dice roll without *any* modifiers of any kind
            pure_diceroll = ast.name == "<dice>" and re.match(r"^\s*(1?)d(\d+)\s*$", ast.value, re.UNICODE | re.VERBOSE | re.IGNORECASE)

            result = ast.eval()
            # if isinstance(result, DiceRoll):
            #     result = result.total
            print(result)

        except (dice.DiceError, SyntaxError, NotImplementedError) as error:
            if "help" in message:
                return {'title': "Dice Roll Usage:", 'description': help_message}
            else:
                return error

        if "sort" in modifiers or "sorted" in modifiers:
            for r in original_rolls:
                r.original.sort(reverse=True)
                r.rolls.sort(reverse=True)

        description = ""
        if not pure_diceroll:
            description += ' '.join(map(lambda s: f"`{s}`", map(str, original_rolls)))
        if match.group('reason'):
            description += f"\n**Reason**: {match.group('reason')}"

        return {'title': str(result), 'description': description}

    else:
        return {'title': "Dice Roll Usage:", 'description': help_message}



import pratt
import dice
# TOKENIZER

# REMEMBER, DON'T ALLOW A `!` IN HERE!
# (or it'll break the !reason feature, maybe...)
TOKEN_PATTERNS = (
    ('whitespace',  r"\s+"),
    ('dice',        r"\d*d(\d+|f|%) (\s* (kl|kh|k|dl|dh|d|t|f)\d+)*"),  # a "dice" expression, e.g. "3d6"
    # ('fudge_dice',  r"\d*df"),
    # ('drop_keep',   r"(kl|kh|k|dl|dh|d)\d+"), # k == kh, d == dl
    ('decimal',     r"\d*\.\d+"),  # either decimal or integer
    ('integer',     r"\d+"),  # either decimal or integer
    ('operator',    r"//|[+\-*x×/÷\^]"),
    ('parens',      r"[()]"),
    ('times',       r"times"), # e.g. `6 times 3d6`
    ('comma',       r","), # e.g. `3d6, 2d6+6`
)

# DEFINITION

import operator
grammar = pratt.Parser(TOKEN_PATTERNS)

grammar.define_literal("<integer>", eval=int)
grammar.define_literal("<decimal>", eval=float)

class DiceRoll:
    def __init__(self, d, n=1):
        self.d = d
        self.n = n
        self.original = dice.d(d, n, total=False)
        self.rolls = list(self.original)  # the `list()` ensures that the list is copied and it's not a reference
        # self.total = sum(self.original)
    
    @property
    def total(self):
        return sum(self.rolls)

    def __str__(self):
        return str(self.original)

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

class SuccessFailureRoll(DiceRoll):
    @classmethod
    def transform_DiceRoll(cls, roll):
        roll.__class__ = cls  # I know, super hacky but it works :p
        roll.target = None
        roll.failure = None
        return roll

    def count(self, d):
        total = 0
        if self.target:
            total += int(d >= self.target)
        if self.failure:
            total -= int(d <= self.failure)
        return total

    # @property
    # # bad name, but can't think of anything better
    # def total_counts(self):
    #     return list(map(self.count, self.rolls))

    @property
    def total(self):
        return sum(map(self.count, self.rolls))

    def __str__(self):
        def format_die(d):
            fate = getattr(self, 'fate', False)
            c = self.count(d)
            if c > 0:
                return '+' if fate else f"{d} (+)"
            elif c < 0:
                return '-' if fate else f"{d} (-)"
            else:
                return ' ' if fate else f"{d}"

        return f"[{', '.join(format_die(d) for d in self.original)}]"
        # return str([str(r) for r in map(format_die, self.total_counts)])

@grammar.define_literal("<dice>")
def roll_dice(expr):
    # n, d = expr.split('d')

    # I know... So much regex jank...
    expr = expr.lower()
    matches = re.findall(r"(\d*)d(\d+|f|%) ((?:\s* (?:kl|kh|k|dl|dh|d|t|f)\d+)*)", expr, re.UNICODE | re.VERBOSE | re.IGNORECASE)[0]
    n = int(matches[0] or 1)
    d = matches[1]
    modifiers = re.findall(r"\s* ((?:kl|kh|k|dl|dh|d|t|f)\d+)", matches[2], re.UNICODE | re.VERBOSE | re.IGNORECASE)

    # fudge dice
    if d == 'f':
        # gonna do a little transformation here
        d = 3  # roll d3
        # and add the `t3f1` modifiers to the start of the modifiers
        modifiers.insert(0, "t3")
        modifiers.insert(0, "f1")
        modifiers.insert(0, "fate0")  # just a marker to mark the roll as coming from a fate die

    # percentile dice
    elif d == '%':
        d = 100


    roll = DiceRoll(int(d), n)
    original_rolls.append(roll)
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

        #  drop / keep operators
        if operation == 'd' or operation == 'dl':
            # TODO: yknow, these should really be DiceRoll methods...
            remove_n(roll.rolls, op_n, min)
        elif operation == 'dh':
            remove_n(roll.rolls, op_n, max)
        elif operation == 'k' or operation == 'kh':
            remove_n(roll.rolls, len(roll.rolls) - op_n, min)
        elif operation == 'kl':
            remove_n(roll.rolls, len(roll.rolls) - op_n, max)

        # target / failure operators
        elif operation == 't':
            if not isinstance(roll, SuccessFailureRoll):
                roll = SuccessFailureRoll.transform_DiceRoll(roll)
            roll.target = op_n

        elif operation == 'f':
            if not isinstance(roll, SuccessFailureRoll):
                roll = SuccessFailureRoll.transform_DiceRoll(roll)
            roll.failure = op_n

        elif operation == 'fate':
            roll.fate = True

    print(roll.rolls)
    return roll.total

# @grammar.define_literal("<fudge_dice>")
# def roll_fudge_dice(expr):
#     n, _ = expr.split('d')
#     roll = dice.d(3, int(n or 1), total=False)
#     roll = list(map(lambda d: d-2, roll))
#     def format_fate_die(die):
#         return {1: '+', 0: ' ', -1: '-'}[die]
#     original_rolls.append(list(map(format_fate_die, roll)))
#     return sum(roll)

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
