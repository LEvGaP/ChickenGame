from __future__ import annotations
from Mediators.mediator_base import MediatorMode

from typing import List, Sequence
import numpy as np


class StatisticsCollector:
    """Stores per-round statistics recorded during simulation."""

    def __init__(self) -> None:
        self._loyal_ratings: List[float] = []
        self._avg_payoffs: List[float] = []
        self._deviate_counts: List[int] = []
        self._dev_stay_counts: List[int] = []
        self._mediator_modes: List[MediatorMode] = []
        self._total_payoffs: List[float] = []
        self._payoffs_by_players: List[List[float]] = []

    def record_mediator_stats(self, rating: float,
                              mode: MediatorMode = MediatorMode.ORDINARY)\
            -> None:
        self._loyal_ratings.append(float(rating))
        self._mediator_modes.append(mode)

    def record_round_stats(self,
                           payoffs: List[float],
                           deviate_count: int,
                           dev_stay_count: int) -> None:
        total_payoff = sum(payoffs)
        avg_payoff = total_payoff / len(payoffs)
        self._avg_payoffs.append(float(avg_payoff))
        self._deviate_counts.append(int(deviate_count))
        self._dev_stay_counts.append(int(dev_stay_count))
        self._total_payoffs.append(float(total_payoff))
        self._payoffs_by_players.append(payoffs)

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

    def get_players_faults_in_last_rounds(self, rounds: int) -> float:
        faults_count = sum(self._dev_stay_counts[-rounds:])
        return faults_count / rounds

    def get_players_ordinary_faults_in_last_rounds(self, rounds: int) -> float:
        mode_and_count_by_rounds = zip(self._mediator_modes[-rounds:],
                                       self._dev_stay_counts[-rounds:])
        faults_count = 0
        rounds_count = 0
        for (mode, count) in mode_and_count_by_rounds:
            if mode != MediatorMode.ORDINARY:
                continue
            faults_count += count
            rounds_count += 1

        return faults_count / rounds_count

    def get_players_total_payoff_in_last_rounds(self, rounds: int) -> float:
        return sum(self._total_payoffs[-rounds:]) / rounds

    def get_players_ordinary_total_payoff_in_last_rounds(
            self, rounds: int) -> float:
        mode_and_payoff_by_rounds = zip(self._mediator_modes[-rounds:],
                                        self._total_payoffs[-rounds:])

        total_payoff = 0
        rounds_count = 0
        for (mode, payoff) in mode_and_payoff_by_rounds:
            if mode != MediatorMode.ORDINARY:
                continue
            total_payoff += payoff
            rounds_count += 1

        return total_payoff / rounds_count

    def get_total_system_payoff_in_last_rounds(self, rounds: int) -> float:
        payoff_by_players = np.array(self._payoffs_by_players[-rounds:])
        return np.pow(2, payoff_by_players).sum() / rounds

    def get_ordinary_total_system_payoff_in_last_rounds(self, rounds: int) -> float:
        mode_and_payoff_by_rounds = zip(self._mediator_modes[-rounds:],
                                        self._payoffs_by_players[-rounds:])

        ord_payoffs_by_players = []
        rounds_count = 0
        for (mode, payoff) in mode_and_payoff_by_rounds:
            if mode != MediatorMode.ORDINARY:
                continue
            ord_payoffs_by_players.append(payoff)
            rounds_count += 1

        payoff_by_players = np.array(ord_payoffs_by_players)
        return np.pow(2, payoff_by_players).sum() / rounds_count


    def get_payoffs_by_players_in_last_rounds(self, rounds: int) -> np.ndarray:
        result = np.sum(self._payoffs_by_players[-rounds:], axis=0) / rounds
        return result

    def get_payoffs_by_players_in_last_ordinary_rounds(
            self, rounds: int) -> np.ndarray:
        mediator_modes = np.array(self._mediator_modes[-rounds:])
        payoffs_by_players = np.array(self._payoffs_by_players[-rounds:])
        ord_rounds_mask = mediator_modes == MediatorMode.ORDINARY
        result = \
            np.sum(payoffs_by_players[ord_rounds_mask], axis=0)\
            / np.sum(ord_rounds_mask)
        return result

    def clear(self) -> None:
        self._loyal_ratings.clear()
        self._avg_payoffs.clear()
        self._deviate_counts.clear()
        self._dev_stay_counts.clear()
        self._mediator_modes.clear()
        self._total_payoffs.clear()
        self._payoffs_by_players.clear()

    def __len__(self) -> int:
        return len(self._loyal_ratings)
