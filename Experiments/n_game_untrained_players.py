from Players.players_factory import create_two_faced_mixer_players
from Utils.statistics_collector import StatisticsCollector
from Utils.players_storage_manager import PlayersStorageManager
from Mediators.loyal_punishment_mediator import LoyalPunishmentMediator
from n_player_chicken_game import NPlayerChickenGame, get_compute_payoffs
from Visualization import StatisticsView
from pathlib import Path

STORE_PATH = Path('PlayersStorage', 'TwoFacedMixerPlayers10000')
SAVE_FIG_FILE = Path(r'C:\Users\Евгений\Pictures\Эксперименты без дет сада',
                     'LPmed_50r_-1_8k.png')


def run(n_players, k):
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
    stats_view.show(save_file=SAVE_FIG_FILE)
