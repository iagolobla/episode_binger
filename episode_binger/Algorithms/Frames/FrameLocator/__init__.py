from enum import Enum
from episode_binger.Algorithms.Frames.FrameLocator.Frame_Locator import Frame_Locator
from episode_binger.Algorithms.Frames.FrameLocator.Sequential_Frame_Locator import Sequential_Frame_Locator

class Frame_Locator_Type(Enum):
    """
    Enumeration Class with the types of Frame Locator Algorithms in the project
    """
    SEQUENTIAL_FRAME_LOCATOR = 0