import numpy as np


class UCB:
    def __init__(self, num_arms, num_input_combinations):
        self.ignore_input_combination = True
        self.num_arms = num_arms
        self.num_input_combinations = num_input_combinations
        self.estimated_rewards = np.zeros((num_arms, num_input_combinations))
        self.counters = np.ones((num_arms, num_input_combinations))

    def choose_arm(self, input_combination) -> int:
        if self.ignore_input_combination:
            input_combination = 0

        ucbs = []
        for a in range(self.num_arms):
            ucbs.append(np.sqrt(2 * np.log(np.sum(self.counters)) / self.counters[a][input_combination]) +
                        self.estimated_rewards[a][input_combination])
        print(f"{ucbs=}")
        return np.argmax(ucbs).item()

    def update(self, arm, input_combination, reward):
        if self.ignore_input_combination:
            input_combination = 0

        self.counters[arm][input_combination] += 1
        self.estimated_rewards[arm][input_combination] = (self.estimated_rewards[arm][input_combination] *
                                                          self.counters[arm][input_combination] + reward) / (
                                                                 self.counters[arm][input_combination] + 1)
