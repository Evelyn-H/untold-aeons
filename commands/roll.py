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

            description = ' '.join(map(str, original_rolls))
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
    ('number',      r"\d+\.\d+ | \d+"),  # either decimal or integer
    ('operator',    r"//|[+\-*x/\^]"),
    ('parens',      r"[()]"),
) 

# DEFINITION

import operator
grammar = pratt.Parser(TOKEN_PATTERNS)

grammar.define_literal("<number>", eval=int)

# class DiceRoll:
#     def __init__(self, d, n=1):
#         self.d = d
#         self.n = n
#         self.original = core.d(d, n, total=False)
#         self.total = sum(self.original)

def roll_dice(expr):
    n, d = expr.split('d')
    roll = dice.d(int(d), int(n or 1), total=False)
    original_rolls.append(roll)
    return sum(roll)

grammar.define_literal("<dice>", eval=roll_dice)

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

@grammar.define_custom("(", lbp=110)
class LeftParens(pratt.Symbol):
    def prefix(self):
        expr = self.expression(0)
        self.parser.advance(")")
        return expr


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
