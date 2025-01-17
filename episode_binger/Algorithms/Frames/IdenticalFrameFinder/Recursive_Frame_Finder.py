from episode_binger.Algorithms.Frames.IdenticalFrameFinder import Identical_Frame_Finder
from episode_binger.Dataclasses import Episode
from random import randint
import numpy as np
from episode_binger.Algorithms.Distance import Distance_Algorithm
import logging

logger = logging.getLogger(__name__)

class Recursive_Frame_Finder(Identical_Frame_Finder):
    """
    Class that holds an specific Identical Frame Finder algorithm that uses recursivity to operate
    """
    def __init__(self, distance_algorithm: Distance_Algorithm, thumbnail_resolution: tuple = (36,64), num_subsamples: int = 50, max_reshuffles: int = 20, max_identical_frames_diff: float = 0.01, max_similar_frames_diff: float = 0.10,):
        """
        Description: Creates a Recursive_Frame_Finder object

        Parameters:
            - distance_algorithm: An instance of a Distance_Algorithm object
            - thumbnail_resolution: Performance Parameter. It's the size to resize frames after loading them. Generally, the lower the better but a 10th part from the original resolution should be fine.
            - num_subsamples: Number of subsamples to take in every step of the algorithm
            - max_reshuffles: Max amount of random shuffles to pick frames to compare
            - max_identical_frames_diff: Max difference percentage (between 0 and 1) between frames to consider them identical
            - max_similar_frames_diff: Max difference percentage (between 0 and 1) between frames to consider them similar
        """
        self.max_reshuffles = max_reshuffles
        self.distance_algorithm = distance_algorithm
        self.thumbnail_resolution = thumbnail_resolution
        self.num_subsamples = num_subsamples
        self.max_similar_frames_diff = max_similar_frames_diff
        self.max_identical_frames_diff = max_identical_frames_diff

    def _recursive_identical_frames(self, e1: Episode, e2: Episode, initial_frames: tuple, final_frames: tuple, max_reshuffles: int, blacklist: list=[], best_match: list=[],level:int = 0):
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
        used_offsets = []

        e1_full_section_len = final_frames[0]-initial_frames[0]
        e2_full_section_len = final_frames[1]-initial_frames[1]

        # Check if any section len is under num_sections
        e1_subsection_len = e1_full_section_len // self.num_subsamples
        e2_subsection_len = e2_full_section_len // self.num_subsamples

        # If subsection len is 1 or less, fix subsection_offset to 0
        if e1_subsection_len <= 1:
            e1_subsection_len = 1
            e1_section_offset = 0

        # If subsection len is 1 or less, fix subsection_offset to 0
        if e2_subsection_len == 0:
            e2_subsection_len = 1
            e2_section_offset = 0

        max_possible_offset_combinations = e1_subsection_len*e2_subsection_len
        reshuffle = 0

        while reshuffle < max_reshuffles and len(used_offsets) < max_possible_offset_combinations:       
            # Get Random offsets
            e1_section_offset = randint(0,e1_subsection_len-1)
            e2_section_offset = randint(0,e2_subsection_len-1)

            # Check offset combination hasn't been used before
            while ((e1_section_offset,e2_section_offset) in used_offsets):
                e1_section_offset = randint(0,e1_subsection_len-1)
                e2_section_offset = randint(0,e2_subsection_len-1)

            # Mark offset combination as used
            used_offsets.append((e1_section_offset,e2_section_offset))

            # Get frames list of frames to compare
            e1_frame_list = (np.array(range(self.num_subsamples))*e1_subsection_len+e1_section_offset+initial_frames[0])
            e2_frame_list = (np.array(range(self.num_subsamples))*e2_subsection_len+e2_section_offset+initial_frames[1])
            
            # Filter out invalid frames (out of range)
            e1_frame_list = e1_frame_list[np.where(np.logical_and(e1_frame_list>=0, e1_frame_list<e1.frame_count))].tolist()
            e2_frame_list = e2_frame_list[np.where(np.logical_and(e2_frame_list>=0, e2_frame_list<e2.frame_count))].tolist()

            # Get distances between all selected frames
            frames_relative_distances = self.distance_algorithm.calculate_distance(e1, e2, e1_frame_list, e2_frame_list,self.thumbnail_resolution)


            num_zoom_ins=0  # Set nested zoomins to 0
            # Loop while the found minimum distances are below the reshuffle threshold
            while np.min(frames_relative_distances) <= self.max_similar_frames_diff:
                # Get minimum distance
                min_distance = np.min(frames_relative_distances)
                min_distance_index = np.unravel_index(np.argmin(frames_relative_distances),frames_relative_distances.shape)
                # Convert local indexes to global ones
                global_min_distance_index = (e1_frame_list[min_distance_index[0]],e2_frame_list[min_distance_index[1]])

                # If there's not a best match yet, store it
                if not best_match:
                    best_match.append((global_min_distance_index[0],global_min_distance_index[1],min_distance))

                # If the found match is better than the best stored match and not in found matches list
                elif global_min_distance_index not in blacklist and min_distance < best_match[0][2]:
                    best_match.clear()
                    best_match.append((global_min_distance_index[0],global_min_distance_index[1],min_distance))

                # Check if found minimum distance is low enough to consider frames as equal
                if min_distance <= self.max_identical_frames_diff:
                    # Save identical frames found
                    identical_frames = (global_min_distance_index[0],global_min_distance_index[1])

                    # Get the most identical pair of frames in the suroundings of the found match
                    e1_proximity_frames = [i for i in range(identical_frames[0]-50 if identical_frames[0]-50 > 0 else 0,identical_frames[0]+50 if identical_frames[0]+50 < e1.frame_count else e1.frame_count-1)]
                    e2_proximity_frames = [i for i in range(identical_frames[1]-50 if identical_frames[1]-50 > 0 else 0,identical_frames[1]+50 if identical_frames[1]+50 < e2.frame_count else e2.frame_count-1)]
                    distances = self.distance_algorithm.calculate_distance(e1,e2,e1_proximity_frames,e2_proximity_frames,self.thumbnail_resolution,True)

                    # Get closest frames considering frame succession
                    diagonal_matrix = np.zeros((len(e1_proximity_frames),len(e2_proximity_frames)))
                    for i in range(len(e1_proximity_frames)):
                        for j in range(len(e2_proximity_frames)):
                            sum = 0
                            count = 0

                            for k in range(min(len(e1_proximity_frames)-i,len(e2_proximity_frames)-j)):
                                sum += distances[i+k,j+k]
                                count += 1
                            
                            diagonal_matrix[i,j] = sum/count
                    min_distance = np.min(diagonal_matrix)
                    min_distance_index = np.unravel_index(np.argmin(diagonal_matrix),diagonal_matrix.shape)
                    closest_frames=(e1_proximity_frames[min_distance_index[0]],e2_proximity_frames[min_distance_index[1]])

                    # If the identical frames weren't found before -> Return the match
                    if (closest_frames not in blacklist):
                        blacklist.append(closest_frames)
                        return closest_frames
                    else:
                        break

                # Check if max amount of allowed zoom_ins reached
                if num_zoom_ins >= 1:
                    break   # Exit loop (Don't keep geting into zoom ins)
                
                # If found frames are not similar enough to be considered as identical, zoom in
                # Get subsection boundaries
                e1_subsection_lower_boundary = global_min_distance_index[0]-int(e1_subsection_len/2)
                e1_subsection_upper_boundary = global_min_distance_index[0]+int(e1_subsection_len/2)
                e2_subsection_lower_boundary = global_min_distance_index[1]-int(e2_subsection_len/2)
                e2_subsection_upper_boundary = global_min_distance_index[1]+int(e2_subsection_len/2)

                # Ensure boundaries are within the frame range of the episodes
                e1_subsection = (e1_subsection_lower_boundary if e1_subsection_lower_boundary >= 0 else 0, e1_subsection_upper_boundary if e1_subsection_upper_boundary <= e1.frame_count else e1.frame_count)
                e2_subsection = (e2_subsection_lower_boundary if e2_subsection_lower_boundary >= 0 else 0, e2_subsection_upper_boundary if e2_subsection_upper_boundary <= e2.frame_count else e2.frame_count)

                # Get the result in zoomed in section
                if e1_full_section_len >= self.num_subsamples and e2_full_section_len >= self.num_subsamples:
                    # Nested Identical frames searchs cannot reshuffle
                    zoomed_in_result = self._recursive_identical_frames(e1, e2, (e1_subsection[0], e2_subsection[0]),(e1_subsection[1], e2_subsection[1]), 1, blacklist, best_match)
                    num_zoom_ins+=1

                    if zoomed_in_result is not None:
                        return zoomed_in_result
                
                # If can't zoom in any closer and the identical pair wasn't found, break the loop (The next ones are worse since the results are ordered)
                else:
                    break
                
                frames_relative_distances[min_distance_index] = 2   # Set value above 100% difference (To not process it again)
            
            reshuffle+=1
        
        return None # No identical frames found

    def find_identical_frames(self, e1: Episode, e2: Episode, initial_frames: tuple, final_frames: tuple, blacklist: list=[]) -> tuple:
        best_match = []
        identical_frames = self._recursive_identical_frames(e1,e2,initial_frames,final_frames,self.max_reshuffles,blacklist,best_match,0)

        if identical_frames is None and best_match[0] is not None:
            return best_match[0]
        return identical_frames
