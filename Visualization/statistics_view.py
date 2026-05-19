from __future__ import annotations

from typing import Optional, Sequence

import matplotlib.axes
import matplotlib.pyplot as plt

from Utils.statistics_collector import StatisticsCollector


class StatisticsView:
    """Line charts of simulation statistics over rounds in one window."""

    def __init__(
        self,
        collector: StatisticsCollector,
        *,
        threshold: Optional[float] = None,
        title: str = "Simulation statistics by round",
    ) -> None:
        self._collector = collector
        self._threshold = threshold
        self._title = title

    def show(self, *, block: bool = True) -> None:
        ratings = self._collector.loyal_ratings
        if not ratings:
            raise ValueError("no loyal rating samples recorded")

        rounds = range(1, len(ratings) + 1)
        fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
        ax_rating, ax_payoff, ax_deviate = axes

        self._plot_loyal_rating(ax_rating, rounds, ratings)
        self._plot_avg_payoff(ax_payoff, rounds, self._collector.avg_payoffs)
        self._plot_deviates(ax_deviate, rounds, self._collector.deviate_counts)

        ax_deviate.set_xlabel("Round")
        fig.suptitle(self._title)
        fig.tight_layout()
        plt.show(block=block)

    def _plot_loyal_rating(
        self,
        ax: matplotlib.axes.Axes,
        rounds: Sequence[int],
        ratings: Sequence[float],
    ) -> None:
        ax.plot(rounds, ratings, color="#1f77b4", linewidth=1, label="Loyal rating")
        ax.set_ylabel("Loyal rating")
        ax.set_ylim(0.05)
        ax.set_title("Loyal rating")
        ax.grid(True, alpha=0.3)

        if self._threshold is not None:
            ax.axhline(
                self._threshold,
                color="#d62728",
                linestyle="--",
                linewidth=1,
                label=f"threshold ({self._threshold:g})",
            )

        ax.legend(loc="upper right")

    def _plot_avg_payoff(
        self,
        ax: matplotlib.axes.Axes,
        rounds: Sequence[int],
        avg_payoffs: Sequence[float],
    ) -> None:
        ax.plot(
            rounds, avg_payoffs, color="#ff7f0e", linewidth=1,
            label="Avg player payoff",
        )
        ax.set_ylabel("Avg player payoff")
        ax.set_title("Avg payoffs")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right")

    def _plot_deviates(
        self,
        ax: matplotlib.axes.Axes,
        rounds: Sequence[int],
        deviates: Sequence[int],
    ) -> None:
        ax.plot(
            rounds, deviates, color="#2ca02c", linewidth=1,
            label="Deviates per round",
        )
        ax.set_ylabel("Deviates per round")
        ax.set_title("Deviate number")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right")
