from chicken_game import STAY, SWERVE
import numpy as np
import logging
from Mediators.mediator_base import MediatorBase


class RationalMediator(MediatorBase):
    def __init__(self, num_players, k=2, threshold=0.5, discount=0.9,
                 stats_discount=0.8):
        """
        :param num_players: Number of players in the game
        :param k: Number of players recommended to STAY during punishment
        :param threshold: Rating value that triggers/stops punishment
        :param discount: Factor for the global loyal rating (moving average)
        :param stats_discount: Factor for individual player stats (moving average)
        """
        self.num_players = num_players
        self.k = min(k, num_players)
        self.threshold = threshold
        self.discount = discount
        self.stats_discount = stats_discount

        self.loyal_rating = 0.0
        self.mode = "SEQUENTIAL"

        # Individual Statistics
        # dev_stay_stats: Deviates when signal is STAY (they swerved instead)
        self.dev_stay_stats = np.zeros(num_players)
        # dev_swerve_stats: Deviates when signal is SWERVE (they stayed instead)
        self.dev_swerve_stats = np.zeros(num_players)

        self.last_recommendations = []
        logging.info(
            f'Mediator settings: {self.k=} | {self.threshold=} | {self.discount=} | {self.stats_discount=}')

    def _softmax(self, x):
        """Compute softmax values for a set of scores."""
        e_x = np.exp(x)
        return e_x / e_x.sum()

    def get_recommendations(self):
        recommendations = [SWERVE] * self.num_players

        if self.mode == "SEQUENTIAL":
            # Mode 1: Select ONE player to STAY.
            # We reward loyalty: pick player with the LOWEST stay-deviation.
            # Use negative stats so low values get high probability.
            probs = self._softmax(-self.dev_stay_stats)
            stay_idx = np.random.choice(self.num_players, p=probs)
            recommendations[stay_idx] = STAY

        else:
            # Mode 2: Punishment. Select K players to STAY.
            # We target "greedy" players: pick players with the HIGHEST swerve-deviation.
            probs = self._softmax(self.dev_swerve_stats)

            # Select k unique players based on the distribution
            punished_indices = np.random.choice(
                self.num_players,
                size=self.k,
                replace=False,
                p=probs
            )

            for idx in punished_indices:
                recommendations[idx] = STAY

        self.last_recommendations = recommendations
        return recommendations

    def update_strategy(self, player_actions):
        """
        Updates individual player stats and global loyal rating.
        """
        deviations_this_round = 0

        for i in range(self.num_players):
            rec = self.last_recommendations[i]
            act = player_actions[i]

            if rec == STAY:
                # Signal was STAY. Deviation = player chose SWERVE
                val = 1.0 if act == SWERVE else 0.0
                self.dev_stay_stats[i] = (self.stats_discount *
                                          self.dev_stay_stats[i]) + \
                                         ((1 - self.stats_discount) * val)

            elif rec == SWERVE:
                # Signal was SWERVE. Deviation = player chose STAY
                val = 1.0 if act == STAY else 0.0
                self.dev_swerve_stats[i] = (self.stats_discount *
                                            self.dev_swerve_stats[i]) + \
                                           ((1 - self.stats_discount) * val)

                # Global disloyalty logic: how many people ignored the "Safe" signal
                if val == 1.0:
                    deviations_this_round += 1

        # 1. Update global rating (Mean deviation of people told to SWERVE)
        mean_deviation = deviations_this_round / self.num_players
        self.loyal_rating = (self.discount * self.loyal_rating) + \
                            ((1 - self.discount) * mean_deviation)

        # 2. Mode Switching Logic
        if self.mode == "SEQUENTIAL":
            if self.loyal_rating > self.threshold:
                logging.info(
                    f'Switch to PUNISHMENT. Rating: {self.loyal_rating:.5f}')
                self.mode = "PUNISHMENT"
        else:
            if self.loyal_rating <= self.threshold:
                logging.info(
                    f'Switch to SEQUENTIAL. Rating: {self.loyal_rating:.5f}')
                self.mode = "SEQUENTIAL"

    def __str__(self):
        return (f"Mode: {self.mode} | Rating: {self.loyal_rating:.4f} | "
                f"Avg Swerve Dev: {np.mean(self.dev_swerve_stats):.4f}")