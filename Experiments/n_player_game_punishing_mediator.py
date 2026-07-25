from Utils.players_storage_manager import PlayersStorageManager
from n_player_chicken_game import NPlayerChickenGame, get_compute_payoffs
from Players.base_player import BasePlayer
from Mediators.loyal_punishment_mediator import LoyalPunishmentMediator
from Mediators.rational_mediator import RationalMediator
from pathlib import Path
from Utils.statistics_collector import StatisticsCollector
from Visualization import StatisticsView

STORE_PATH = Path('PlayersStorage', 'TwoFacedMixerPlayers')
SAVE_PATH = Path('PlayersStorage', 'TwoFacedMixerPlayers40000')
# SAVE_PATH = None

SAVE_FIG_DIR = Path(r'C:\Users\Евгений\Pictures\Эксперименты с дет садом')
FILE_SUFFIX = 'Lmed_a7_-1.png'


def run(n_players, k):
    storage_manager = PlayersStorageManager(
        store_path=STORE_PATH)
    trained_players = storage_manager.load()[:n_players]

    for p in trained_players:
        p.update_temperature(factor=0.28)

    players: list[BasePlayer] = trained_players

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
        players,
        mediator,
        payoff_function=get_compute_payoffs(-1),
        statistics_collector=stats_collector)

    for i in range(1, 6):
        stats_collector.clear()
        game_controller.play_round_series(10000)

        for p in trained_players:
            p.log_parameters()

        fig_file_name = f'{i * 10}r_{FILE_SUFFIX}'

        stats_view = StatisticsView(
            collector=stats_collector,
            threshold=threshold
        )

        stats_view.show(
            save_file=SAVE_FIG_DIR / fig_file_name
        )

    if SAVE_PATH is not None:
        storage_manager = PlayersStorageManager(store_path=SAVE_PATH,
                                                clear=True)
        storage_manager.dump_batch(players)
