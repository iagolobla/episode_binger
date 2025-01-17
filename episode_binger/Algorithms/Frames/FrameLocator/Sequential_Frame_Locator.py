from episode_binger.Algorithms.Frames.FrameLocator import Frame_Locator
from episode_binger.Dataclasses import Episode
from episode_binger.Algorithms.Distance import Distance_Algorithm
import numpy as np
import logging

logger = logging.getLogger(__name__)

class Sequential_Frame_Locator(Frame_Locator):
    """
    Class that holds an specific Frame Locator algorithm that loads sequential sections of frames for the search
    """
    def __init__(self, distance_algorithm: Distance_Algorithm, thumbnail_resolution: tuple = (36,64), max_loading_frames: int = 500, max_identical_frames_diff: float = 0.03):
        """
        Description: Creates a Sequential_Frame_Locator object

        Parameters:
            - distance_algorithm: An instance of the Distance_Algorithm object
            - thumbnail_resolution: Performance Parameter. It's the size to resize frames after loading them. Generally, the lower the better but a 10th part from the original resolution should be fine.
            - max_loading_frames: Max amount of frames to load at once when searching
            - max_identical_frames_diff: Max difference percentage (between 0 and 1) between frames to consider them identical
        """
        self.distance_algorithm = distance_algorithm
        self.thumbnail_resolution = thumbnail_resolution
        self.max_loading_frames = max_loading_frames
        self.max_identical_frames_diff = max_identical_frames_diff

    def locate_frames(self, frames_to_locate: list, ref_episode: Episode, search_episode: Episode, starting_search_index: int = 0, ending_search_index: int = None, reverse_search: bool = False):
        """
        Description: Locates a list of frames from a given episode in another episode.

        Parameters:
            - frames_to_locate: The list of frame indexes from the ref_episode to locate in the search_episode
            - ref_episode: The reference episode
            - search_episode: The episode to search frames in
            - reverse_search: True if the search should start from the ending of the episode instead of the beggining

        Return Value: A tuple containing a dictionary relating the frames of the reference episode with the ones in the search episode and a measure of how similar they are (The closer to 1 the better). Example: ({1234: 2345, 1235: 2346, 1236: 2347}, 0.95)
        """
        # Adjust ending search index
        if ending_search_index is None or ending_search_index >= search_episode.frame_count:
            ending_search_index = search_episode.frame_count    # Note that last accessed index will be ending_search_index - 1

        # Check if starting search index is wrong
        if starting_search_index < 0 or starting_search_index >= ending_search_index:
            # TODO: Raise Exception
            pass

        # Divide search range in chunks to avoid running out of memory
        section_len = self.max_loading_frames
        num_sections = (ending_search_index - starting_search_index) // section_len

        if num_sections == 0:
            num_sections=1

        # Create result dict
        result = {}
        best_match={}

        # Extra iteration mechanism to fix possible matches between iterations
        extra_iteration=False

        # Search for frames in each section
        s=0

        while s < num_sections:
            # Common iteration
            if not extra_iteration:
                # Load episode forward
                if not reverse_search:
                    # Get frame indexes to compare with
                    if s < num_sections-1:
                        search_frames = [f for f in range(s*section_len+starting_search_index,starting_search_index+(s+1)*section_len)]
                    else:
                        search_frames = [f for f in range(s*section_len+starting_search_index,ending_search_index)]
                # Load episode backwards
                else:
                    # Get frame indexes to compare with
                    if s == 0:
                        search_frames = [f for f in range((num_sections-1-s)*section_len+starting_search_index,ending_search_index)]
                    else:
                        search_frames = [f for f in range((num_sections-1-s)*section_len+starting_search_index,starting_search_index+(num_sections-s)*section_len)]
            # Extra iteration
            else:
                extra_iteration=False

            # Compare reference frames with current search frames
            distance_matrix = self.distance_algorithm.calculate_distance(ref_episode, search_episode, frames_to_locate, search_frames, self.thumbnail_resolution, True, False)

            # Get closest frames considering frame succession
            diagonal_matrix = np.zeros((len(frames_to_locate),len(search_frames)))
            for i in range(len(frames_to_locate)):
                for j in range(len(search_frames)):
                    sum = 0
                    count = 0

                    for k in range(min(len(frames_to_locate)-i,len(search_frames)-j)):
                        sum += distance_matrix[i+k,j+k]
                        count += 1
                    
                    diagonal_matrix[i,j] = sum/count
            min_distance_index = np.unravel_index(np.argmin(diagonal_matrix),diagonal_matrix.shape)

            checking_index = (min_distance_index[0]-min(min_distance_index[0],min_distance_index[1]),min_distance_index[1]-min(min_distance_index[0],min_distance_index[1]))
            
            diff_value = (diagonal_matrix[checking_index[0],checking_index[1]],min([distance_matrix[checking_index[0]+i,checking_index[1]+i] for i in range(min(min_distance_index[0],min_distance_index[1])+1)]))
            if not best_match:
                best_match["frame_to_locate"]=frames_to_locate[checking_index[0]]
                best_match["search_frame"]=search_frames[checking_index[1]]
                best_match["diagonal_diff"]=diff_value[0]
                best_match["min_frame_diff"]=diff_value[1]
            elif diff_value[0] < best_match["diagonal_diff"] and diff_value[1] < best_match["min_frame_diff"]:
                # Check if the match could be split between search_frames
                if checking_index[0] != 0:
                    # Run an extra search with the full range to be sure
                    search_frames = [f for f in range(search_frames[checking_index[1]]-(section_len//2),search_frames[checking_index[1]]+(section_len//2))]
                    extra_iteration = True
                    continue    # Go for the extra iteration

                best_match["frame_to_locate"]=frames_to_locate[checking_index[0]]
                best_match["search_frame"]=search_frames[checking_index[1]]
                best_match["diagonal_diff"]=diff_value[0]
                best_match["min_frame_diff"]=diff_value[1]

            if diff_value[0] <= self.max_identical_frames_diff or diff_value[1] < 0.01:
                break
            
            # Update loop variable
            s+=1

        for i in range(len(frames_to_locate)):
            result[best_match["frame_to_locate"]+i]=best_match["search_frame"]+i

        return (result, (1-best_match["min_frame_diff"]))