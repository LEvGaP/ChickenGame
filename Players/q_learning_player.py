from Players.base_player import BasePlayer
from GameControllers.chicken_game import SWERVE, STAY, ACTIONS
import numpy as np
import random
import logging


rng = np.random.default_rng()


class QLearningPlayer(BasePlayer):
    def __init__(self, name, learning_rate=0.1, temperature=0.5):
        super().__init__(name)
        self.learning_rate = learning_rate
        self.temperature = temperature  # Controls exploration (higher = more random)
        # Initialize internal values (Q-values) for each action
        self.q_values = rng.uniform(-1, 1, size=2)
        self.last_action = None

    def get_action(self, recommendation=0):
        """Selects action using Softmax distribution based on Q-values."""
        # Calculate probabilities: P(a) = exp(Q(a)/T) / sum(exp(Q/T))
        exp_q = np.exp(self.q_values / self.temperature)
        probs = exp_q / np.sum(exp_q)

        self.last_action = np.random.choice([SWERVE, STAY], p=probs)
        return int(self.last_action)

    def update(self, my_action, opponent_action, my_payoff):
        """Updates the internal value of the action taken based on the payoff received."""
        self.total_score += my_payoff
        if self.last_action is not None:
            # Simple reinforcement learning update rule:
            # NewValue = OldValue + LearningRate * (Payoff - OldValue)
            self.q_values[self.last_action] += self.learning_rate * \
                        (my_payoff - self.q_values[self.last_action])

    def swap_strategy(self):
        pass

    def update_temperature(self, factor):
        self.temperature *= factor

    def log_parameters(self):
        str_weights = ', '.join(str(round(w, 2)) for w in self.q_values)
        logging.info(f"{self.name} | "
                     f"Weights: [{str_weights}] | "
                     f"T: {self.temperature}")


class EpsGreedyQLearningPlayer(BasePlayer):
    def __init__(self, name, learning_rate=0.1, epsilon=0.1):
        super().__init__(name)
        self.lr = learning_rate
        self.epsilon = epsilon # Probability of picking a random action
        self.q_values = {SWERVE: 0.0, STAY: 0.0}
        self.last_action = None

    def get_action(self, recommendation=0):
        # Epsilon-greedy exploration
        if random.random() < self.epsilon:
            self.last_action = random.choice(ACTIONS)
        else:
            self.last_action = max(self.q_values, key=self.q_values.get)
        return self.last_action

    def update(self, my_action, opponent_action, my_payoff):
        self.total_score += my_payoff
        # Update Q-value: Q = Q + LR * (Reward - Q)
        self.q_values[my_action] += self.lr * (my_payoff - self.q_values[my_action])

    def display_parameters(self):
        print(f"{self.name}: {self.q_values=}")


class QLearningPlayerV2(BasePlayer):
    def __init__(self, name, learning_rate=0.1, temperature=0.5):
        super().__init__(name)
        self.learning_rate = learning_rate
        self.temperature = temperature
        self.q_values = np.array([[0.0 for _ in ACTIONS] for _ in ACTIONS])
        self.last_action = None
        self.last_signal = None

    def get_action(self, signal=0):
        """Selects action using Softmax distribution based on Q-values."""
        # Calculate probabilities: P(a) = exp(Q(a)/T) / sum(exp(Q/T))
        exp_q = np.exp(self.q_values[signal] / self.temperature)
        probs = exp_q / np.sum(exp_q)

        self.last_signal = signal
        self.last_action = np.random.choice([SWERVE, STAY], p=probs)
        return self.last_action

    def update(self, my_action, opponent_action, my_payoff):
        """Updates the internal value of the action taken based on the payoff received."""
        self.total_score += my_payoff
        if self.last_action is not None:
            q_values = self.q_values[self.last_signal]
            # Simple reinforcement learning update rule:
            # NewValue = OldValue + LearningRate * (Payoff - OldValue)
            q_values[self.last_action] += self.learning_rate * \
                        (my_payoff - q_values[self.last_action])

    def display_parameters(self):
        print(f"{self.name}: {self.q_values=}")
