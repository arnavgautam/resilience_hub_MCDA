from random import seed, randint
from constant import FIXED_COSTS, Technology


class TechnologyEnumerator():

    def __init__(self):
        seed(9001)
        self.tech_sets = []

    def enumerate_tech_sets(self, upfront_cost_ceiling=1e9):
        while (len(self.tech_sets) < 1000):
            tech_set = dict()
            purchase_cost = 0
            for tech in Technology:
                tech_set[tech] = randint(0,100)
                purchase_cost += FIXED_COSTS[tech] * tech_set[tech]
            if purchase_cost < upfront_cost_ceiling:
                self.tech_sets.append(tech_set)