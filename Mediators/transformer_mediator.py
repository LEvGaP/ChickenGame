from GameControllers.chicken_game import STAY, SWERVE
import numpy as np
import logging
from Mediators.mediator_base import MediatorBase, MediatorMode
from Utils.statistics_collector import StatisticsCollector
from Utils.softmax_distribution import softmax


class TransformerMediator(MediatorBase):
    def __init__(self, num_players, k=2, threshold=0.5, discount=0.9,
                 stats_discount=0.8,
                 stats_temperature=1.0,
                 statistics_collector: StatisticsCollector = None,
                 random_punishment=False):
        """
        :param num_players: Number of players in the game
        :param k: Number of players recommended to STAY during punishment
        :param threshold: Rating value that triggers/stops punishment
        :param discount: Factor for the global loyal rating (moving average)
        :param stats_discount: Factor for individual player stats (moving average)
        """
        super().__init__()

        self.num_players = num_players
        self.k = min(k, num_players)
        self.threshold = threshold
        self.init_threshold = threshold
        self.discount = discount
        self.stats_discount = stats_discount
        self.stats_temperature = stats_temperature
        self.statistics_collector = statistics_collector

        self.loyal_rating = 0.0

        # Individual Statistics
        # follow_stay_stats: Follows recommendation when signal is STAY (they stayed as told)
        self.follow_stay_stats = np.zeros(num_players)
        # dev_swerve_stats: Deviates when signal is SWERVE (they stayed instead of swerving)
        self.dev_swerve_stats = np.zeros(num_players)

        # State for Punishment Mode
        self.random_punishment = random_punishment
        self.punishment_pool = list(range(num_players))
        np.random.shuffle(self.punishment_pool)
        self.pool_pointer = 0

        self.last_recommendations = []
        logging.info(
            f'Mediator settings: {self.k=} | {self.threshold=} | {self.discount=} | {self.stats_discount=}')

    def get_recommendations(self):
        recommendations = [SWERVE] * self.num_players

        if np.min(self.follow_stay_stats) > 0.75:
            self.threshold = 0.0033
        else:
            self.threshold = self.init_threshold

        if self._mode == MediatorMode.ORDINARY:
            # Mode 1: Select ONE player to STAY.
            # Reward reliability: pick player with the HIGHEST follow_stay score.
            probs = self.ord_mode_player_probs()
            stay_idx = np.random.choice(self.num_players, p=probs)
            recommendations[stay_idx] = STAY

        elif self.random_punishment:
            # Mode 2: Punishment (k players STAY)
            # Select k players from the pool that haven't been punished recently
            for _ in range(self.k):
                # If we've exhausted the pool, reshuffle to ensure non-overlapping
                # groups in consecutive rounds until the cycle is complete
                if self.pool_pointer >= self.num_players:
                    np.random.shuffle(self.punishment_pool)
                    self.pool_pointer = 0

                p_idx = self.punishment_pool[self.pool_pointer]
                recommendations[p_idx] = STAY
                self.pool_pointer += 1
        else:
            # Mode 2: Punishment. Select K players to STAY.
            # Target "greedy" players: pick players with the HIGHEST swerve-deviation score.
            probs = self.punish_mode_player_probs()

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
                # Signal was STAY. "Following" means they actually chose STAY.
                val = 1.0 if act == STAY else 0.0
                self.follow_stay_stats[i] = (self.stats_discount *
                                             self.follow_stay_stats[i]) + \
                                            ((1 - self.stats_discount) * val)
            elif rec == SWERVE:
                # Signal was SWERVE. "Deviation" means they chose STAY.
                val = 1.0 if act == STAY else 0.0
                self.dev_swerve_stats[i] = (self.stats_discount *
                                            self.dev_swerve_stats[i]) + \
                                           ((1 - self.stats_discount) * val)

                # Global disloyalty: count people who ignored the SWERVE signal
                if val == 1.0:
                    deviations_this_round += 1

        # 1. Update global rating (Mean deviation of people told to SWERVE)
        mean_deviation = deviations_this_round / self.num_players
        self.loyal_rating = (self.discount * self.loyal_rating) + \
                            ((1 - self.discount) * mean_deviation)

        if self.statistics_collector is not None:
            self.statistics_collector.record_mediator_stats(
                self.loyal_rating,
                mode=self._mode)

        # 2. Mode Switching Logic
        if self._mode == MediatorMode.ORDINARY:
            if self.loyal_rating > self.threshold:
                logging.info(
                    f'Switch to {MediatorMode.PUNISHMENT}.'
                    f' Rating: {self.loyal_rating:.5f}')
                self._mode = MediatorMode.PUNISHMENT
                # Reset punishment pool logic
                np.random.shuffle(self.punishment_pool)
                self.pool_pointer = 0
        else:
            if self.loyal_rating <= self.threshold:
                logging.info(
                    f'Switch to {MediatorMode.ORDINARY}.'
                    f' Rating: {self.loyal_rating:.5f}')
                self._mode = MediatorMode.ORDINARY

    def __str__(self):
        return (
            f"Mode: {self._mode} | Global Rating: {self.loyal_rating:.4f} | "
            f"Avg Follow-Stay: {np.mean(self.follow_stay_stats):.4f}")

    def ord_mode_player_probs(self):
        return softmax(-self.follow_stay_stats / self.stats_temperature)

    def punish_mode_player_probs(self):
        return softmax(-self.dev_swerve_stats / self.stats_temperature)
