from __future__ import annotations

from typing import Optional, Sequence

import matplotlib.axes
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
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

    def show(self, save_file=None, show=False) -> None:
        ratings = self._collector.loyal_ratings
        if not ratings:
            raise ValueError("no loyal rating samples recorded")

        rounds = range(1, len(ratings) + 1)
        fig, axes = plt.subplots(nrows=4, ncols=1, figsize=(10, 10),
                                 sharex=True)
        # ax_rating, ax_payoff, ax_deviate = (axes[i][0] for i in range(3))
        # ax_faults, ax_ord_faults = axes[0][1], axes[1][1]
        ax_rating, ax_payoff, ax_deviate, ax_faults = axes

        self._plot_loyal_rating(ax_rating, rounds, ratings)
        self._plot_avg_payoff(ax_payoff, rounds, self._collector.avg_payoffs)
        self._plot_deviates(ax_deviate, rounds, self._collector.deviate_counts)
        self._plot_players_faults(ax_faults, rounds)

        ax_deviate.set_xlabel("Round")
        fig.suptitle(self._title)
        fig.tight_layout()

        if save_file is not None:
            plt.savefig(save_file)

        if show:
            plt.show()
        plt.close()

    def _plot_loyal_rating(
            self,
            ax: matplotlib.axes.Axes,
            rounds: Sequence[int],
            ratings: Sequence[float],
    ) -> None:
        ax.plot(rounds, ratings, color="#1f77b4", linewidth=1,
                label="Loyal rating")
        ax.set_ylabel("Loyal rating")
        ax.set_ylim(top=0.02)
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
        ax.set_ylim(bottom=-6)
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
        ax.set_ylim(top=20)
        ax.set_title("Deviate number")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right")

    def _plot_players_faults(
            self,
            ax: matplotlib.axes.Axes,
            rounds: Sequence[int]
    ):
        ax.plot(
            rounds, self._collector.players_faults,
            linewidth=1,
            label="faults"
        )
        ax.plot(
            rounds, self._collector.players_ordinary_faults,
            linewidth=1,
            label="ordinary faults"
        )
        ax.set_ylabel("Players faults")
        ax.set_title("Players faults mean by last 1000 rounds")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right")

    @staticmethod
    def show_mediator_stats(seq_mode_player_probs: np.ndarray,
                            punish_mode_player_probs: np.ndarray,
                            title: str,
                            save_file=None,
                            show=False):
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 10))

        def plot_distribution(ax, player_probs, title):
            ax.hist(player_probs, bins='auto')
            ax.set_title(title)
            ax.set_xlabel('Value')
            ax.set_ylabel('Frequency')

        plot_distribution(axes[0], seq_mode_player_probs,
                          'Ordinary mode probs distribution')
        plot_distribution(axes[1], punish_mode_player_probs,
                          'Punishment mode probs distribution')

        fig.suptitle(title)
        plt.tight_layout()

        if save_file is not None:
            plt.savefig(save_file)

        if show:
            plt.show()
        plt.close()
