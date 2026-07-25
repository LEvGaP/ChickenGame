from Mediators.mediators import SequenceMediator
from chicken_game import ChickenGame, RoundHistory
from Players.mixer_player import MixerPlayer
from Players.base_player import BasePlayer
from enum import Enum
from collections import defaultdict
import logging


class PlayerRank(Enum):
    SOPHISTIC = "SOPHISTIC"
    BULLY = "BULLY"
    CHICKEN = "CHICKEN"


class Academy:
    ROOKIE_GROUP = "ROOKIE"
    JUNIOR_GROUP = "JUNIOR"
    EPS = 1e-9

    def __init__(self, students: list[BasePlayer], max_iterations: int):
        self.student_groups: dict[PlayerRank, list[BasePlayer]] = defaultdict(
            list)
        self.student_groups[PlayerRank.CHICKEN] = students
        self.mediator = SequenceMediator(num_players=2)
        self.evaluator = Evaluator(discount=0.99, rounds=100, gingerbread=7,
                                   eps=0.1)
        self.max_iterations = max_iterations

    def run(self):
        for iteration in range(self.max_iterations):
            if len(self.student_groups[PlayerRank.CHICKEN]) < 2 \
                    and len(self.student_groups[PlayerRank.BULLY]) < 2:
                break

            for rank in [PlayerRank.CHICKEN, PlayerRank.BULLY]:
                rank_group = self.student_groups.pop(rank, [])
                new_groups = self.run_study(rank_group, rank)
                for r, g in new_groups.items():
                    self.student_groups[r].extend(g)

            if iteration % 5 == 0:
                logging.info(f'Iteration: {iteration}')
                self.log_groups_stats()

    def run_study(self, study_group: list[BasePlayer],
                  group_rank: PlayerRank) -> dict[
        PlayerRank, list[MixerPlayer]]:
        n = len(study_group)
        first_half = study_group[:(n // 2)]
        second_half = study_group[(n // 2):]

        new_groups = defaultdict(list)
        if len(second_half) > len(first_half):
            skipped_student = second_half.pop()
            new_groups[group_rank].append(skipped_student)

        for p1, p2 in zip(first_half, second_half):
            p1_rank, p2_rank = self.play_episode(p1, p2)
            new_groups[p1_rank].append(p1)
            new_groups[p2_rank].append(p2)

        return new_groups

    def play_episode(self, player1, player2):
        game_controller = ChickenGame(player1, player2, self.mediator)
        game_controller.play_round_series(rounds_count=1000)
        p1_rank = self.evaluator.get_rank(game_controller.p1_history)
        p2_rank = self.evaluator.get_rank(game_controller.p2_history)
        logging.debug(f'Result:'
                      f' {player1.name} - {p1_rank}'
                      f' | {player2.name} - {p2_rank}')

        player_descriptions = zip([player1, player2],
                                  [p1_rank, p2_rank],
                                  [game_controller.p1_history,
                                   game_controller.p2_history])
        for p, r, h in player_descriptions:
            if r == PlayerRank.SOPHISTIC and \
                    h[-1].action != h[-1].recommendation:
                p.swap_strategy()

        return p1_rank, p2_rank

    def log_groups_stats(self):
        for rank, group in self.student_groups.items():
            logging.info(f'Rank: {rank}, player count: {len(group)}')

    def log_each_player(self):
        for rank, group in self.student_groups.items():
            logging.info(f'Rank: {rank}')
            for p in group:
                p.log_parameters()


class Evaluator:
    def __init__(self, discount: float, rounds: int, gingerbread: int,
                 eps: float):
        self.discount = discount
        self.rounds = rounds
        self.gingerbread = gingerbread
        self.eps = eps

    def get_rank(self, player_history: list[RoundHistory]):
        expected_score, actual_score = 0, 0
        for i, h in enumerate(player_history[-self.rounds:]):
            if i % 2 == 0:
                expected_score *= self.discount
                actual_score *= self.discount

            expected_score += self.gingerbread * h.recommendation
            actual_score += self.gingerbread * h.action

        if abs(expected_score - actual_score) < self.eps:
            return PlayerRank.SOPHISTIC

        if actual_score > expected_score:
            return PlayerRank.BULLY

        return PlayerRank.CHICKEN
