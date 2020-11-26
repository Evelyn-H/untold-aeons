import math
import random
import numpy as np
import dice

from . import tables
from . import traits
from . import names
from . import occupations

# ideas:
#    - description based on stats if possible otherwise random
#    - weigh random occupation towards ones with where the stats would be appropriate
#    - optional "balanced" npcs, where ones with stats that ate too low / high are thrown out

# little helper function to pick an element from a list with weighted probability
def pick(l, p=None):
    if not p:
        l, p = zip(*l)
    total = sum(p)
    return np.random.choice(l, p=list(map(lambda x: x / total, p)))

class Character:
    def __init__(self, name=None):
        self.gender = random.choice(["male", "female"])
        self.name = name if name else Character.generate_name(gender=self.gender)
        self.STR = dice.d(6, 3) * 5
        self.CON = dice.d(6, 3) * 5
        self.DEX = dice.d(6, 3) * 5
        self.SIZ = (dice.d(6, 2) + 6) * 5
        self.INT = (dice.d(6, 2) + 6) * 5
        self.POW = dice.d(6, 3) * 5
        self.APP = dice.d(6, 3) * 5
        self.EDU = (dice.d(6, 2) + 6) * 5
        self.age = 15 + dice.d(6, 2) + min(dice.d(30, 3, total=False))
        self.luck = dice.d(6, 3) * 5
        self.sanity = self.POW

        self.hp = math.floor((self.SIZ + self.CON) / 10)

        if self.DEX < self.SIZ and self.STR < self.SIZ:
            self.move_rate = 7
        elif self.DEX > self.SIZ and self.STR > self.SIZ:
            self.move_rate = 9
        else:
            self.move_rate = 8

        if self.STR + self.SIZ < 65:
            self.damage_bonus = "-2"
            self.build = -2
        elif self.STR + self.SIZ < 85:
            self.damage_bonus = "-1"
            self.build = -1
        elif self.STR + self.SIZ < 125:
            self.damage_bonus = "0"
            self.build = 0
        elif self.STR + self.SIZ < 165:
            self.damage_bonus = "+1d4"
            self.build = 1
        else:
            self.damage_bonus = "+1d6"
            self.build = 2

        self.occupation = self.generate_occupation()
        #TODO: calculate credit reating based on occupation
        self.credit_rating = 0

    @staticmethod
    def z_score(value):
        avg = 10.5
        std = 3
        return (value / 5 - avg) / std


    @classmethod
    def generate_name(cls, gender=None):
        if gender == "male":
            first_name = pick(names.male)
        elif gender == "female":
            first_name = pick(names.female)
        else:
            first_name = pick(names.male + names.female)

        return first_name + " " + pick(names.family)

    def generate_occupation(self):
        # possibilities = [(
        #     occupation, 
        #     max(0, occupation.appropriateness(self)) + 1) 
        # for occupation in occupations.all]
        # # print(possibilities)

        # possibilities.sort(key=lambda x: x[1], reverse=True)
        # # only choose from top 10
        # possibilities = possibilities[0:10]
        # # for p in possibilities:
        # #     print(p[0].name, "\t", p[1])


        # m = max(possibilities, key=lambda x: x[1])
        # best = [o[0] for o in possibilities if o[1] == m[1]]
        # print(m, best)
        # return pick(possibilities)  # weighted random selection

        possibilities = [(
            occupation, 
            max(0, occupation.appropriateness(self)) + 1) 
        for occupation in occupations.all]
        # print(possibilities)

        selection = [pick(possibilities) for _ in range(20)]
        return random.choice(selection)

        # return random.choice(occupations.all)

    def generate_description(self):
        # traits = list(filter(lambda trait: trait != "", [
        #     "strong"            if self.STR >= 70 else "",
        #     "weak"              if self.STR <= 35 else "",
        #     "tough"             if self.CON >= 70 else "",
        #     # "sickly"            if self.CON <= 35 else "",
        #     "nimble"            if self.DEX >= 70 else "",
        #     "clumsy"            if self.DEX <= 35 else "",
        #     "large"             if self.SIZ >= 80 else "",
        #     "small"             if self.SIZ <= 45 else "",
        #     "intelligent"       if self.INT >= 80 else "",
        #     # "dumb"              if self.INT <= 45 else "",
        #     "driven"            if self.POW >= 70 else "",
        #     # "weak-willed"       if self.POW <= 35 else "",
        #     "charismatic"       if self.APP >= 70 else "",
        #     "ugly"              if self.APP <= 35 else "",
        #     "well-educated"     if self.EDU >= 80 else "",
        #     "poorly-educated"   if self.EDU <= 45 else "",
        # ]))
        # TODO: do physical characteristics separately
        # TODO: don't be too offensive
        # TODO: add synonyms
        # TODO: make a trait class to encapsulate synonyms, condition(s), and priorities and stuff?

        character_traits = list(map(lambda t: t.random_adjective(), traits.get_character_traits(self)))

        if len(character_traits) == 0:
            traits_str = "awefully average"
        elif len(character_traits) == 1:
            traits_str = character_traits[0]
        else:
            traits_str = ", ".join(character_traits[:-1]) + " and " + character_traits[-1]

        description =  f"{self.name} is {'an' if traits_str.startswith(('a', 'e', 'i', 'o', 'u')) else 'a'} {traits_str} {self.occupation.name}.\n"
        # description += f"{'She' if self.gender == 'female' else 'He'} is <>."

        return description

    def generate_embed(self):
        title = f"**{self.name}**, {self.age}"

        # text description
        description = self.generate_description() + "\n"

        # stat block
        description += "```"
        # description += f"STR: {self.STR},  INT: {self.INT},  Credit: {self.credit_rating}\n" \
        description += f"STR: {self.STR},  INT: {self.INT}\n" \
                     + f"CON: {self.CON},  POW: {self.POW},  Move: {self.move_rate}\n" \
                     + f"DEX: {self.DEX},  APP: {self.APP},  DB: {self.damage_bonus}\n" \
                     + f"SIZ: {self.SIZ},  EDU: {self.EDU},  Build: {self.build}\n"
        description += "\n"
        description += f"Hit points: {self.hp},  Luck: {self.luck},  Sanity: {self.sanity}\n"
        description += "```"

        return {'title': title, 'description': description}

if __name__ == "__main__":
    character = Character()
    print(character)
