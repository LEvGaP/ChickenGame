from Utils.players_storage_manager import PlayersStorageManager
from Utils.statistics_collector import StatisticsCollector
from pathlib import Path
from Visualization.game_history_grid import GameHistoryGridView
from Mediators.rational_mediator import RationalMediator
from GameControllers.n_player_chicken_game import NPlayerChickenGame

STORE_PATH = Path('PlayersStorage', 'TwoFacedMixer25000')
SAVE_PATH = Path('PlayersStorage', 'TwoFacedMixer40000')


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
        statistics_collector=statistics,
    )

    game_controller = NPlayerChickenGame(
        players, mediator, statistics_collector=statistics,
    )


    view = GameHistoryGridView(n_players)
    for i in range(10):
        actions, payoffs, recs = game_controller.play_round()
        view.append_round(actions, recs)

    view.pump()
    view.run_mainloop()

    # if SAVE_PATH:
    #     storage_manager = PlayersStorageManager(store_path=SAVE_PATH)
    #     storage_manager.dump_batch(players)
    #
    # StatisticsView(statistics, threshold=threshold).show()