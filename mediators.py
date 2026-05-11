from chicken_game import STAY, SWERVE
import numpy as np
import logging


class RandomMediator:
    def __init__(self, actions, num_players):
        """
        Initializes the mediator.
        :param actions: list of possible actions (e.g., ['SWERVE', 'STAY'])
        :param num_players: total number of players in the game
        """
        self.actions = actions
        self.num_players = num_players

    def get_recommendations(self):
        """
        Returns a list of recommendations for all players.
        Each recommendation is uniformly drawn from the set of actions.
        """
        return np.random.choice(self.actions, size=self.num_players)


class RandomMediatorV2:
    def __init__(self, num_players):
        self.num_players = num_players

    def get_recommendations(self):
        stay_index = np.random.randint(0, self.num_players)
        recommendations = [SWERVE] * self.num_players
        recommendations[stay_index] = STAY
        return recommendations


class SequenceMediator:
    def __init__(self, num_players):
        self.num_players = num_players
        self.stay_index = self.num_players - 1

    def get_recommendations(self):
        self.stay_index = (self.stay_index + 1) % self.num_players
        recommendations = [SWERVE] * self.num_players
        recommendations[self.stay_index] = STAY
        return recommendations


class PunishingMediator:
    def __init__(self, num_players, k):
        self.num_players = num_players
        self.k = k  # Number of stay recommendations during punishment

        # State tracking
        self.stay_index = self.num_players - 1
        self.consecutive_deviations = [0] * num_players
        self.last_recommendations = []

        # Punishment state
        self.punished_player = None
        self.punishment_group_offset = 0

    def get_recommendations(self):
        recommendations = [SWERVE] * self.num_players

        if self.punished_player is not None:
            if self.punishment_group_offset == 0:
                print(f'Start punishing: {self.punished_player}\n')
            # --- Punishment Mode ---
            # Get list of all players except the one being punished
            eligible_players = [p for p in range(self.num_players) if
                                p != self.punished_player]

            # Select k players using a rotating offset to ensure different groups
            # We use modulo to wrap around the eligible list
            for i in range(self.k):
                idx = (self.punishment_group_offset + i) % len(
                    eligible_players)
                recommendations[eligible_players[idx]] = STAY

            # Update offset for the next round to ensure different players are picked
            self.punishment_group_offset = \
                (self.punishment_group_offset + self.k) % len(eligible_players)

        else:
            # --- Normal Mode (Sequential) ---
            self.stay_index = (self.stay_index + 1) % self.num_players
            recommendations[self.stay_index] = STAY

        self.last_recommendations = recommendations
        return recommendations

    def update_strategy(self, actual_actions):
        """
        Updates deviation counts and switches modes based on player actions.
        """
        for i in range(self.num_players):
            # Check if player i deviated from recommendation
            if actual_actions[i] != self.last_recommendations[i]:
                self.consecutive_deviations[i] += 1
            else:
                self.consecutive_deviations[i] = 0

        # Logic for exiting punishment
        if self.punished_player is not None:
            # If the punished player finally followed the recommendation (SWERVE)
            if actual_actions[self.punished_player] == SWERVE:
                print(f'Stop punishing: {self.punished_player}\n')
                self.punished_player = None
                self.punishment_group_offset = 0
                # Optional: reset their deviation count after punishment
                self.consecutive_deviations = [0] * self.num_players
            return  # Stay in punishment mode until they swerve

        # Logic for entering punishment
        for i in range(self.num_players):
            if self.consecutive_deviations[i] >= 2:
                self.punished_player = i
                self.punishment_group_offset = 0
                break  # Punish the first person found who deviated twice


class PunishingMediatorV2:
    def __init__(self, num_players, k, with_sophistics=False):
        self.num_players = num_players
        self.k = k  # Number of people recommended to STAY during punishment

        # State tracking for Normal Mode
        self.stay_index = num_players - 1
        self.consecutive_deviations = [0] * num_players
        self.last_recommendations = []

        # State tracking for Punishment Mode
        self.punished_player = None
        self.punishment_swerves_count = 0  # Counter for the stopping condition
        self.punishment_group_offset = 0
        self.start_punishing = False
        self.with_sophistics = with_sophistics

    def get_recommendations(self):
        recommendations = [SWERVE] * self.num_players

        if self.punished_player is not None:
            if self.start_punishing:
                self.start_punishing = False
                logging.info(f'Start punishing: {self.punished_player}')

            if self.with_sophistics:
                for i in range(self.k):
                    recommendations[i] = STAY
            else:
                # --- PUNISHMENT MODE ---
                # Deviated player is forced to SWERVE
                # We pick k other players to STAY
                eligible_players = [p for p in range(self.num_players) if
                                    p != self.punished_player]

                for i in range(self.k):
                    # Use modulo to cycle through groups of size k
                    idx = (self.punishment_group_offset + i) % len(
                        eligible_players)
                    recommendations[eligible_players[idx]] = STAY

                # Rotate the group for the next round
                self.punishment_group_offset = (
                                                           self.punishment_group_offset + self.k) % len(
                    eligible_players)

        else:
            # --- NORMAL MODE ---
            # Simple sequential rotation
            self.stay_index = (self.stay_index + 1) % self.num_players
            recommendations[self.stay_index] = STAY

        self.last_recommendations = recommendations
        return recommendations

    def update_strategy(self, actual_actions):
        """
        Updates internal state based on what players actually did.
        """
        # 1. Update deviation trackers for all players
        for i in range(self.num_players):
            if actual_actions[i] != self.last_recommendations[i]:
                self.consecutive_deviations[i] += 1
            else:
                self.consecutive_deviations[i] = 0

        # 2. Logic if we are currently in Punishment Mode
        if self.punished_player is not None:
            # Check if the punished player followed the recommendation (SWERVE)
            if actual_actions[self.punished_player] == SWERVE:
                self.punishment_swerves_count += 1
            else:
                # If they deviate (STAY) during their punishment, reset the counter
                self.punishment_swerves_count = 0

            # Exit condition: Two consecutive swerves
            if self.punishment_swerves_count >= 3:
                logging.info(f'Stop punishing: {self.punished_player}')
                self.punished_player = None
                self.punishment_swerves_count = 0
                # Reset all deviation counts when returning to normal mode
                self.consecutive_deviations = [0] * self.num_players

            return  # Exit function; don't trigger new punishments while one is active

        selected_player_followed = actual_actions[self.stay_index] == STAY
        logging.info(f'{selected_player_followed=}')
        # 3. Logic to enter Punishment Mode (Normal Mode)
        for i in range(self.num_players):
            if self.consecutive_deviations[i] >= 2:
                self.punished_player = i
                self.punishment_swerves_count = 0
                self.start_punishing = True
                break


class PunishingMediatorV3:
    def __init__(self, num_players, k, discount=0.5, threshold=1.5,
                 with_sophistics=False):
        self.num_players = num_players
        self.k = k  # Number of people recommended to STAY during punishment
        self.discount = discount
        self.threshold = threshold
        self.with_sophistics = with_sophistics

        # State tracking for Normal Mode
        self.stay_index = num_players - 1
        self.deviation_scores = [0.0] * num_players
        self.last_recommendations = []

        # State tracking for Punishment Mode
        self.punished_player = None
        self.punishment_swerves_count = 0  # Counter for the stopping condition
        self.punishment_group_offset = 0
        self.start_punishing = False

    def _calculate_new_score(self, current_score, deviated):
        """
        Update rule: discount * prob + current_action (1 if deviated, 0 if not)
        """
        return (self.discount * current_score) + (1 if deviated else 0)

    def get_recommendations(self):
        recommendations = [SWERVE] * self.num_players

        if self.punished_player is not None:
            # Handle logging for the first round of punishment
            if self.start_punishing:
                self.start_punishing = False
                logging.info(f'Start punishing player: {self.punished_player}')

            if self.with_sophistics:
                # Sophistic handling: always recommend the first k players to stay
                for i in range(self.k):
                    recommendations[i] = STAY
            else:
                # Standard Punishment: Rotate through eligible players in groups of k
                eligible_players = [p for p in range(self.num_players) if
                                    p != self.punished_player]

                for i in range(self.k):
                    idx = (self.punishment_group_offset + i) % len(
                        eligible_players)
                    recommendations[eligible_players[idx]] = STAY

                # Rotate the group offset for the next round
                self.punishment_group_offset = (
                                                           self.punishment_group_offset + self.k) % len(
                    eligible_players)

        else:
            # --- NORMAL MODE ---
            self.stay_index = (self.stay_index + 1) % self.num_players
            recommendations[self.stay_index] = STAY

        self.last_recommendations = recommendations
        return recommendations

    def update_strategy(self, actual_actions):
        """
        Updates internal state based on actual actions using the discounted score.
        """
        # 1. Update deviation scores for all players
        for i in range(self.num_players):
            deviated = (actual_actions[i] != self.last_recommendations[i])
            self.deviation_scores[i] = self._calculate_new_score(
                self.deviation_scores[i], deviated)

        # 2. Logic if we are currently in Punishment Mode
        if self.punished_player is not None:
            # Check if the punished player followed the recommendation (SWERVE)
            if actual_actions[self.punished_player] == SWERVE:
                self.punishment_swerves_count += 1
            else:
                # If they deviate (STAY) during punishment, reset the counter
                self.punishment_swerves_count = 0

            # Exit condition: Two consecutive swerves
            if self.punishment_swerves_count >= 2:
                logging.info(f'Stop punishing player: {self.punished_player}')

                # Reset punished player score and state
                self.deviation_scores[self.punished_player] = 0.0
                self.punished_player = None
                self.punishment_swerves_count = 0

            return  # Skip normal mode logic during punishment

        # Logging for Normal Mode: did the person we told to STAY actually STAY?
        selected_player_followed = (actual_actions[self.stay_index] == STAY)
        logging.info(f'{selected_player_followed=}')

        # 3. Logic to enter Punishment Mode (check scores against threshold)
        for i in range(self.num_players):
            if self.deviation_scores[i] >= self.threshold:
                self.punished_player = i
                self.punishment_swerves_count = 0
                self.punishment_group_offset = 0
                self.start_punishing = True
                break
