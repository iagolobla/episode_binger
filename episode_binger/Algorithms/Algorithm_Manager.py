from episode_binger.Dataclasses import Episode
from episode_binger.Dataclasses import Chunk
from episode_binger.Algorithms.Frames import Frame_Algorithm
from episode_binger.Algorithms.Chunks import Boundary_Finder

import logging

logger = logging.getLogger(__name__)

class Algorithm_Manager():
    """
    Class that holds the different algorithms used and groups their functionalities to find and locate openings and endings
    """
    def __init__(self, frame_algorithm: Frame_Algorithm, chunk_boundary_finder: Boundary_Finder):
        """
        Description: Creates an Algorithm_Manager Object.

        Parameters:
            - frame_algorithm: An instance of an Frame_Algorithm object
            - chunk_boundary_finder: An instance of an Boundary_Finder object
        """
        self.frame_algorithm = frame_algorithm
        self.chunk_boundary_finder = chunk_boundary_finder

    def find_common_chunk(self, e1: Episode, e2: Episode, from_frames: tuple=(0,0), to_frames: tuple=None, chunk_min_seconds: int = 30) -> tuple:
        """
        Description: Function to find a common chunk of video between 2 files.

        Parameters:
            - e1: An episode
            - e2: Another episode
            - from_frames: Tuple indicating lower limit of frames to start the search (Shaped like: (e1_start_frame, e2_start_frame)). If omited will be from the beginning.
            - to_frames: Tuple indicating upper limit of frames to end the search (Shaped like: (e1_end_frame, e2_end_frame)). If omited will be until the end.
            - chunk_min_seconds: Minimum length in seconds to consider a chunk of interest

        Return Value: A tuple containing 2 identical chunks, like: (chunk_e1, chunk_e2). None if any could be found
        """
        # Check if frame shapes are the same
        if e1.frame_shape != e2.frame_shape:
            raise Exception("Episodes have different frame shapes")

        # If no final frames for the search are given, take the last ones
        if to_frames is None:
            to_frames = (e1.frame_count, e2.frame_count)

        # Minimum lengths (in frames) to consider a chunk relevant
        min_relevant_chunk_len = int(chunk_min_seconds*e1.fps)

        # Set Max Retries
        max_retries = 3

        blacklist = []

        for _ in range(max_retries):
            # Search for identical frames
            identical_frames = self.frame_algorithm.find_identical_frames(e1,e2,(from_frames[0],from_frames[1]),(to_frames[0],to_frames[1]),blacklist=blacklist) 

            # Find boundaries of the chunk
            chunks = self.chunk_boundary_finder.find_boundaries(e1, e2, identical_frames)

            # If couldn't find the boundaries, try again
            if not chunks:
                continue

            chunk_e1, chunk_e2 = chunks

            # Check if the chunk is big enough to have in consideration
            if chunk_e1.end_frame-chunk_e1.start_frame < min_relevant_chunk_len or chunk_e2.end_frame-chunk_e2.start_frame < min_relevant_chunk_len:
                continue

            # Return the chunk definition ((e1_start,e1_end),(e2_start, e2_end))
            return chunks
        
        # If couldn't find common chunks return None
        return None
    
    def find_chunk_in_episode(self, episode: Episode, chunk: Chunk, starting_search_index: int = 0, ending_search_index: int = None, reverse_search: bool = False, minimum_reliability: float = 0.90) -> Chunk:
        """
        Description: Searches for a chunk in an episode.

        Parameters:
            - episode: Episode where to look for the given chunk
            - chunk: Chunk of frames from another episode to search for in the given episode
            - starting_search_index: Starting frame in the episode to look for the chunk
            - ending_search_index: Ending frame in the episode to look for the chunk
            - reverse_search: True when the search should start from the end of the episode towards its beggining
            - minimum_reliability: Parameter to establish result reliability. Values closer to one might deliver better results but with a lower performance. Also, higher values might not find any matches

        Return Value: Matching chunk in the search episode
        """
        # Adjust ending_search_index
        if ending_search_index is None or ending_search_index >= episode.frame_count:
            ending_search_index = episode.frame_count

        # Check if starting search index is wrong
        if starting_search_index < 0 or starting_search_index >= ending_search_index:
            # TODO: Raise Exception
            return None
        
        # Take starting frames of the chunk
        starting_frames=[chunk.start_frame + i for i in range(5)]

        # Locate those frames in the episode
        starting_frames_relation, reliability = self.frame_algorithm.locate_frames(starting_frames, chunk.episode, episode, starting_search_index, ending_search_index, reverse_search)

        # Check location reliability
        if reliability < minimum_reliability:
            # TODO: Raise Exception
            return None

        # Take ending frames of the chunk
        ending_frames=[chunk.end_frame-4+i for i in range(5)]

        # Locate those frames in the episode (Aim search to where they should be located)
        ending_frames_relation, reliability = self.frame_algorithm.locate_frames(ending_frames, chunk.episode, episode, starting_frames_relation[starting_frames[-1]], starting_frames_relation[starting_frames[-1]] + (chunk.end_frame-chunk.start_frame)*2)

        # Check location reliability
        if reliability < minimum_reliability:
            # TODO: Raise Exception
            return None

        # Return found chunk
        found_chunk = Chunk(episode, starting_frames_relation[starting_frames[0]], ending_frames_relation[ending_frames[-1]])
        return found_chunk
    
    def locate_episodes(self, episodes: list, ref_episode: Episode) -> tuple:
        """
        Description: Locates opening and ending of a reference episode in the given episodes

        Parameters:
            - episodes: List of episodes where the opening and ending have not been located yet
            - ref_episode: Episode with its opening and ending located. The Episode object must contain the opening and ending chunks

        Return Value: Tuple containing 2 lists, the first one with the opening chunk for every given episode and the second one with the endings
        """
        # Create Result list with found openings and found endings
        found_openings = []
        found_endings = []

        # Search for opening and ending in the episodes
        for episode in episodes:
            # Locate opening in the episode
            opening = self.find_chunk_in_episode(episode, ref_episode.opening)

            # Locate ending in the episode
            if opening:
                # Save found opening
                found_openings.append(opening)
                ending = self.find_chunk_in_episode(episode, ref_episode.ending, opening.end_frame+1,reverse_search=True)
            else:
                ending = self.find_chunk_in_episode(episode, ref_episode.ending,reverse_search=True)

            # Save found ending
            if ending:
                found_endings.append(ending)

        # Return found openings and endings
        return found_openings, found_endings
    
    def locate_episode(self, episode: Episode, ref_episode: Episode) -> tuple:
        """
        Description: Locates opening and ending of a reference episode in a given episode

        Parameters:
            - episode: Episode where opening and ending should be located
            - ref_episode: Episode with its opening and ending located. The Episode object must contain the opening and ending chunks

        Return Value: A tuple with 2 chunks (opening and ending) of the search episode, like: (opening, ending)
        """
        # Locate opening in the episode
        opening = self.find_chunk_in_episode(episode, ref_episode.opening)

        # Locate ending in the episode
        if opening:
            ending = self.find_chunk_in_episode(episode, ref_episode.ending, opening.end_frame+1,reverse_search=True)
        else:
            ending = self.find_chunk_in_episode(episode, ref_episode.ending,reverse_search=True)

        # Return found openings and endings
        return opening, ending