import dataclasses, logging


SWERVE = 0
STAY = 1
ACTIONS = [SWERVE, STAY]


@dataclasses.dataclass
class RoundHistory:
    action: STAY | SWERVE
    recommendation: STAY | SWERVE


class ChickenGame:
    def __init__(self, player1, player2, mediator):
        self.p1 = player1
        self.p2 = player2
        self.matrix = {
            (SWERVE, SWERVE): (-1, -1),
            (SWERVE, STAY):   (-1, 7),
            (STAY, SWERVE):   (7, -1),
            (STAY, STAY):     (-5, -5)
        }
        self.mediator = mediator
        self.p1_history: list[RoundHistory] = []
        self.p2_history: list[RoundHistory] = []

    def play_round(self):
        recommendations = self.mediator.get_recommendations()

        a1 = self.p1.get_action(recommendations[0])
        a2 = self.p2.get_action(recommendations[1])

        self.p1_history.append(RoundHistory(a1, recommendations[0]))
        self.p2_history.append(RoundHistory(a2, recommendations[1]))

        # 2. Get payoffs
        payoff1, payoff2 = self.matrix[(a1, a2)]

        self.p1.update(a1, a2, payoff1)
        self.p2.update(a2, a1, payoff2)

        return a1, a2, payoff1, payoff2, recommendations[0], recommendations[1]

    def play_round_series(self, rounds_count):
        logging.debug(
            f"{'Round':<8}"
            f" | {'P1 Action':<10} | {'P2 Action':<10}"
            f" | {'P1 Payoff':<10} | {'P2 Payoff':<10}"
            f" | {'P1 Signal':<10} | {'P2 Signal':<10}")

        for r in range(1, rounds_count + 1):
            p1_move, p2_move, p1_payoff, p2_payoff, p1_signal, p2_signal = self.play_round()
            logging.debug(
                f"{r:<8}"
                f" | {p1_move:<10} | {p2_move:<10}"
                f" | {p1_payoff:<10} | {p2_payoff:<10}"
                f" | {p1_signal:<10} | {p2_signal:<10}")