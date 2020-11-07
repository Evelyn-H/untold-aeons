import re

# heavily based on code from: https://github.com/percolate/pratt-parser
# and inspired by: http://effbot.org/zone/simple-top-down-parsing.htm

# TOKENIZER

def tokenize(source, pattern):
    def error():
        raise SyntaxError(f"Unexpected character at position {i}: `{source[i]}`")

    i = 0
    for match in pattern.finditer(source):
        pos = match.start()
        if pos > i:
            error()
        i = match.end()
        name = match.lastgroup
        if name == "whitespace":
            continue
        else:
            token = (f"<{name}>", match.group(0))
        yield token

    if i < len(source):
        error()


# PARSER

#TODO:
#  - Add support for symbol alternate names (e.g. '*' and 'x')
#  - make define_x also work as decorators

class Parser:
    def __init__(self, lex_pattern):
        token_regex = '|'.join(fr"(?P<{name}>{pattern})" for name, pattern in lex_pattern)
        self.lex_pattern = re.compile(token_regex, re.UNICODE | re.VERBOSE | re.IGNORECASE)
        self.token_stream = None
        self.symbol = None
        self.symbol_table = {}

    def parse(self, source):
        # try:
        self.token_stream = tokenize(source, self.lex_pattern)
        self.advance()

        return self.expression(0)

        # except SyntaxError as error:
            # pass

    def expression(self, rbp):
        # little helper function
        def lbp(symbol):
            if not hasattr(symbol, "lbp"):
                raise SyntaxError(f"Symbol `{symbol.name}` not allowed in this position.")
            return symbol.lbp

        old_symbol = self.symbol
        self.advance()
        # print(old_symbol, self.symbol)
        left = old_symbol.prefix()

        while lbp(self.symbol) > rbp:
            old_symbol = self.symbol
            self.advance()
            left = old_symbol.infix(left)
        if isinstance(left, EndSymbol):
            raise SyntaxError(f"Unexpected end of stream")
        return left

    def advance(self, value=None):
        try:
            token_type, token = next(self.token_stream)
        except StopIteration:
            self.symbol = EndSymbol(self)
            return

        # if a value is given only that token will be accepted
        if value and not type(value) == type(token):
            raise SyntaxError(f"Expected `{value}`, got `{token}` instead")

        # lookup table shenanigans
        # check for value first
        # this will handle operators and such
        if token in self.symbol_table:
            symbol_class = self.symbol_table[token]
        # if not found check for the type instead
        # this will take care of literals
        elif token_type in self.symbol_table:
            # then symbol's type
            symbol_class = self.symbol_table[token_type]
        else:
            raise SyntaxError(f"Undefined token: ({token_type}, `{token}`)")

        self.symbol = symbol_class(self, token)

    def define_custom(self, name, **kwargs):
        def wrapper(symbol_class):
            symbol_class.name = name
            # this lets us pass arguments like `lbp` and `right_assoc` to `define`
            for k, v in kwargs.items():
                setattr(symbol_class, k, v)
            self.symbol_table[name] = symbol_class
            return symbol_class
        return wrapper

    def define_symbol(self, name, lbp=0):
        symbol_class = type(
            "CustomSymbol",
            (Symbol,),
            { 'name': name, 'lbp': lbp }
        )
        self.symbol_table[name] = symbol_class
        return symbol_class


    def define_literal(self, name, *, eval=None):
        symbol_class = type(
            "CustomLiteralSymbol",
            (Literal,),
            { 
                'name': name,
                'eval': (lambda self: eval(self.value)) if eval else None
            }
        )
        self.symbol_table[name] = symbol_class
        def wrapper(func):
            setattr(self.symbol_table[name], 'eval', (lambda self: func(self.value)))
            return func

        return wrapper

    def define_infix(self, name, lbp, *, right_assoc=False, eval=None):
        base_class = (self.symbol_table[name], Infix) if name in self.symbol_table else (Infix,)
        symbol_class = type(
            "CustomInfixSymbol",
            base_class,
            {
                'name': name, 'lbp': lbp, 'right_assoc': right_assoc,
                # '': eval
                # 'eval': (lambda self: eval(self.left.eval(), self.right.eval()))
            }
        )
        symbol_class.infix_eval = eval
        self.symbol_table[name] = symbol_class
        def wrapper(func):
            setattr(self.symbol_table[name], 'infix_eval', func)
            return func

        return wrapper

    def define_prefix(self, name, rbp, *, eval=None):
        base_class = (self.symbol_table[name], Prefix) if name in self.symbol_table else (Prefix,)
        symbol_class = type(
            "CustomPrefixSymbol",
            base_class,
            {
                'name': name, 'rbp': rbp,
                'prefix_eval': eval
                # 'eval': (lambda self: eval(self.left.eval(), self.right.eval()))
            }
        )
        self.symbol_table[name] = symbol_class
        def wrapper(func):
            setattr(self.symbol_table[name], 'prefix_eval', func)
            return func

        return wrapper

    def define_postfix(self, name, lbp, *, eval=None):
        base_class = (self.symbol_table[name], Postfix) if name in self.symbol_table else (Postfix,)
        symbol_class = type(
            "CustomPostfixSymbol",
            base_class,
            {
                'name': name, 'lbp': lbp,
                'postfix_eval': eval
                # 'eval': (lambda self: eval(self.left.eval(), self.right.eval()))
            }
        )
        self.symbol_table[name] = symbol_class
        def wrapper(func):
            setattr(self.symbol_table[name], 'postfix_eval', func)
            return func

        return wrapper


class Symbol(object):
    """Base class for all nodes"""
    name = None

    def __init__(self, parser, value=None):
        self.parser = parser
        # simple alias for brevity
        self.expression = self.parser.expression
        self.value = value
        self.left = None
        self.right = None

    def prefix(self):
        raise SyntaxError(f"Symbol `{self.name}` not allowed in prefix position.")

    def infix(self, left):
        raise SyntaxError(f"Symbol `{self.name}` not allowed in infix position.")


    def eval(self):
        def get_func(name):
            if hasattr(getattr(self, name), '__func__'):
                # the .__func__ fixes problems with functions getting bound
                return getattr(self, name).__func__
            return getattr(self, name)

        if hasattr(self, 'prefix_eval') and self.left and self.right is None:
            return get_func('prefix_eval')(self.left.eval()) 
        elif hasattr(self, 'postfix_eval') and self.left is None and self.right:
            return get_func('postfix_eval')(self.right.eval())
        elif hasattr(self, 'infix_eval'):
            return get_func('infix_eval')(self.left.eval(), self.right.eval())
        else:
            raise NotImplementedError(f"`eval` not implemented for `{self.name}`")


    def __repr__(self):
        if self.left and self.right:
            return f"({self.name} {repr(self.left)} {repr(self.right)})"
        elif self.left:
            return f"({self.name} {repr(self.left)})"
        elif self.right:
            return f"({self.value or self.name} {repr(self.right)})"
        else:
            return f"{self.value}"

class EndSymbol(Symbol):
    lbp = -1
    def prefix(self):
        return self


# Technically a special case of PrefixSymbol,
# but doing it like this this just makes it easier to work with
class Literal(Symbol):
    def prefix(self):
        return self

# NUD, Null Denotation
# i.e. starts a (sub)expression
class Prefix(Symbol):
    rbp = 0
    def prefix(self):
        self.left = self.expression(self.rbp)
        return self

# LED, Left Denotation
# i.e. continues an expression
class Infix(Symbol):
    lbp = 0
    right_assoc=False

    def infix(self, left):
        self.left = left
        rbp = self.lbp - int(self.right_assoc)
        self.right = self.parser.expression(rbp)
        return self

# Postfix
class Postfix(Symbol):
    lbp = 0
    def infix(self, left):
        self.right = left
        return self
