import dataclasses
from typing import List, Callable, Union, Any
from Players.base_player import BasePlayer
from mediators import PunishingMediatorV2
import numpy as np
import logging

SWERVE = 0
STAY = 1
ACTIONS = [SWERVE, STAY]


@dataclasses.dataclass
class RoundHistory:
    action: Union[SWERVE, STAY]
    recommendation: Union[SWERVE, STAY]


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
                 mediator: PunishingMediatorV2,
                 payoff_function: Callable = compute_payoffs):
        self.players = players
        self.n = len(players)
        self.mediator = mediator
        self.payoff_function = payoff_function

        self.history: List[List[RoundHistory]] = [[] for _ in range(self.n)]

        logging.info(f'Players number: {self.n}')

    def play_round(self, log=False):
        # 1. Get recommendations for all players
        recommendations = self.mediator.get_recommendations()  # length n

        # 2. Collect actions
        actions = []
        for i, player in enumerate(self.players):
            action = player.get_action(recommendations[i])
            actions.append(action)
            # Record history
            self.history[i].append(RoundHistory(action, recommendations[i]))

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
        if log:
            logging.info(f'Max payoff: {max(payoffs):.4f}'
                         f' | Min payoff: {min(payoffs):.4f}\n'
                         f'Number of deviated: {deviated}'
                         )

        return actions, payoffs, recommendations

    def play_round_series(self, rounds):
        self.history = [[] for _ in range(self.n)]
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

    def get_history(self, player_index: int) -> List[RoundHistory]:
        """Return history for a specific player."""
        return self.history[player_index]

    def log_history_stats(self, player_index):
        player_history = self.history[player_index]
        unfollow_by_action = [0] * 2
        follow_by_action = [0] * 2
        for h in player_history:
            if h.action != h.recommendation:
                unfollow_by_action[h.action] += 1
            else:
                follow_by_action[h.action] += 1

        logging.info(f'Player {player_index}'
                     f' history statistics: {unfollow_by_action=},'
                     f' {follow_by_action=}')

    def log_unfollowed_players(self, last_rounds=5000, threshold=5):
        for i in range(self.n):
            history = self.history[i][-last_rounds:]
            unfollowed_by_action = [0] * 2
            for rh in history:
                if rh.action != rh.recommendation:
                    unfollowed_by_action[rh.action] += 1

            if sum(unfollowed_by_action) > threshold:
                player = self.players[i]
                logging.info(f'{player.name}: {unfollowed_by_action=}')
                player.log_parameters()