from Players.base_player import BasePlayer
from pathlib import Path
import pickle
import logging


class PlayersStorageManager:
    SUFFIX = '.pkl'

    def __init__(self, store_path: Path = Path('PlayersStorage'), clear=False):
        self.store_path = store_path

        if clear:
            self.clear()

    def dump_batch(self, players: list[BasePlayer]):
        for p in players:
            self.dump(p)

    def dump(self, player: BasePlayer):
        file_path = self.store_path / f'{player.name}{self.SUFFIX}'
        with open(file_path, 'wb') as f:
            pickle.dump(player, f)
            logging.debug(f'Player {player.name} was dumped')

    def load(self) -> list[BasePlayer]:
        players = []
        for file_path in self.store_path.iterdir():
            if file_path.is_file() and file_path.name.endswith(self.SUFFIX):
                with open(file_path, 'rb') as f:
                    p = pickle.load(f)
                    logging.debug(f'Player {p.name} was loaded')
                    players.append(p)

        return players

    def clear(self):
        for p in self.store_path.iterdir():
            p.unlink()

        logging.debug("Storage was cleared")
