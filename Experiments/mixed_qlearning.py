from GameControllers.chicken_game import ChickenGame
from Players.q_learning_player import QLearningPlayer
from Players.mixer_player import MixerPlayer
from Mediators.mediators import RandomMediatorV2


def create_mixer_player(name):
    sub_players = [
        QLearningPlayer("QLearning", learning_rate=0.2, temperature=0.5),
        QLearningPlayer("QLearning", learning_rate=0.2, temperature=0.5),
        QLearningPlayer("QLearning", learning_rate=0.2, temperature=0.5),
    ]

    return MixerPlayer(name, players=sub_players, learning_rate=0.1, temperature=2)


def play_game(total_rounds):
    p1 = create_mixer_player("Mixer1")
    p2 = create_mixer_player("Mixer2")

    mediator = RandomMediatorV2(num_players=2)

    game = ChickenGame(p1, p2, mediator)

    for r in range(total_rounds - 10):
        game.play_round()

    print(
        f"{'Round':<8} | {'P1 Action':<10} | {'P2 Action':<10} |"
        f" {'P1 Payoff':<10} | {'P2 Payoff':<10} | {'P1 Signal':<10} | {'P2 Signal':<10}")
    for r in range(total_rounds - 10 + 1, total_rounds + 1):
        p1_move, p2_move, p1_payoff, p2_payoff, p1_signal, p2_signal = game.play_round()
        print(
            f"{r:<8} | {p1_move:<10} | {p2_move:<10} |"
            f" {p1_payoff:<10} | {p2_payoff:<10} | {p1_signal:<10} | {p2_signal:<10}")

    print(
        f"Results: {p1.name}: {p1.total_score} | {p2.name}: {p2.total_score}")

    p1.log_parameters()
    p2.log_parameters()