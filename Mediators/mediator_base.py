from abc import ABC, abstractmethod


class MediatorBase(ABC):
    """Abstract base for mediators that recommend actions and learn from outcomes."""

    @abstractmethod
    def get_recommendations(self):
        """Return a recommendation (one per player) for the current round."""

    @abstractmethod
    def update_strategy(self, player_actions):
        """
        Update mediator state after players act.

        :param player_actions: Sequence of actions actually taken by each player.
        """
