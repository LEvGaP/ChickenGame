from Utils.players_storage_manager import PlayersStorageManager
from pathlib import Path


def run():
    storage = PlayersStorageManager(Path('MixerPlayerStorage'))
    players = storage.load()
    players[174].log_parameters()
