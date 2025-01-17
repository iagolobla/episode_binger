from enum import Enum
from episode_binger.Algorithms.Distance.Distance_Algorithm import Distance_Algorithm
from episode_binger.Algorithms.Distance.Euclidean_Distance import Euclidean_Distance
from episode_binger.Algorithms.Distance.Manhattan_Distance import Manhattan_Distance

class Distance_Algorithm_Type(Enum):
    """
    Enumeration Class with the types of Distance Algorithms in the project
    """
    MANHATTAN_DISTANCE = 0
    EUCLIDEAN_DISTANCE = 1