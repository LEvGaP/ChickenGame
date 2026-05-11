import logging

from Utils.mixer_player_storage_manager import PlayersStorageManager
from mediators import PunishingMediatorV2
from n_player_chicken_game import NPlayerChickenGame
from Players.base_player import BasePlayer
from Mediators.loyal_punishment_mediator import LoyalPunishmentMediator
from pathlib import Path


def run(num_players, k):
    storage_manager = PlayersStorageManager(
        store_path=Path('PlayersStorage', 'TwoFacedMixerPlayers'))
    trained_players_num = num_players
    trained_players = storage_manager.load()[:trained_players_num]

    for p in trained_players:
        p.update_temperature(factor=0.28)

    players: list[BasePlayer] = trained_players

    mediator = LoyalPunishmentMediator(num_players=num_players, k=k,
                                       threshold=0.0033,
                                       discount=0.9)

    game_controller = NPlayerChickenGame(players, mediator)

    for i in range(3):
        game_controller.play_round_series(rounds=5000)
        game_controller.log_unfollowed_players(last_rounds=5000, threshold=10)

    for p in players:
        p.log_parameters()
