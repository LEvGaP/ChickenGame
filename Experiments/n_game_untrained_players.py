import logging

from Players.players_factory import create_two_faced_mixer_players
from Utils.statistics_collector import StatisticsCollector
from Utils.players_storage_manager import PlayersStorageManager
from Mediators.loyal_punishment_mediator import LoyalPunishmentMediator
from Mediators.rational_mediator import RationalMediator
from n_player_chicken_game import NPlayerChickenGame, get_compute_payoffs
from Visualization import StatisticsView
from pathlib import Path

STORE_PATH = Path('PlayersStorage', 'TwoFacedMixerPlayers50000')
SAVE_PATH = Path('PlayersStorage', 'TwoFacedMixerPlayers100000')

SAVE_FIG_DIR = Path(r'C:\Users\Евгений\Pictures\Защитная неделя')
FILE_SUFFIX = 'RMed_k10_doubleTh.png'
SAVE_FIG_FILE = SAVE_FIG_DIR / FILE_SUFFIX
SAVE_MEDIATOR_FIG_FILE = SAVE_FIG_DIR / ('med_stats_' + FILE_SUFFIX)


def run_rational_mediator(n_players, k):
    # untrained_players = create_two_faced_mixer_players(n_players)
    #
    # for p in untrained_players:
    #     p.update_temperature(factor=0.28)

    storage = PlayersStorageManager(store_path=STORE_PATH)
    untrained_players = storage.load()[:n_players]

    stats_collector = StatisticsCollector()
    threshold = 0.0033
    mediator = RationalMediator(
        num_players=n_players,
        k=k,
        threshold=(0.002, threshold),
        discount=0.9,
        stats_discount=0.9,
        stats_temperature=0.2,
        statistics_collector=stats_collector
    )

    game_controller = NPlayerChickenGame(
        players=untrained_players,
        mediator=mediator,
        payoff_function=get_compute_payoffs(-1),
        statistics_collector=stats_collector
    )

    for i in range(1, 6):
        stats_collector.clear()
        game_controller.play_round_series(10000)

        for p in untrained_players:
            p.log_parameters()

        fig_file_name = f'{i * 10}r_{FILE_SUFFIX}'

        stats_view = StatisticsView(
            collector=stats_collector,
            threshold=threshold
        )

        stats_view.show_mediator_stats(
            seq_mode_player_probs=mediator.ord_mode_player_probs(),
            punish_mode_player_probs=mediator.punish_mode_player_probs(),
            # save_file=SAVE_FIG_DIR / ('medstats_probs_' + fig_file_name)
        )

        stats_view.show_mediator_stats(
            seq_mode_player_probs=mediator.follow_stay_stats,
            punish_mode_player_probs=mediator.dev_swerve_stats,
            # save_file = SAVE_FIG_DIR / ('medstats_' + fig_file_name)
        )

        stats_view.show(
            # save_file=SAVE_FIG_DIR / fig_file_name
        )

    storage = PlayersStorageManager(store_path=SAVE_PATH)
    storage.clear()
    storage.dump_batch(untrained_players)


def run_loyal_mediator(n_players, k):
    # untrained_players = create_two_faced_mixer_players(n_players)
    #
    # for p in untrained_players:
    #     p.update_temperature(factor=0.25)

    storage = PlayersStorageManager(store_path=STORE_PATH)
    untrained_players = storage.load()

    stats_collector = StatisticsCollector()
    threshold = 0.0033
    mediator = LoyalPunishmentMediator(
        num_players=n_players,
        k=k,
        threshold=threshold,
        discount=0.9,
        statistics_collector=stats_collector
    )

    game_controller = NPlayerChickenGame(
        players=untrained_players,
        mediator=mediator,
        payoff_function=get_compute_payoffs(cooperate_payoff=-1),
        statistics_collector=stats_collector
    )

    game_controller.play_round_series(20000)

    storage.clear()
    storage.dump_batch(untrained_players)

    for p in untrained_players:
        p.log_parameters()

    stats_view = StatisticsView(collector=stats_collector, threshold=threshold)
    stats_view.show(
        save_file=SAVE_FIG_FILE
    )
