import logging

from Utils.players_storage_manager import PlayersStorageManager
from Utils.statistics_collector import StatisticsCollector
from pathlib import Path
from Visualization.statistics_view import StatisticsView
from Mediators.rational_mediator import RationalMediator
from n_player_chicken_game import NPlayerChickenGame, get_compute_payoffs

STORE_PATH = Path('PlayersStorage', 'TwoFacedMixerPlayers')
# SAVE_PATH = Path('PlayersStorage', 'TwoFacedMixerPlayers25000')
SAVE_PATH = None


SAVE_FIG_DIR = Path(r'C:\Users\Евгений\Pictures\Эксперименты с дет садом')
FILE_SUFFIX = 'Rmed_-1_th.png'


def run(n_players, k):
    storage_manager = PlayersStorageManager(
        store_path=STORE_PATH)

    players = storage_manager.load()[:n_players]
    for p in players:
        p.update_temperature(factor=0.25)

    threshold = 0.005
    stats_collector = StatisticsCollector()
    mediator = RationalMediator(
        num_players=n_players,
        k=k,
        threshold=threshold,
        discount=0.9,
        stats_discount=0.9,
        stats_temperature=0.2,
        statistics_collector=stats_collector,
    )

    game_controller = NPlayerChickenGame(
        players,
        mediator,
        statistics_collector=stats_collector,
        payoff_function=get_compute_payoffs(-1)
    )

    stats_view = StatisticsView(collector=stats_collector, threshold=threshold)

    for i in range(1, 6):
        stats_collector.clear()
        game_controller.play_round_series(10000)

        for p in players:
            p.log_parameters()

        fig_file_name = f'{i * 10}r_{FILE_SUFFIX}'

        stats_view.show_mediator_stats(
            seq_mode_player_probs=mediator.ord_mode_player_probs(),
            punish_mode_player_probs=mediator.punish_mode_player_probs(),
            save_file=SAVE_FIG_DIR / ('medstats_' + fig_file_name)
        )

        stats_view.show(
            save_file=SAVE_FIG_DIR / fig_file_name
        )

    if SAVE_PATH is not None:
        storage_manager = PlayersStorageManager(store_path=SAVE_PATH,
                                                clear=True)
        storage_manager.dump_batch(players)
