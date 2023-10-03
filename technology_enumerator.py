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
        max_tech_num = dict()
        for tech in Technology:
            zero_tech_set[tech] = 0
            max_tech_num[tech] = upfront_cost_ceiling // FIXED_COSTS[tech] # 21
        for tech in Technology:
            single_tech_set = zero_tech_set.copy()
            single_tech_set[tech] = max_tech_num[tech]
            self.tech_sets.append(single_tech_set)
        # max_tech_num = 42 # upfront_cost_ceiling // min([FIXED_COSTS[t] for t in Technology]) # 21
        for h in range(max_tech_num[Technology.STORAGE_ONLY]):
            # if FIXED_COSTS[Technology.STORAGE_ONLY] * h > upfront_cost_ceiling:
            #     continue
            for i in range(max_tech_num[Technology.SOLAR_ONLY]):
                # if FIXED_COSTS[Technology.STORAGE_ONLY] * h + FIXED_COSTS[Technology.SOLAR_ONLY] * i > upfront_cost_ceiling:
                #     continue
                for j in range(max_tech_num[Technology.SOFC]):
                    # if FIXED_COSTS[Technology.STORAGE_ONLY] * h + FIXED_COSTS[Technology.SOLAR_ONLY] * i + FIXED_COSTS[Technology.SOFC] * j > upfront_cost_ceiling:
                    #     continue
                    for k in range(max_tech_num[Technology.DIESEL]):
                        new_tech_set = zero_tech_set.copy()
                        new_tech_set[Technology.STORAGE_ONLY] = h
                        new_tech_set[Technology.SOLAR_ONLY] = i
                        new_tech_set[Technology.SOFC] = j
                        new_tech_set[Technology.DIESEL] = k
                        
                        purchase_cost = 0
                        for tech in Technology:
                            purchase_cost += FIXED_COSTS[tech] * new_tech_set[tech]
                        if purchase_cost < upfront_cost_ceiling:
                            self.tech_sets.append(new_tech_set)
                        else:
                            break
        print(f"Enumeration took {time.perf_counter() - enumeration_start_time} seconds")
        # while (len(self.tech_sets) < 10000):
        #     tech_set = dict()
        #     purchase_cost = 0
        #     for tech in Technology:
        #         tech_set[tech] = randint(0,upfront_cost_ceiling // FIXED_COSTS[tech])
        #         purchase_cost += FIXED_COSTS[tech] * tech_set[tech]
        #     if purchase_cost < upfront_cost_ceiling:
        #         self.tech_sets.append(tech_set)