from __future__ import annotations

from typing import List, Sequence


class StatisticsCollector:
    """Stores loyal rating values recorded after each mediator update."""

    def __init__(self) -> None:
        self._loyal_ratings: List[float] = []

    def record_loyal_rating(self, rating: float) -> None:
        self._loyal_ratings.append(float(rating))

    @property
    def loyal_ratings(self) -> Sequence[float]:
        return tuple(self._loyal_ratings)

    def clear(self) -> None:
        self._loyal_ratings.clear()

    def __len__(self) -> int:
        return len(self._loyal_ratings)
