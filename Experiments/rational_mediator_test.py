import logging

from Utils.players_storage_manager import PlayersStorageManager
from Utils.statistics_collector import StatisticsCollector
from pathlib import Path
from Visualization.statistics_view import StatisticsView
from Mediators.rational_mediator import RationalMediator
from n_player_chicken_game import NPlayerChickenGame

STORE_PATH = Path('PlayersStorage', 'TwoFacedMixerPlayers')
# SAVE_PATH = Path('PlayersStorage', 'TwoFacedMixerPlayers25000')
SAVE_PATH = None


def run(n_players, k):
    storage_manager = PlayersStorageManager(
        store_path=STORE_PATH)

    players = storage_manager.load()[:n_players]
    for p in players:
        p.update_temperature(factor=0.28)

    threshold = 0.0033
    statistics = StatisticsCollector()
    mediator = RationalMediator(
        num_players=n_players,
        k=k,
        threshold=threshold,
        discount=0.9,
        stats_discount=0.9,
        stats_temperature=0.5,
        statistics_collector=statistics,
    )

    game_controller = NPlayerChickenGame(
        players, mediator, statistics_collector=statistics,
    )

    stats_view = StatisticsView(collector=statistics, threshold=threshold)

    # game_controller.play_round_series(25000)
    for i in range(3):
        game_controller.play_round_series(5000)
        stats_view.show_mediator_stats(mediator.ord_mode_player_probs(),
                                       mediator.punish_mode_player_probs())

    if SAVE_PATH is not None:
        storage_manager = PlayersStorageManager(store_path=SAVE_PATH,
                                                clear=True)
        storage_manager.dump_batch(players)

    stats_view.show()
