from Utils.mixer_player_storage_manager import PlayersStorageManager
from pathlib import Path
from Visualization.game_history_grid import GameHistoryGridView
from Mediators.loyal_punishment_mediator import LoyalPunishmentMediator
from n_player_chicken_game import NPlayerChickenGame

def run(n_players, k):
    storage_manager = PlayersStorageManager(
        store_path=Path('PlayersStorage', 'TwoFacedMixerPlayers'))

    players = storage_manager.load()[:n_players]
    for p in players:
        p.update_temperature(factor=0.28)

    mediator = LoyalPunishmentMediator(num_players=n_players, k=k,
                                        threshold=0.0033,
                                        discount=0.9)

    game_controller = NPlayerChickenGame(players, mediator)

    view = GameHistoryGridView(n_players)
    for i in range(100):
        actions, payoffs, recs = game_controller.play_round()
        view.append_round(actions, recs)

    # view.pump()
    view.run_mainloop()