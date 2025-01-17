from episode_binger.Dataclasses import Episode
from episode_binger.Algorithms.Frames.IdenticalFrameFinder import Identical_Frame_Finder
from episode_binger.Algorithms.Frames.FrameLocator import Frame_Locator

class Frame_Algorithm():
    """
    Aggregation Class that holds the 2 frame-related algorithms: The identical frame finder and the frame locator.
    """
    def __init__(self, identical_frame_finder: Identical_Frame_Finder, frame_locator: Frame_Locator):
        """
        Description: Creates an Frame_Algorithm object

        Parameters:
            - identical_frame_finder: An instance of an Identical_Frame_Finder object
            - frame_locator: An instance of an Frame_Locator object
        """
        self.identical_frame_finder = identical_frame_finder
        self.frame_locator = frame_locator

    def find_identical_frames(self, e1: Episode, e2: Episode, initial_frames: tuple, final_frames: tuple, blacklist: list=[]) -> tuple:
        return self.identical_frame_finder.find_identical_frames(e1,e2,initial_frames,final_frames,blacklist)

    def locate_frames(self, frames_to_locate: list, ref_episode: Episode, search_episode: Episode, starting_search_index: int = 0, ending_search_index: int = None, reverse_search: bool = False):
        return self.frame_locator.locate_frames(frames_to_locate, ref_episode, search_episode, starting_search_index, ending_search_index, reverse_search)
