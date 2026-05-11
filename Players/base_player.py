from abc import ABC, abstractmethod


class BasePlayer(ABC):
    def __init__(self, name):
        self.name = name
        self.total_score = 0

    @abstractmethod
    def get_action(self, recommendation=0):
        """
        Must return SWERVE (0) or STAY (1).
        This is where the strategy logic lives.
        """
        pass

    @abstractmethod
    def update(self, my_action, opponent_action, my_payoff):
        """
        This is called after every round.
        Use this to update internal state, memory, or learning weights.
        """
        pass

    @abstractmethod
    def log_parameters(self):
        pass

    @abstractmethod
    def swap_strategy(self):
        pass

    @abstractmethod
    def update_temperature(self, factor):
        pass
