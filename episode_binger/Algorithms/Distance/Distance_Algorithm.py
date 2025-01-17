from episode_binger.Dataclasses import Episode
from abc import ABC, abstractmethod

class Distance_Algorithm(ABC):
    """
    Abstract Class that defines how Distance Algorithms should behave
    """
    @abstractmethod
    def calculate_distance(self, e1: Episode, e2: Episode, index_frames_e1: list, index_frames_e2: list, thumbnail_resolution: tuple, consecutive_frames: bool=False, reversed_list: bool=False):
        """
        Description: Calculates how different are the given frames from episode e1 and e2. It compares every specified frame from e1 with every specified frame from e2.

        Parameters:
            - e1: An episode
            - e2: Another episode
            - index_frames_e1: List of frame indexes from e1 to compare
            - index_frames_e2: List of frame indexes from e2 to compare
            - thumbnail_resolution: Performance Parameter. It's the size to resize frames after loading them. Generally, the lower the better but a 10th part from the original resolution should be fine.
            - consecutive_frames: Performance Parameter. True if the lists of frames are consecutive. This leads to better performance. Use it when possible.
            - reversed_list: True if the lists of frames should be reversed. It can be convenient depending on the latter analisys of distances.

        Return Value: A numpy matrix containing difference percentage between each pair of frames.
        """
        pass