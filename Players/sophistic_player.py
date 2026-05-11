from Players.base_player import BasePlayer
import logging


class SophisticPlayer(BasePlayer):
    def get_action(self, signal=0):
        return signal

    def update(self, my_action, opponent_action, my_payoff):
        self.total_score += my_payoff

    def swap_strategy(self):
        pass

    def update_temperature(self, factor):
        pass

    def log_parameters(self):
        logging.info(f'SophisticPlayer: {self.name}')