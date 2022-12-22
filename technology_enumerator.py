from random import seed, randint
from constant import FIXED_COSTS, Technology


class TechnologyEnumerator():

    def __init__(self):
        seed(9001)
        self.tech_sets = []

    def enumerate_tech_sets(self, upfront_cost_ceiling=1e9):
        zero_tech_set = dict()
        for tech in Technology:
            zero_tech_set[tech] = 0
        for tech in Technology:
            single_tech_set = zero_tech_set.copy()
            single_tech_set[tech] = upfront_cost_ceiling // FIXED_COSTS[tech]
            self.tech_sets.append(single_tech_set)
        for i in range(16):
            for j in range(16):
                for k in range(16):
                    new_tech_set = zero_tech_set.copy()
                    new_tech_set[Technology.SOLAR_STORAGE] = i
                    new_tech_set[Technology.SOFC] = j
                    new_tech_set[Technology.DIESEL] = k
                    
                    purchase_cost = 0
                    for tech in Technology:
                        purchase_cost += FIXED_COSTS[tech] * new_tech_set[tech]
                    if purchase_cost < upfront_cost_ceiling:
                        self.tech_sets.append(new_tech_set)
        # while (len(self.tech_sets) < 10000):
        #     tech_set = dict()
        #     purchase_cost = 0
        #     for tech in Technology:
        #         tech_set[tech] = randint(0,upfront_cost_ceiling // FIXED_COSTS[tech])
        #         purchase_cost += FIXED_COSTS[tech] * tech_set[tech]
        #     if purchase_cost < upfront_cost_ceiling:
        #         self.tech_sets.append(tech_set)