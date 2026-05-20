from academy import Academy, PlayerRank
from Players.mixer_player import MixerPlayer
from Players.q_learning_player import QLearningPlayer, EpsGreedyQLearningPlayer
from Players.two_faced_player import TwoFacedPlayer
from Utils.mixer_player_storage_manager import PlayersStorageManager
from pathlib import Path


def run(players_num=8):
    players = create_two_faced_mixer_players(players_num)

    academy = Academy(players, max_iterations=200)
    academy.run()

    academy.log_groups_stats()
    academy.log_each_player()

    sophistic_players = academy.student_groups[PlayerRank.SOPHISTIC]
    save_players(sophistic_players)


def save_players(players):

    storage_manager = PlayersStorageManager(
        store_path=Path('PlayersStorage', 'TwoFacedMixerPlayers'),
        clear=True)
    storage_manager.dump_batch(players)


def create_two_faced_mixer_players(n):
    return [TwoFacedPlayer(f'TwoFaced {i}', stay_face=create_mixer_player(i),
                           swerve_face=create_mixer_player(i))
            for i in range(n)]


def create_two_faced_mixer_with_mutual_policy(i):
    mutual_policy = QLearningPlayer(f'QL mutual {i}', temperature=1)
    player1 = MixerPlayer(
        f'Mixer 1 {i}',
        players=[
            QLearningPlayer(f'QL {j} {i}', temperature=1)
            for j in range(2)
        ] + [mutual_policy],
        temperature=1)
    player2 = MixerPlayer(
        f'Mixer 2 {i}',
        players=[
                    QLearningPlayer(f'QL {j} {i}', temperature=1)
                    for j in range(2)
                ] + [mutual_policy],
        temperature=1)

    return TwoFacedPlayer(f'TwoFaced Mixer {i}',
                          stay_face=player1,
                          swerve_face=player2)


def create_mixer_player(idx):
    policies = [QLearningPlayer(f'QL {idx} {i}', temperature=1) for i in range(3)]
    return MixerPlayer(f'Mixer {idx}', policies, temperature=1)


def create_two_faced_players(number):
    return [
        TwoFacedPlayer(f"TwoFaced {i}",
                       QLearningPlayer("QL 1", temperature=1.0),
                       QLearningPlayer("QL 2", temperature=1.0))
        for i in range(number)
    ]


def create_large_number_of_similar_players(number):
    return [
        MixerPlayer(f'Mixer {i}',
                    [
                        QLearningPlayer(f'QLearning 1', temperature=1),
                        QLearningPlayer(f'QLearning 2', temperature=1.5),
                        QLearningPlayer(f'QLearning 3', temperature=2),
                    ],
                    temperature=1
                    )
        for i in range(number)
    ]


def create_different_players():
    return [
        MixerPlayer(f'Mixer QL {i}',
                    [QLearningPlayer(f'QLearning {j}', temperature=1) for j in
                     range(3)],
                    temperature=1
                    )

        for i in range(10)
    ] + \
    [
        MixerPlayer(f'Mixer EpsGreedyQLearning {i}',
                    [EpsGreedyQLearningPlayer(f'EpsGreedyQL {j}') for j in
                     range(3)],
                    temperature=1
                    )

        for i in range(10)
    ]
