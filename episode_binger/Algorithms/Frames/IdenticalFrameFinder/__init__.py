from enum import Enum
from episode_binger.Algorithms.Frames.IdenticalFrameFinder.Identical_Frame_Finder import Identical_Frame_Finder
from episode_binger.Algorithms.Frames.IdenticalFrameFinder.Recursive_Frame_Finder import Recursive_Frame_Finder

class Identical_Frames_Algorithm_Type(Enum):
    """
    Enumeration Class with the types of Identical Frames Finder Algorithms in the project
    """
    RECURSIVE_FINDER = 0