from Players.base_player import BasePlayer
from chicken_game import ACTIONS
import random


class RandomPlayer(BasePlayer):
    def get_action(self):
        return random.choice(ACTIONS)

    def update(self, my_action, opponent_action, my_payoff):
        self.total_score += my_payoff
