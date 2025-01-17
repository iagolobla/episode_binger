from abc import ABC, abstractmethod
from episode_binger.Dataclasses import Episode

class Identical_Frame_Finder(ABC):
    """
    Abstract Class that defines how Identical Frame Finder Algorithms should behave
    """
    @abstractmethod
    def find_identical_frames(self, e1: Episode, e2: Episode, initial_frames: tuple, final_frames: tuple, blacklist: list=[]) -> tuple:
        """
        Description: Performs a blind search for identical frames between 2 episodes.

        Parameters:
            - e1: An episode
            - e2: Another episode
            - initial_frames: A tuple containing the starting frame to analyze in each episode like: (initial_frame_e1, initial_frame_e2)
            - final_frames: A tuple containing the final frame to analyze in each episode like: (final_frame_e1, final_frame_e2)
            - blacklist: A list of frames not to consider in the search. Useful to search for different matches

        Return Value: A tuple containing an identical pair of frame indexes like: (identical_frame_e1, identical_frame_e2)
        """
        pass