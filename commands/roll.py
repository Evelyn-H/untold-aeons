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
    match = re.match(r"^\s*(?P<dice_expr>.*?)\s*(?:!\s*(?P<reason>.*))?$", message)
    if match:
        try:
            #TODO: make this less janky too
            global original_rolls
            original_rolls = []
            
            ast = grammar.parse(match.group('dice_expr'))
            print(ast)
            result = ast.eval()
            print(result)

            def format_dice_list(rolls):
                return f"`[{', '.join(str(r) for r in rolls)}]`"

            description = ' '.join(map(format_dice_list, original_rolls))
            if match.group('reason'):
                description += f"\n**Reason**: {match.group('reason')}"

            return {'title': str(result), 'description': description}

        except SyntaxError as error:
            return error

    # else:
    #     return {'title': "Dice Roll Usage:", 'description': help_message}


import pratt
import dice
# TOKENIZER

# REMEMBER, DON'T ALLOW A `!` IN HERE!
# (or it'll break the !reason feature, maybe...)
TOKEN_PATTERNS = (
    ('whitespace',  r"\s+"),
    ('dice',        r"\d*d\d+"),  # a "dice" expression, e.g. "3d6"
    ('fudge_dice',  r"\d*df"),
    ('decimal',     r"\d*\.\d+"),  # either decimal or integer
    ('integer',     r"\d+"),  # either decimal or integer
    ('operator',    r"//|[+\-*x/\^]"),
    ('parens',      r"[()]"),
    ('times',       r"times"), # e.g. `6 times 3d6`
    ('comma',       r","), # e.g. `3d6, 2d6+6`
) 

# DEFINITION

import operator
grammar = pratt.Parser(TOKEN_PATTERNS)

grammar.define_literal("<integer>", eval=int)
grammar.define_literal("<decimal>", eval=float)

# class DiceRoll:
#     def __init__(self, d, n=1):
#         self.d = d
#         self.n = n
#         self.original = dice.d(d, n, total=False)
#         self.total = sum(self.original)

@grammar.define_literal("<dice>")
def roll_dice(expr):
    n, d = expr.split('d')
    roll = dice.d(int(d), int(n or 1), total=False)
    original_rolls.append(roll)
    return sum(roll)

@grammar.define_literal("<fudge_dice>")
def roll_fudge_dice(expr):
    n, _ = expr.split('d')
    roll = dice.d(3, int(n or 1), total=False)
    roll = list(map(lambda d: d-2, roll))
    def format_fate_die(die):
        return {1: '+', 0: ' ', -1: '-'}[die]
    original_rolls.append(list(map(format_fate_die, roll)))
    return sum(roll)

grammar.define_infix("+", lbp=20, eval=operator.add)

grammar.define_infix("-", lbp=20, eval=operator.sub)
grammar.define_prefix("-", rbp=100, eval=operator.neg)

grammar.define_infix("*", lbp=30, eval=operator.mul)
grammar.define_infix("x", lbp=30, eval=operator.mul)
grammar.define_infix("/", lbp=30, eval=operator.truediv)
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
        if isinstance(n, int) or (isinstance(n, float) and n.is_integer):
            return MultipleResults([self.right.eval() for _ in range(int(n))])
        else:
            raise SyntaxError("The `times` operator must have an integer as the left argument.")



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
            print(ast.eval())
        except SyntaxError as error:
            print(error)
