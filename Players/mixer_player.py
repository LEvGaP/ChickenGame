from Players.base_player import BasePlayer
import numpy as np
import logging


class MixerPlayer(BasePlayer):
    """
    Meta‑player that selects among several sub‑players based on a mediator signal.
    The selection probabilities are learned via reinforcement learning.
    """

    def __init__(self, name, players: list[BasePlayer], learning_rate=0.1,
                 temperature=0.5,
                 log=False):
        super().__init__(name)
        self.players = players                      # list of BasePlayer instances
        self.learning_rate = learning_rate
        self.temperature = temperature
        # weights[signal] = numpy array of weights for each sub‑player
        self.weights = np.zeros((2, len(self.players)))
        self.last_signal = None
        self.last_selected_idx = None
        self.last_selected_player = None

        self.log = log

    def get_action(self, recommendation=0):
        """
        Select a sub‑player according to the recommendation (signal),
        then return the action chosen by that sub‑player.
        """

        w = self.weights[recommendation]
        # Softmax over weights to obtain selection probabilities
        exp_w = np.exp(w / self.temperature)
        probs = exp_w / np.sum(exp_w)
        selected_idx = np.random.choice(len(self.players), p=probs)

        self.last_signal = recommendation
        self.last_selected_idx = selected_idx
        self.last_selected_player = self.players[selected_idx]

        # Let the chosen sub‑player decide its action
        action = self.last_selected_player.get_action()
        return action

    def update(self, my_action, opponent_action, my_payoff):
        """
        Update the chosen sub‑player and the mixer's own weights.
        """
        # 1. Update the selected sub‑player
        self.last_selected_player.update(my_action, opponent_action, my_payoff)
        self.total_score += my_payoff

        # 2. Update the weight for the (signal, selected player) pair
        w = self.weights[self.last_signal][self.last_selected_idx]
        new_w = w + self.learning_rate * (my_payoff - w)
        self.weights[self.last_signal][self.last_selected_idx] = new_w

        if self.log:
            logging.info(f'Action: {my_action} | Payoff: {my_payoff}'
                          f' | Signal: {self.last_signal}')
            self.log_parameters()

    def log_parameters(self):
        """Print current weight vectors for all seen signals."""

        str_weights = []
        for w_list in self.weights:
            str_weights.append(', '.join(str(round(w, 2)) for w in w_list))

        logging.info(f"{self.name} | "
                     f"Weights: [{str_weights[0]}] [{str_weights[1]}] | "
                     f"T: {self.temperature}")
        for p in self.players:
            p.log_parameters()

    def swap_strategy(self):
        self.weights[0], self.weights[1] = self.weights[1], self.weights[0]

    def update_temperature(self, factor):
        self.temperature *= factor
        for p in self.players:
            p.update_temperature(factor)
