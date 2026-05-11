from Utils.mixer_player_storage_manager import PlayersStorageManager
from pathlib import Path
from n_player_chicken_game import compute_payoffs


def run():
    storage = PlayersStorageManager(Path('MixerPlayerStorage'))
    players = storage.load()
    players[174].log_parameters()
