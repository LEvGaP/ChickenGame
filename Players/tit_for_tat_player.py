from Players.base_player import BasePlayer
from chicken_game import SWERVE


class TitForTatPlayer(BasePlayer):
    def __init__(self, name):
        super().__init__(name)
        self.opponent_last_move = SWERVE # Start peaceful

    def get_action(self):
        return self.opponent_last_move

    def update(self, my_action, opponent_action, my_payoff):
        self.total_score += my_payoff
        self.opponent_last_move = opponent_action
