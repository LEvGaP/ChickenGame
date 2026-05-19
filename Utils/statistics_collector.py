from __future__ import annotations

from typing import List, Sequence


class StatisticsCollector:
    """Stores per-round statistics recorded during simulation."""

    def __init__(self) -> None:
        self._loyal_ratings: List[float] = []
        self._avg_payoffs: List[float] = []
        self._deviate_counts: List[int] = []

    def record_loyal_rating(self, rating: float) -> None:
        self._loyal_ratings.append(float(rating))

    def record_round_stats(self, avg_payoff: float, deviate_count: int) -> None:
        self._avg_payoffs.append(float(avg_payoff))
        self._deviate_counts.append(int(deviate_count))

    @property
    def loyal_ratings(self) -> Sequence[float]:
        return tuple(self._loyal_ratings)

    @property
    def avg_payoffs(self) -> Sequence[float]:
        return tuple(self._avg_payoffs)

    @property
    def deviate_counts(self) -> Sequence[int]:
        return tuple(self._deviate_counts)

    def clear(self) -> None:
        self._loyal_ratings.clear()
        self._avg_payoffs.clear()
        self._deviate_counts.clear()

    def __len__(self) -> int:
        return len(self._loyal_ratings)
