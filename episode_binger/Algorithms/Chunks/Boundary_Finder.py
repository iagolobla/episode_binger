from abc import ABC, abstractmethod
from episode_binger.Dataclasses import Episode

class Boundary_Finder(ABC):
    """
    Abstract Class that defines how Boundary Finder Algorithms should behave
    """
    @abstractmethod
    def find_boundaries(self, e1: Episode, e2: Episode, identical_frames: tuple) -> tuple:
        """
        Description: Finds the upper and lower limit of a identical chunk in 2 episodes

        Parameters:
            - e1: An episode
            - e2: Another episode
            - identical_frames: Tuple containing frame indexes like: (frame_index_e1, frame_index_e2)

        Return value: Tuple containing 2 chunks like: (chunk_e1, chunk_e2). Each chunk is defined by an start and end frame
        """
        pass