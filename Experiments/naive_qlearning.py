from Players.q_learning_player import QLearningPlayerV2
from mediators import RandomMediatorV2
from chicken_game import ChickenGame


def play_game(total_rounds):
    p1 = QLearningPlayerV2("QLearning", learning_rate=0.1)
    p2 = QLearningPlayerV2("QLearning2", learning_rate=0.1)

    mediator = RandomMediatorV2(num_players=2)

    game = ChickenGame(p1, p2, mediator)

    for r in range(total_rounds - 10):
        game.play_round()

    print(
        f"{'Round':<8} | {'P1 Action':<10} | {'P2 Action':<10} | {'P1 Payoff':<10} | {'P2 Payoff':<10}")
    for r in range(total_rounds - 10 + 1, total_rounds + 1):
        p1_move, p2_move, p1_payoff, p2_payoff = game.play_round()
        print(
            f"{r:<8} | {p1_move:<10} | {p2_move:<10} | {p1_payoff:<10} | {p2_payoff:<10}")

    print(f"Results: {p1.name}: {p1.total_score} | {p2.name}: {p2.total_score}")

    p1.display_parameters()
    p2.display_parameters()
