class Occupation:
    def __init__(self, name, stat_weights=None):
        self.name = name
        self.stat_weights = stat_weights or (0, 0, 0, 0, 0, 0, 0, 0)
        # remove my super janky ... hack
        self.stat_weights = tuple([0 if w == ... else w for w in self.stat_weights])

    def appropriateness(self, c: "npc.Character"):
        return sum([
            c.z_score(c.STR) * self.stat_weights[0],
            c.z_score(c.CON) * self.stat_weights[1],
            c.z_score(c.DEX) * self.stat_weights[2],
            c.z_score(c.SIZ) * self.stat_weights[3],
            c.z_score(c.INT) * self.stat_weights[4],
            c.z_score(c.POW) * self.stat_weights[5],
            c.z_score(c.APP) * self.stat_weights[6],
            c.z_score(c.EDU) * self.stat_weights[7],
        ])
        # maybe normalize based on the sum of stat_weights?


lovecraftian = [
    #                            STR CON DEX SIZ INT POW APP EDU
    Occupation("Antiquarian",   (..., -1,...,...,  1,  1,...,  2)),  # I know, I know, don't judge me for the ...
    Occupation("Archeologist",  (...,...,  1,...,  1,...,...,  2)),  # it makes it so much more readable!
    Occupation("Author",        ( -1, -1,...,...,  1,  2,...,  1)),
    Occupation("Dilletante",    (...,...,...,..., -1,...,  3,...)),
    Occupation("Doctor",        (...,  1,...,...,  1,...,...,  2)),
    Occupation("Journalist",    (..., -1,...,...,  1,...,  1,  1)),
    Occupation("Librarian",     ( -1, -1,...,...,  1,..., -1,  3)),
    Occupation("Occultist",     (...,  1,...,...,  1,  2, -1,  1)),
    Occupation("Police Officer",(  2,...,  2,  1,..., -1,..., -1)),
    Occupation("Professor",     ( -1,..., -1,...,  2,...,...,  3)),
]

other = [
    #                            STR CON DEX SIZ INT POW APP EDU
    Occupation("Accountant",    ( -1,..., -1,...,  1,..., -1,  2)),
    Occupation("Acrobat",       (...,...,  3, -1,...,...,  1,...)),
    Occupation("Actor",         (...,...,...,..., -1,  1,  3, -1)),
    Occupation("Detective",     (..., -1,...,...,  2,  1,...,  1)),
    Occupation("Animal Trainer",(...,...,...,  1,...,  3,  1, -1)),
    Occupation("Architect",     ( -1,..., -1,...,  1,...,...,  2)),
    Occupation("Artist",        (...,...,  1,...,...,  2,  1,...)),
    # Occupation("Assassin",      (  1,...,  3,...,...,  1, -1, -1)),
    Occupation("Athlete",       (  2,  1,  2,  1, -1,...,..., -2)),
    Occupation("Aviator",       (...,...,  2,  1,...,...,...,  1)),
    Occupation("Bank Robber",   (  2,...,  2,  1, -2,..., -1, -1)),
    Occupation("Bartender",     (...,  1,...,...,...,  1,  1, -1)),
    Occupation("Big Game Hunter",( 1,  2,...,  1,...,...,..., -1)),
    Occupation("Book Dealer",   (...,...,..., -2,  2,  1, -1,  3)),
    Occupation("Bootlegger",    (  1,  1,  1,...,...,...,..., -2)),
    Occupation("Bounty Hunter", (  1,...,  1,  1,  1,...,..., -2)),
    Occupation("Wrestler",      (  3,  2, -1,  2, -1,...,..., -1)),
    Occupation("Burglar",       (...,...,  3,..., -1,...,..., -2)),
    Occupation("Butler",        (...,...,...,...,...,  1,  1,  2)),
    Occupation("Chauffeur",     (...,...,  2,...,  1,  1,..., -1)),
    Occupation("Clergy member", ( -1,..., -1,...,...,  3,...,  2)),
    Occupation("Conman",        ( -1,..., -1,...,  1,  2,  3,...)),
    Occupation("Artisan",       (...,...,  1,...,...,  1,...,...)),
    Occupation("Cult Leader",   ( -1,..., -1,...,  2,  3,  2, -1)),
    Occupation("Designer",      (..., -1,..., -1,...,  1,  1,  2)),
    Occupation("Diver",         (...,  2,  2, -1,...,...,...,  1)),
    Occupation("Drifter",       (..., -1,...,..., -1,..., -1, -2)),
    Occupation("Editor",        ( -1, -1,...,...,  1,...,...,  2)),
    Occupation("Gov. Official", (...,...,...,..., -1,  1,  2,  1)),
    Occupation("Engineer",      (...,...,...,...,  1,...,...,  2)),
    Occupation("Entertainer",   (...,...,  1,...,  1,  1,  2, -1)),
    Occupation("Explorer",      (  1,  1,  1,...,...,  1,  1,...)),
    Occupation("Farmer",        (  1,  2,  1,...,...,...,..., -2)),
    Occupation("Federal Agent", (...,...,...,...,  1,  1,...,  1)),
    Occupation("Fence",         ( -1,...,...,...,  1,  1,  2,...)),
    Occupation("Firefighter",   (  2,  2,  1,...,...,  1,...,...)),
    Occupation("Surgeon",       (...,...,  1,...,...,  1, -1,  3)),
    #                            STR CON DEX SIZ INT POW APP EDU
    Occupation("Counterfeiter", ( -1,...,  1,...,  2,...,...,  1)),
    Occupation("Gambler",       (...,...,  1,...,  1, -2,  1,...)),
    Occupation("Gangster",      (...,...,...,  1,...,  1,  1, -1)),
    Occupation("Hobo",          (...,  1,...,...,..., -1, -1, -2)),
    Occupation("Laborer",       (  2,  1,...,  1,...,..., -1, -2)),
    Occupation("Lawyer",        (...,...,...,...,...,  2,  1,  2)),
    Occupation("Lumberjack",    (  2,  1,...,  1,...,..., -1, -2)),
    Occupation("Mechanic",      (  1,...,  1,...,  2,..., -1,  1)),
    Occupation("Military Officer",(1,  1,...,...,  2,  1,...,  2)),
    Occupation("Miner",         (  2,  1,...,  1,...,..., -1, -2)),
    Occupation("Missionary",    ( -1,..., -1,...,...,  2,  1,  1)),
    Occupation("Museum Curator",( -1, -1,...,...,...,  1,...,  2)),
    Occupation("Musician",      (...,...,  1,...,...,...,  2,...)),
    Occupation("Nurse",         (...,  1,...,...,...,  2,...,  2)),
    Occupation("Parapsychologist",(...,1, -1,...,...,  2, -1,  2)),
    Occupation("Pharmacist",    (...,...,...,...,  1,...,...,  2)),
    Occupation("Photographer",  ( -1,...,  1,...,  1,...,...,  1)),
    Occupation("Private Investigator",(...,  1,...,...,  2,..., -1, 1)),
    Occupation("Psychiatrist",  ( -1,..., -1,...,...,  1,...,  2)),
    Occupation("Psychologist",  ( -1,..., -1,...,...,  1,  1,  2)),
    Occupation("Researcher",    ( -1,..., -1,...,  2,...,...,  3)),
    #                            STR CON DEX SIZ INT POW APP EDU
    Occupation("Sailor",        (  2,  1,...,  1,...,..., -1, -2)),
    Occupation("Salesperson",   (..., -1,..., -1,...,  1,  2, -1)),
    Occupation("Scientist",     ( -1,..., -1,...,  2,...,...,  2)),
    Occupation("Secretary",     ( -1,...,...,...,...,...,  1, -1)),
    Occupation("Shopkeeper",    (..., -1,..., -1,...,  1,...,...)),
    Occupation("Smuggler",      (  1,...,  2, -1,...,...,..., -1)),
    Occupation("Soldier",       (  1,  1,  1,  1,...,  1,..., -1)),
    Occupation("Spy",           ( -1,...,...,...,  1,  1,  2,  1)),
    Occupation("Taxi Driver",   (...,...,...,...,...,  1,..., -1)),
    Occupation("Thug",          (  2,  1,...,  1, -2,..., -1,...)),
    # Occupation("Undertaker",    (...,...,...,...,...,...,...,...)),
    # Occupation("Union Activist",(...,...,...,...,...,...,...,...)),
    Occupation("Zealot",        (...,...,...,...,...,  3,...,...)),
    # Occupation("Zookeeper",     (...,...,...,...,...,...,...,...)),
]

all = lovecraftian + other
