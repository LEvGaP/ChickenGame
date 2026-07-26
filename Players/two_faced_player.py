from Players.base_player import BasePlayer
from GameControllers.chicken_game import STAY
import logging


class TwoFacedPlayer(BasePlayer):
    def __init__(self, name, stay_face: BasePlayer, swerve_face: BasePlayer):
        super().__init__(name)
        self.stay_face = stay_face
        self.swerve_face = swerve_face
        self.last_signal = None

    def get_action(self, recommendation=0):
        face = self.stay_face if recommendation == STAY else self.swerve_face

        self.last_signal = recommendation
        return face.get_action()

    def update(self, my_action, opponent_action, my_payoff):
        face = self.stay_face if self.last_signal == STAY else self.swerve_face
        face.update(my_action, opponent_action, my_payoff)

    def swap_strategy(self):
        self.stay_face, self.swerve_face = self.swerve_face, self.stay_face

    def update_temperature(self, factor):
        for p in (self.stay_face, self.swerve_face):
            p.update_temperature(factor)

    def log_parameters(self):
        logging.info(f'Two-Faced Player: {self.name} (stay, swerve)')
        self.stay_face.log_parameters()
        self.swerve_face.log_parameters()

