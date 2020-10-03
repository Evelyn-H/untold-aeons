import random

class Trait:
    def __init__(self, value_func, adjectives):
        self.value_func = value_func
        self.adjectives = adjectives

    def value(self, character):
        if callable(self.value_func):
            return int(self.value_func(character))
        else:
            # if it isn't a function just assume it's a static value
            return int(self.value_func)

    def random_adjective(self):
        return random.choice(self.adjectives)

    def __str__(self):
        return "<Trait: " + self.adjectives[0] + ">"

    def __repr__(self):
        return str(self)

def get_character_traits(character):
    applicable_traits = list(filter(
        lambda trait_value_pair: trait_value_pair[1] > 0,
        [(trait, trait.value(character)) for trait in all_traits]
    ))

    print(applicable_traits)
    return list(map(lambda trait_value_pair: trait_value_pair[0], applicable_traits))


# TODO: split traits into categories (physical description, mental / stat based, ...)
# TODO: add addjectives to the adjectives (e.g. "gorgeous blue eyes", "piercing blue eyes", "piercing green eyes", ...)
# TODO: proportionately random selection of traits

all_traits = [
    Trait(lambda c: (c.STR >= 70),
        ["strong", "burly", "muscular"]),

    Trait(lambda c: (c.STR <= 35),
        ["weak"]),

    Trait(lambda c: (c.CON >= 70),
        ["tough"]),

    Trait(lambda c: (c.CON <= 24),
        ["sickly", "frail"]),

    Trait(lambda c: (c.DEX >= 70),
        ["nimble"]),

    Trait(lambda c: (c.DEX <= 35),
        ["clumsy"]),

    Trait(lambda c: (c.SIZ >= 80),
        ["large", "tall", "stout"]),

    Trait(lambda c: (c.SIZ <= 45),
        ["small", "short", "slim"]),

    Trait(lambda c: (c.INT >= 80),
        ["intelligent", "bookish", "smart"]),

    Trait(lambda c: (c.INT <= 45),
        ["dull"]),

    Trait(lambda c: (c.POW >= 70),
        ["driven", "strong-willed"]),

    # Trait(lambda c: (c.POW <= 35),
    #     ["weak-willed"]),

    Trait(lambda c: (c.APP >= 70),
        ["charismatic", "attractive", "elegant"]),

    Trait(lambda c: (c.APP <= 35),
        ["ugly", "scruffy"]),

    Trait(lambda c: (c.EDU >= 80),
        ["well-educated"]),

    Trait(lambda c: (c.EDU <= 45),
        ["poorly-educated"]),
]
