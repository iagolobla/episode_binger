from enum import Enum
from episode_binger.Algorithms.Chunks.Boundary_Finder import Boundary_Finder
from episode_binger.Algorithms.Chunks.Zoomin_Boundary_Finder import Zoomin_Boundary_Finder


class Boundary_Finder_Type(Enum):
    """
    Enumeration Class with the types of Boundary Finder Algorithms in the project
    """
    ZOOMIN_FINDER = 0