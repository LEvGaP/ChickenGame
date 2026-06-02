from __future__ import annotations

from typing import Optional

from chicken_game import STAY, SWERVE
import numpy as np
import logging

from Utils.statistics_collector import StatisticsCollector

from Mediators.mediator_base import MediatorBase, MediatorMode


class LoyalPunishmentMediator(MediatorBase):
    def __init__(
        self,
        num_players,
        k=2,
        threshold=0.5,
        discount=0.9,
        statistics_collector: Optional[StatisticsCollector] = None,
    ):
        """
        :param num_players: Number of players in the game
        :param k: Number of players recommended to STAY during punishment
        :param threshold: Rating value that triggers/stops punishment
        :param discount: Factor for the moving average (0 to 1)
        """
        super().__init__()
        self.num_players = num_players
        self.k = min(k, num_players)
        self.threshold = threshold
        self.discount = discount
        self.statistics_collector = statistics_collector

        self.loyal_rating = 0.0

        # State for Sequential Mode
        self.stay_index = num_players - 1

        # State for Punishment Mode
        self.punishment_pool = list(range(num_players))
        np.random.shuffle(self.punishment_pool)
        self.pool_pointer = 0

        self.last_recommendations = []

        logging.info(f'Mediator settings: {self.k=} | {self.threshold=} | {self.discount=}')

    def get_recommendations(self):
        recommendations = [SWERVE] * self.num_players

        if self.mode == MediatorMode.ORDINARY:
            # Mode 1: Sequential single STAY
            self.stay_index = (self.stay_index + 1) % self.num_players
            recommendations[self.stay_index] = STAY

        else:
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

        self.last_recommendations = recommendations
        return recommendations

    def update_strategy(self, player_actions):
        """
        :param player_actions: List of actions actually taken by players
        """
        # 1. Calculate statistics: Mean number of players who deviated
        # Deviation = Recommended SWERVE (0) but chose STAY (1)
        deviations = 0
        for rec, act in zip(self.last_recommendations, player_actions):
            if rec == SWERVE and act == STAY:
                deviations += 1

        mean_deviation = deviations / self.num_players

        # 2. Update loyal rating using discount parameter (Moving Average)
        # Note: According to specification, high rating = punishment trigger.
        # This means the rating tracks "disloyalty".
        self.loyal_rating = (self.discount * self.loyal_rating) + \
                    ((1 - self.discount) * mean_deviation)

        if self.statistics_collector is not None:
            self.statistics_collector.record_mediator_stats(
                self.loyal_rating, mode=self._mode)

        # 3. Handle Mode Switching
        if self.mode == MediatorMode.ORDINARY:
            if self.loyal_rating > self.threshold:
                self._mode = MediatorMode.PUNISHMENT
                # Reset punishment pool logic
                np.random.shuffle(self.punishment_pool)
                self.pool_pointer = 0
        else:
            # Currently in punishment
            if self.loyal_rating <= self.threshold:
                self._mode = MediatorMode.ORDINARY

    def __str__(self):
        return f"Mode: {self.mode} | Rating: {self.loyal_rating:.5f}"
