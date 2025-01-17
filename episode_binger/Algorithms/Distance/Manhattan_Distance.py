from threading import Thread
import numpy as np
from episode_binger.Dataclasses import Episode
from episode_binger.Algorithms.Distance import Distance_Algorithm

class Manhattan_Distance(Distance_Algorithm):
    """
    Class that holds an specific Distance Algorithm that calculates the distance between frames using the Manhattan Distances
    """
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
        e1_frames = []
        e2_frames = []

        max_distance = thumbnail_resolution[1]*thumbnail_resolution[0]*3*255    # Max Manhattan Distance

        # If frames to load are not consecutive
        if not consecutive_frames:
            e1_thread = Thread(target=e1.load_frame_list, args=(index_frames_e1, thumbnail_resolution, reversed_list, e1_frames))
            e2_thread = Thread(target=e2.load_frame_list, args=(index_frames_e2, thumbnail_resolution, reversed_list, e2_frames))
        # If frames to load are consecutive
        else:
            e1_thread = Thread(target=e1.load_consecutive_frames, args=(index_frames_e1[0],len(index_frames_e1),thumbnail_resolution, reversed_list, e1_frames))
            e2_thread = Thread(target=e2.load_consecutive_frames, args=(index_frames_e2[0],len(index_frames_e2),thumbnail_resolution, reversed_list, e2_frames))

        e1_thread.start()
        e2_thread.start()

        e1_thread.join()
        e2_thread.join()

        e1_frames = np.array(e1_frames)
        e2_frames = np.array(e2_frames)

        # Calculate Manhattan Distance
        comparing_matrix = e1_frames[:, np.newaxis]-e2_frames
        comparing_matrix = np.abs(comparing_matrix)
        comparing_matrix = np.sum(comparing_matrix,axis=(-1,-2,-3))

        return comparing_matrix / max_distance  # Return relative distances
