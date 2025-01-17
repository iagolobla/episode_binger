from episode_binger.Dataclasses import Episode
from episode_binger.Dataclasses import Chunk
from episode_binger.Algorithms.Chunks import Boundary_Finder
from episode_binger.Algorithms.Distance import Distance_Algorithm
import numpy as np
import logging

logger = logging.getLogger(__name__)

class Zoomin_Boundary_Finder(Boundary_Finder):
    """
    Class that holds an specific Boundary Finder Algorithm that finds the boundaries of a chunk performing a general scan and then zooming in into regions of interest
    """
    def __init__(self, distance_algorithm: Distance_Algorithm, thumbnail_resolution: tuple = (36,64), max_frames_search_range: int = 180*24, max_loading_frames: int = 100, max_similar_frames_diff: float = 0.1, max_identical_frames_diff: float = 0.03):
        """
        Description: Creates a Zoomin_Boundary_Finder object

        Parameters:
            - distance_algorithm: An instance of the Distance_Algorithm object
            - thumbnail_resolution: Performance Parameter. It's the size to resize frames after loading them. Generally, the lower the better but a 10th part from the original resolution should be fine.
            - max_frames_search_range: Max amount of frames to look forward and backwards from the starting point to find chunk boundaries
            - max_loading_frames: Max amount of frames to load at once for the search
            - max_similar_frames_diff: Max difference percentage (between 0 and 1) between frames to consider them similar
            - max_identical_frames_diff: Max difference percentage (between 0 and 1) between frames to consider them identical
        """
        self.distance_algorithm = distance_algorithm
        self.max_frames_search_range = max_frames_search_range
        self.thumbnail_resolution = thumbnail_resolution
        self.max_similar_frames_diff = max_similar_frames_diff
        self.max_identical_frames_diff = max_identical_frames_diff
        self.max_loading_frames = max_loading_frames
        
    def find_boundaries(self, e1: Episode, e2: Episode, identical_frames: tuple) -> tuple:
        """
        Description: Finds the upper and lower limit of a identical chunk in 2 episodes

        Parameters:
            - e1: An episode
            - e2: Another episode
            - identical_frames: Tuple containing frame indexes like: (frame_index_e1, frame_index_e2)

        Return value: Tuple containing 2 chunks like: (chunk_e1, chunk_e2). Each chunk is defined by an start and end frame
        """
        # Generate frame lists
        e1_frame_indexes_aux = [i for i in range(identical_frames[0]-self.max_frames_search_range//2,identical_frames[0],self.max_frames_search_range//self.max_loading_frames)] + [i for i in range(identical_frames[0],identical_frames[0]+self.max_frames_search_range//2,self.max_frames_search_range//self.max_loading_frames)]
        e2_frame_indexes_aux = [i for i in range(identical_frames[1]-self.max_frames_search_range//2,identical_frames[1],self.max_frames_search_range//self.max_loading_frames)] + [i for i in range(identical_frames[1], identical_frames[1]+self.max_frames_search_range//2,self.max_frames_search_range//self.max_loading_frames)]

        # Only keep valid frames from lists
        e1_frame_indexes = []
        e2_frame_indexes = []
        for i in range(len(e1_frame_indexes_aux)):
            if e1_frame_indexes_aux[i] >= 0 and e2_frame_indexes_aux[i] >= 0 and e1_frame_indexes_aux[i] < e1.frame_count and e2_frame_indexes_aux[i] < e2.frame_count:
                e1_frame_indexes.append(e1_frame_indexes_aux[i])
                e2_frame_indexes.append(e2_frame_indexes_aux[i])
        e1_frame_indexes_aux.clear()
        e2_frame_indexes_aux.clear()

        # Get frames lists comparison (One to one)
        distance_matrix = self.distance_algorithm.calculate_distance(e1, e2, e1_frame_indexes, e2_frame_indexes,self.thumbnail_resolution)

        # Iterate through distances and get the first and last that complies with the navigation_threshold
        first_similar_pair=None
        last_similar_pair=None
        for i in range(len(e1_frame_indexes)):
            if not first_similar_pair:
                if distance_matrix[i,i] <= self.max_similar_frames_diff:
                    first_similar_pair=(e1_frame_indexes[i], e2_frame_indexes[i])
                    last_similar_pair=(e1_frame_indexes[i], e2_frame_indexes[i])
            else:
                if distance_matrix[i,i] <= self.max_similar_frames_diff:
                    last_similar_pair=(e1_frame_indexes[i], e2_frame_indexes[i])
                else:
                    break

        if not first_similar_pair:
            # Maybe throw an exception: "First Similar Pair of Frames not found"
            return None
        
        # Search for the first identical pair of frames
        lower_boundary=None
        e1_first_frame_indexes = [i for i in range(first_similar_pair[0]-self.max_frames_search_range//self.max_loading_frames if first_similar_pair[0]-self.max_frames_search_range//self.max_loading_frames > 0 else 0,first_similar_pair[0]+1)]
        e2_first_frame_indexes = [i for i in range(first_similar_pair[1]-self.max_frames_search_range//self.max_loading_frames if first_similar_pair[1]-self.max_frames_search_range//self.max_loading_frames > 0 else 0,first_similar_pair[1]+1)]
        distance_matrix = self.distance_algorithm.calculate_distance(e1, e2, e1_first_frame_indexes, e2_first_frame_indexes,self.thumbnail_resolution,True)
        
        # Get closest frames considering frame succession
        diagonal_matrix = np.zeros((len(e1_first_frame_indexes),len(e2_first_frame_indexes)))
        for i in range(len(e1_first_frame_indexes)):
            for j in range(len(e2_first_frame_indexes)):
                sum = 0
                count = 0

                for k in range(min(len(e1_first_frame_indexes)-i,len(e2_first_frame_indexes)-j)):
                    sum += distance_matrix[i+k,j+k]
                    count += 1
                
                diagonal_matrix[i,j] = sum/count
        min_distance_index = np.unravel_index(np.argmin(diagonal_matrix),diagonal_matrix.shape)

        checking_index = (min_distance_index[0]-min(min_distance_index[0],min_distance_index[1]),min_distance_index[1]-min(min_distance_index[0],min_distance_index[1]))
        for i in range(len(e1_first_frame_indexes)-max(checking_index[0],checking_index[1])):
            if diagonal_matrix[checking_index[0]+i,checking_index[1]+i] <= self.max_identical_frames_diff:
                lower_boundary=(e1_first_frame_indexes[checking_index[0]+i],e2_first_frame_indexes[checking_index[1]+i])
                break

        if not lower_boundary:
            # Maybe throw exception "Error finding lower boundary. Consider adjusting acceptance_threshold(Current value: {self.max_identical_frames_diff})"
            logger.debug(f"Error finding lower boundary. Consider adjusting acceptance_threshold(Current value: {self.max_identical_frames_diff})")
            return None
                
        # Search for the last identical pair of frames
        upper_boundary=None
        e1_last_frame_indexes = [i for i in range(last_similar_pair[0],last_similar_pair[0]+self.max_frames_search_range//self.max_loading_frames if last_similar_pair[0]+self.max_frames_search_range//self.max_loading_frames < e1.frame_count else e1.frame_count)]
        e2_last_frame_indexes = [i for i in range(last_similar_pair[1],last_similar_pair[1]+self.max_frames_search_range//self.max_loading_frames if last_similar_pair[1]+self.max_frames_search_range//self.max_loading_frames < e2.frame_count else e2.frame_count)]
        distance_matrix = self.distance_algorithm.calculate_distance(e1, e2, e1_last_frame_indexes, e2_last_frame_indexes,self.thumbnail_resolution,True,True)
        e1_last_frame_indexes.reverse()
        e2_last_frame_indexes.reverse()

        # Get closest frames considering frame succession
        diagonal_matrix = np.zeros((len(e1_last_frame_indexes),len(e2_last_frame_indexes)))
        for i in range(len(e1_last_frame_indexes)):
            for j in range(len(e2_last_frame_indexes)):
                sum = 0
                count = 0

                for k in range(min(len(e1_last_frame_indexes)-i,len(e2_last_frame_indexes)-j)):
                    sum += distance_matrix[i+k,j+k]
                    count += 1
                
                diagonal_matrix[i,j] = sum/count
        min_distance_index = np.unravel_index(np.argmin(diagonal_matrix),diagonal_matrix.shape)

        checking_index = (min_distance_index[0]-min(min_distance_index[0],min_distance_index[1]),min_distance_index[1]-min(min_distance_index[0],min_distance_index[1]))
        for i in range(len(e1_last_frame_indexes)-max(checking_index[0],checking_index[1])):
            if diagonal_matrix[checking_index[0]+i,checking_index[1]+i] <= self.max_identical_frames_diff:
                upper_boundary=(e1_last_frame_indexes[checking_index[0]+i],e2_last_frame_indexes[checking_index[1]+i])
                break
            
        if not upper_boundary:
            # Maybe throw exception "Error finding upper boundary. Consider adjusting acceptance_threshold(Current value: {self.max_identical_frames_diff})"
            logger.debug(f"Error finding upper boundary. Consider adjusting acceptance_threshold(Current value: {self.max_identical_frames_diff})")
            return None

        # Return Result
        return (Chunk(e1, lower_boundary[0], upper_boundary[0]),Chunk(e2, lower_boundary[1], upper_boundary[1]))