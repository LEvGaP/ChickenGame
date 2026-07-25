import logging

from Players.players_factory import create_two_faced_mixer_players
from Utils.statistics_collector import StatisticsCollector
from Utils.players_storage_manager import PlayersStorageManager
from Mediators.rational_mediator import RationalMediator
from n_player_chicken_game import NPlayerChickenGame, get_compute_payoffs
from Visualization import StatisticsView
from pathlib import Path

STORE_PATH = Path('PlayersStorage', 'TwoFacedMixerPlayers10000')
SAVE_PATH = Path('PlayersStorage', 'TwoFacedMixerPlayers150000')

FOLDER_NAME = 'RMed_k10_t028_dTH_100r(4)'
SAVE_FIG_DIR = Path(r'C:\Users\Евгений\Pictures\Защитная неделя') / FOLDER_NAME
SAVE_FIG_DIR.mkdir()


def run_rational_mediator(n_players, k):
    untrained_players = create_two_faced_mixer_players(n_players)

    for p in untrained_players:
        p.update_temperature(factor=0.28)

    storage = PlayersStorageManager(store_path=STORE_PATH)
    # untrained_players = storage.load()[:n_players]

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

    for i in range(1, 10):
        stats_collector.clear()
        game_controller.play_round_series(10000)

        rounds = 10000
        faults = stats_collector.get_players_faults_in_last_rounds(rounds)
        ord_faults = \
            stats_collector.get_players_ordinary_faults_in_last_rounds(rounds)
        payoff = stats_collector.get_players_total_payoff_in_last_rounds(rounds)
        ord_payoff = \
            stats_collector.get_players_ordinary_total_payoff_in_last_rounds(
                rounds)
        sys_payoff = \
            stats_collector.get_total_system_payoff_in_last_rounds(rounds)
        ord_sys_payoff = \
            stats_collector.get_ordinary_total_system_payoff_in_last_rounds(
                rounds)
        logging.info(f'\n|  STATS  |   ORD   |   ALL   |\n'
                     f'-------------------------------\n'
                     f'| Faults  | {ord_faults:.2f} | {faults:.2f}\n'
                     f'| Payoff  | {ord_payoff:.2f} | {payoff:.2f}\n'
                     f'| Sys Pay | {ord_sys_payoff:.2f} | {sys_payoff:.2f}')

        fig_file_name = f'{i * 10}r.png'

        stats_view = StatisticsView(
            collector=stats_collector,
            threshold=threshold
        )

        # stats_view.show_mediator_stats(
        #     seq_mode_player_probs=
        #     stats_collector.get_payoffs_by_players_in_last_ordinary_rounds(
        #         rounds),
        #     punish_mode_player_probs=
        #     stats_collector.get_payoffs_by_players_in_last_rounds(rounds),
        #     title="Players avg payoffs",
        #     save_file=SAVE_FIG_DIR / ('payoffs_stats_' + fig_file_name)
        # )
        #
        # stats_view.show_mediator_stats(
        #     seq_mode_player_probs=mediator.ord_mode_player_probs(),
        #     punish_mode_player_probs=mediator.punish_mode_player_probs(),
        #     title="Mediator players probs",
        #     save_file=SAVE_FIG_DIR / ('medstats_probs_' + fig_file_name)
        # )
        #
        stats_view.show_mediator_stats(
            seq_mode_player_probs=mediator.follow_stay_stats,
            punish_mode_player_probs=mediator.dev_swerve_stats,
            title="Mediator players stats",
            save_file = SAVE_FIG_DIR / ('medstats_' + fig_file_name)
        )

        stats_view.show(
            save_file=SAVE_FIG_DIR / fig_file_name
        )

    storage = PlayersStorageManager(store_path=SAVE_PATH)
    storage.clear()
    storage.dump_batch(untrained_players)
