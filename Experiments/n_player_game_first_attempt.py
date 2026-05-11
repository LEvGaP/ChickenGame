from Utils.mixer_player_storage_manager import PlayersStorageManager
from mediators import SequenceMediator
from pathlib import Path
from n_player_chicken_game import NPlayerChickenGame


def run():
    storage_manager = PlayersStorageManager(Path('MixerPlayerStorage'))
    players = storage_manager.load()

    mediator = SequenceMediator(num_players=len(players))
    game_controller = NPlayerChickenGame(players, mediator)

    # for i in range(1000):
    #     game_controller.play_round()

    for i in range(1000):
        actions, payoffs, recommendations = game_controller.play_round()
        actions = list(map(int, actions))
        if actions == recommendations:
            continue
        payoffs = list(map(float, payoffs))
        print(f'Iteration: {i}\n'
              f'{actions=}\n'
              f'{payoffs=}\n'
              f'{recommendations=}\n')

    for p in players:
        p.log_parameters()


