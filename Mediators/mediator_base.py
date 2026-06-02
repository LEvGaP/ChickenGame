from abc import ABC, abstractmethod
from enum import Enum


class MediatorMode(Enum):
    ORDINARY = "ORDINARY"
    PUNISHMENT = "PUNISHMENT"


class MediatorBase(ABC):
    """Abstract base for mediators that recommend actions and learn from outcomes."""
    def __init__(self):
        self._mode = MediatorMode.ORDINARY

    @abstractmethod
    def get_recommendations(self):
        """Return a recommendation (one per player) for the current round."""

    @abstractmethod
    def update_strategy(self, player_actions):
        """
        Update mediator state after players act.

        :param player_actions: Sequence of actions actually taken by each player.
        """

    @property
    def mode(self):
        """Return current mediator mode."""
        return self._mode
