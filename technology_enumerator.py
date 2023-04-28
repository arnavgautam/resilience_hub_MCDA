from random import seed, randint
from constant import FIXED_COSTS, Technology

import time

class TechnologyEnumerator():

    def __init__(self):
        seed(9001)
        self.tech_sets = []

    def enumerate_tech_sets(self, upfront_cost_ceiling=1e9):
        enumeration_start_time = time.perf_counter()
        zero_tech_set = dict()
        for tech in Technology:
            zero_tech_set[tech] = 0
        for tech in Technology:
            single_tech_set = zero_tech_set.copy()
            single_tech_set[tech] = upfront_cost_ceiling // FIXED_COSTS[tech]
            self.tech_sets.append(single_tech_set)
        max_tech_num = 17# upfront_cost_ceiling // min([FIXED_COSTS[t] for t in Technology])
        for i in range(max_tech_num):
            for j in range(max_tech_num):
                for k in range(max_tech_num):
                    new_tech_set = zero_tech_set.copy()
                    new_tech_set[Technology.SOLAR_STORAGE] = i
                    new_tech_set[Technology.SOFC] = j
                    new_tech_set[Technology.DIESEL] = k
                    
                    purchase_cost = 0
                    for tech in Technology:
                        purchase_cost += FIXED_COSTS[tech] * new_tech_set[tech]
                    if purchase_cost < upfront_cost_ceiling:
                        self.tech_sets.append(new_tech_set)
        print(f"Enumeration took {time.perf_counter() - enumeration_start_time} seconds")
        # while (len(self.tech_sets) < 10000):
        #     tech_set = dict()
        #     purchase_cost = 0
        #     for tech in Technology:
        #         tech_set[tech] = randint(0,upfront_cost_ceiling // FIXED_COSTS[tech])
        #         purchase_cost += FIXED_COSTS[tech] * tech_set[tech]
        #     if purchase_cost < upfront_cost_ceiling:
        #         self.tech_sets.append(tech_set)