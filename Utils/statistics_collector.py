from __future__ import annotations
from Mediators.mediator_base import MediatorMode

from typing import List, Sequence


class StatisticsCollector:
    """Stores per-round statistics recorded during simulation."""

    def __init__(self) -> None:
        self._loyal_ratings: List[float] = []
        self._avg_payoffs: List[float] = []
        self._deviate_counts: List[int] = []
        self._dev_stay_counts: List[int] = []
        self._mediator_modes: List[MediatorMode] = []

    def record_mediator_stats(self, rating: float,
                              mode: MediatorMode = MediatorMode.ORDINARY)\
            -> None:
        self._loyal_ratings.append(float(rating))
        self._mediator_modes.append(mode)

    def record_round_stats(self,
                           avg_payoff: float,
                           deviate_count: int,
                           dev_stay_count: int) -> None:
        self._avg_payoffs.append(float(avg_payoff))
        self._deviate_counts.append(int(deviate_count))
        self._dev_stay_counts.append(int(dev_stay_count))

    @property
    def loyal_ratings(self) -> Sequence[float]:
        return tuple(self._loyal_ratings)

    @property
    def avg_payoffs(self) -> Sequence[float]:
        return tuple(self._avg_payoffs)

    @property
    def deviate_counts(self) -> Sequence[int]:
        return tuple(self._deviate_counts)

    @property
    def players_faults(self) -> List[float]:
        n = len(self._dev_stay_counts)
        faults: List[float] = [0] * n
        window_sum = 0
        window_len = 1000
        for i, count in enumerate(self._dev_stay_counts):
            window_sum += count
            if i + 1 >= window_len:
                faults[i] = window_sum / window_len
                window_sum -= self._dev_stay_counts[i + 1 - window_len]

        return faults

    @property
    def players_ordinary_faults(self) -> List[float]:
        n = len(self._dev_stay_counts)
        ordinary_faults: List[float] = [0] * n
        window_sum = 0
        window_len = 1000
        mode_and_count_by_rounds = zip(self._mediator_modes,
                                       self._dev_stay_counts)
        for i, (mode, count) in enumerate(mode_and_count_by_rounds):
            if mode == MediatorMode.ORDINARY:
                window_sum += count

            if i + 1 < window_len:
                continue

            ordinary_faults[i] = window_sum / window_len
            head_pos = i + 1 - window_len
            if self._mediator_modes[head_pos] == MediatorMode.ORDINARY:
                window_sum -= self._dev_stay_counts[head_pos]

        return ordinary_faults

    def clear(self) -> None:
        self._loyal_ratings.clear()
        self._avg_payoffs.clear()
        self._deviate_counts.clear()
        self._dev_stay_counts.clear()
        self._mediator_modes.clear()

    def __len__(self) -> int:
        return len(self._loyal_ratings)
