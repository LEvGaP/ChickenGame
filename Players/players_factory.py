from Players.mixer_player import MixerPlayer
from Players.q_learning_player import QLearningPlayer
from Players.two_faced_player import TwoFacedPlayer


def create_two_faced_mixer_players(n):
    return [create_two_faced_mixer_player(i) for i in range(n)]


def create_two_faced_mixer_player(idx):
    return TwoFacedPlayer(f'TwoFaced {idx}',
                          stay_face=create_mixer_player(idx),
                          swerve_face=create_mixer_player(idx))


def create_mixer_player(idx):
    policies = [QLearningPlayer(f'QL {idx} {i}', temperature=1) for i in range(3)]
    return MixerPlayer(f'Mixer {idx}', policies, temperature=1)