from abc import ABC, abstractmethod
from episode_binger.Dataclasses import Episode

class Frame_Locator(ABC):
    """
    Abstract Class that defines how Frame Locator Algorithms should behave
    """
    @abstractmethod
    def locate_frames(self, frames_to_locate: list, ref_episode: Episode, search_episode: Episode, reverse_search: bool = False):
        """
        Description: Locates a list of frames from a given episode in another episode.

        Parameters:
            - frames_to_locate: The list of frame indexes from the ref_episode to locate in the search_episode
            - ref_episode: The reference episode
            - search_episode: The episode to search frames in
            - reverse_search: True if the search should start from the ending of the episode instead of the beggining

        Return Value: A tuple containing a dictionary relating the frames of the reference episode with the ones in the search episode and a measure of how similar they are (The closer to 1 the better). Example: ({1234: 2345, 1235: 2346, 1236: 2347}, 0.95)
        """
        pass