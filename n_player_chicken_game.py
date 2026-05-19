import dataclasses
from typing import List, Callable, Optional
from Players.base_player import BasePlayer
from Mediators.mediator_base import MediatorBase
from Utils.statistics_collector import StatisticsCollector
import numpy as np
import logging

SWERVE = 0
STAY = 1
ACTIONS = [SWERVE, STAY]


@dataclasses.dataclass
class RoundHistory:
    action: int
    recommendation: int


def compute_payoffs(actions: List[int]) -> List[float]:
    """
    Compute payoffs for an n-player chicken game.
    actions: list where each element is SWERVE (0) or STAY (1)
    Returns: list of payoffs, one per player, in the same order.
    """
    n = len(actions)
    k = sum(actions)  # STAY = 1, so sum gives count of stayers

    swerve_payoff = n - np.log2(k + 1)
    stay_payoff = np.log2(n) - np.log2(k + 1) + (n - 2 * k + 2)

    swerve_payoff -= n
    stay_payoff -= n

    payoffs = [stay_payoff if a == STAY else swerve_payoff
               for a in actions]
    return payoffs


class NPlayerChickenGame:
    def __init__(self,
                 players: List[BasePlayer],
                 mediator: MediatorBase,
                 payoff_function: Callable = compute_payoffs,
                 statistics_collector: Optional[StatisticsCollector] = None):
        self.players = players
        self.n = len(players)
        self.mediator = mediator
        self.payoff_function = payoff_function
        self.statistics_collector = statistics_collector

        logging.info(f'Players number: {self.n}')

    def play_round(self, log=False):
        # 1. Get recommendations for all players
        recommendations = self.mediator.get_recommendations()  # length n

        # 2. Collect actions
        actions = []
        for i, player in enumerate(self.players):
            action = player.get_action(recommendations[i])
            actions.append(action)

        # 3. Compute payoffs using the separate function
        payoffs = self.payoff_function(actions)

        # 4. Update each player with the result
        for i, player in enumerate(self.players):
            # Pass the player's own action, the full action profile, and payoff
            player.update(my_action=actions[i],
                          opponent_action=actions,
                          my_payoff=payoffs[i])

        self.mediator.update_strategy(actions)

        deviated = sum(1 for i in range(self.n)
                       if actions[i] != recommendations[i])
        if self.statistics_collector is not None:
            self.statistics_collector.record_round_stats(
                avg_payoff=sum(payoffs) / self.n,
                deviate_count=deviated,
            )
        if log:
            logging.info(f'Max payoff: {max(payoffs):.4f}'
                         f' | Min payoff: {min(payoffs):.4f}\n'
                         f'Number of deviated: {deviated}'
                         )

        return actions, payoffs, recommendations

    def play_round_series(self, rounds):
        logging.info('Start round series')

        for _ in range(max(0, rounds - 100)):
            self.play_round()

        for i in range(min(rounds, 100)):
            r = i
            if rounds > 100:
                r += rounds - 100
            logging.info(f"Round: {r}")
            self.play_round(log=True)

        logging.info('Finish round series')
