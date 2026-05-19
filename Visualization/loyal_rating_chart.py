from __future__ import annotations

from typing import Optional

import matplotlib.pyplot as plt

from Utils.statistics_collector import StatisticsCollector


class LoyalRatingChartView:
    """Line chart of loyal (disloyalty) rating over rounds."""

    def __init__(
        self,
        collector: StatisticsCollector,
        *,
        threshold: Optional[float] = None,
        title: str = "Loyal rating by round",
    ) -> None:
        self._collector = collector
        self._threshold = threshold
        self._title = title

    def show(self, *, block: bool = True) -> None:
        ratings = self._collector.loyal_ratings
        if not ratings:
            raise ValueError("no loyal rating samples recorded")

        rounds = range(1, len(ratings) + 1)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(rounds, ratings, color="#1f77b4", linewidth=1)
        if self._threshold is not None:
            ax.axhline(
                self._threshold,
                color="#d62728",
                linestyle="--",
                linewidth=1,
                label=f"threshold ({self._threshold:g})",
            )
            ax.legend(loc="upper right")
        ax.set_xlabel("Round")
        ax.set_ylabel("Loyal rating")
        ax.set_ylim(0.05)
        ax.set_title(self._title)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        plt.show(block=block)
