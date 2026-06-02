from Utils.players_storage_manager import PlayersStorageManager
from n_player_chicken_game import NPlayerChickenGame
from Players.base_player import BasePlayer
from Mediators.loyal_punishment_mediator import LoyalPunishmentMediator
from Mediators.rational_mediator import RationalMediator
from pathlib import Path
from Utils.statistics_collector import StatisticsCollector
from Visualization import StatisticsView

STORE_PATH = Path('PlayersStorage', 'TwoFacedMixerPlayers')
SAVE_PATH = Path('PlayersStorage', 'TwoFacedMixerPlayers25000')
# SAVE_PATH = None


def run(n_players, k):
    storage_manager = PlayersStorageManager(
        store_path=STORE_PATH)
    trained_players = storage_manager.load()[:n_players]

    for p in trained_players:
        p.update_temperature(factor=0.28)

    players: list[BasePlayer] = trained_players

    statistics = StatisticsCollector()
    threshold = 0.0033
    mediator = LoyalPunishmentMediator(num_players=n_players, k=k,
                                       threshold=threshold,
                                       discount=0.9,
                                       statistics_collector=statistics)

    game_controller = NPlayerChickenGame(
        players, mediator, statistics_collector=statistics)

    game_controller.play_round_series(40000)

    for p in players:
        p.log_parameters()

    if SAVE_PATH is not None:
        storage_manager = PlayersStorageManager(store_path=SAVE_PATH,
                                                clear=True)
        storage_manager.dump_batch(players)

    StatisticsView(collector=statistics, threshold=threshold).show()
