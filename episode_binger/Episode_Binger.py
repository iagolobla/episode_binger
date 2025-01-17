from episode_binger.Algorithms.Chunks import Boundary_Finder_Type
from episode_binger.Algorithms.Chunks import Zoomin_Boundary_Finder
from episode_binger.Algorithms.Distance import Distance_Algorithm_Type
from episode_binger.Algorithms.Distance import Manhattan_Distance
from episode_binger.Algorithms.Distance import Euclidean_Distance
from episode_binger.Algorithms.Frames.IdenticalFrameFinder import Identical_Frames_Algorithm_Type
from episode_binger.Algorithms.Frames.IdenticalFrameFinder import Recursive_Frame_Finder
from episode_binger.Algorithms.Frames.FrameLocator import Frame_Locator_Type
from episode_binger.Algorithms.Frames.FrameLocator import Sequential_Frame_Locator
from episode_binger.Algorithms.Frames import Frame_Algorithm
from episode_binger.Algorithms import Algorithm_Manager
from episode_binger.Dataclasses import Episode
from episode_binger.Dataclasses import Chunk
from episode_binger.DAO import Episode_DAO
from episode_binger.Video import Video_Assembler
from multiprocessing import Pool

import logging

logger = logging.getLogger(__name__)

class Episode_Binger():
    """
    Class to load episodes, find openings and endings and create macro-episodes with only one opening and one ending
    """
    def __init__(self, distance_algorithm_type: Distance_Algorithm_Type = Distance_Algorithm_Type.MANHATTAN_DISTANCE, identical_frame_algorithm_type: Identical_Frames_Algorithm_Type = Identical_Frames_Algorithm_Type.RECURSIVE_FINDER, frame_locator_algorithm_type: Frame_Locator_Type = Frame_Locator_Type.SEQUENTIAL_FRAME_LOCATOR, boundary_finder_algorithm_type: Boundary_Finder_Type = Boundary_Finder_Type.ZOOMIN_FINDER):
        """
        Description: Creates an Episode_Binger object.

        Parameters:
            - distance_algorithm_type: An Distance_Algorithm_Type object to specify which algorithm should be used to calculate distances between frames
            - identical_frame_algorithm_type: An Identical_Frames_Algorithm_Type object to specify which algorithm should be used to find identical frames
            - frame_locator_algorithm_type: An Frame_Locator_Type object to specify which algorithm should be used to locate sets of consecutive frames in episodes
            - boundary_finder_algorithm_type: An Boundary_Finder_Type object to specify which algorithm should be used to find chunk boundaries from an identical pair of frames
        """
        # Create the distance algorithm object
        if distance_algorithm_type == Distance_Algorithm_Type.MANHATTAN_DISTANCE:
            distance_calculator = Manhattan_Distance()
        elif distance_algorithm_type == Distance_Algorithm_Type.EUCLIDEAN_DISTANCE:
            distance_calculator = Euclidean_Distance()

        # Create the identical frames algorithm object
        if identical_frame_algorithm_type == Identical_Frames_Algorithm_Type.RECURSIVE_FINDER:
            identical_frame_finder = Recursive_Frame_Finder(distance_calculator)
        if frame_locator_algorithm_type == Frame_Locator_Type.SEQUENTIAL_FRAME_LOCATOR:
            frame_locator = Sequential_Frame_Locator(distance_calculator, max_loading_frames=5000)
        frame_algorithm = Frame_Algorithm(identical_frame_finder, frame_locator)

        # Create the chunk_algorithm object
        if boundary_finder_algorithm_type == Boundary_Finder_Type.ZOOMIN_FINDER:
            boundary_finder = Zoomin_Boundary_Finder(distance_calculator)

        # Create the algoritm_manager object
        self.algorithm_manager = Algorithm_Manager(frame_algorithm, boundary_finder)
        
        # Create episode DAO
        self.episode_dao = Episode_DAO()

        # Create Video Assembler
        self.video_assembler = Video_Assembler()

    def add_episode(self, episode_path: str):
        """
        Description: Adds an episode to the episode binger object
        Parameters:
            - episode_path: A valid path for an episode
        """
        self.episode_dao.add_episode(episode_path)

    def find_opening_ending(self):
        """
        Description: From the episodes added to the episode binger takes two and compares them to find common regions and identifies them as opening and ending based on their locations.

        Return Value: True if the opening and ending were found, False otherwise.
        """
        # Check if there are 2 episodes at least
        if len(self.episode_dao.get_episode_list()) < 2:
            return False

        # Get 2 random episodes
        e1, e2 = self.episode_dao.get_random_episodes(2)

        openingFound=False
        endingFound=False
        opening_chunk_e1 = None
        opening_chunk_e2 = None
        ending_chunk_e1 = None
        ending_chunk_e2 = None

        change_episodes_attempts = 0
        # Search for opening and ending
        while not (openingFound and endingFound):
            # Blind Search
            if not openingFound and not endingFound:
                chunks = self.algorithm_manager.find_common_chunk(e1,e2)
            # Ending Search
            elif openingFound:
                chunks = self.algorithm_manager.find_common_chunk(e1,e2,(opening_chunk_e1.end_frame+1,opening_chunk_e2.end_frame+1))
            # Opening Search
            elif endingFound:
                chunks = self.algorithm_manager.find_common_chunk(e1,e2,to_frames=(ending_chunk_e1.start_frame,ending_chunk_e2.start_frame))

            # Chunk not found
            if not chunks:
                logger.debug("Chunk not found, trying again")
                change_episodes_attempts+=1
                if change_episodes_attempts > 20:
                    # Try again with 2 different episodes
                    e1, e2 = self.episode_dao.get_random_episodes(2)
                    openingFound=False
                    endingFound=False
                continue

            change_episodes_attempts=0

            e1_chunk, e2_chunk = chunks

            # Check if we are getting an opening or an ending
            if e1_chunk.isOpening() or e2_chunk.isOpening():
                opening_chunk_e1 = e1_chunk
                opening_chunk_e2 = e2_chunk
                openingFound=True
            else:
                ending_chunk_e1 = e1_chunk
                ending_chunk_e2 = e2_chunk
                endingFound=True

        # Store openings and endings in the episodes
        logger.debug(f"Openings: {opening_chunk_e1} and {opening_chunk_e2}")
        logger.debug(f"Endings: {ending_chunk_e1} and {ending_chunk_e2}")

        # Store openings and endings info
        self.episode_dao.add_openings([opening_chunk_e1,opening_chunk_e2])
        self.episode_dao.add_endings([ending_chunk_e1, ending_chunk_e2])

        return True

    def _locate_episode_pool(args):
        obj, config = args
        return obj.locate_episode(*config)

    def locate_opening_ending_every_episode(self):
        """
        Description: Given the opening and ending have been identified. Locate them in every added episode.
        """
        # Check if we have episodes with openings and endings located
        unlocated_episodes = self.episode_dao.get_all_unlocated_episodes()
        logger.debug("Unlocated episodes: [")
        for e in unlocated_episodes:
            logger.debug(f"\t{e},")
        logger.debug("]")
        
        # Select reference episode
        reference_episode = self.episode_dao.get_random_fully_located_episodes(1)[0]
        logger.debug(f"Reference episode: {reference_episode}")

        # Try to locate the openings and endings in the remaining episodes
        with Pool(processes=len(unlocated_episodes)) as pool:
            results = pool.map(Episode_Binger._locate_episode_pool, [(self.algorithm_manager,(e, reference_episode)) for e in unlocated_episodes])
        
        found_openings=[]
        found_endings=[]
        for r in results:
            op, en = r
            found_openings.append(op)
            found_endings.append(en)


        logger.debug(f"Found Openings: [")
        for c in found_openings:
            logger.debug(f"\t{c},")
        logger.debug("]")

        logger.debug(f"Found Endings: [")
        for c in found_endings:
            logger.debug(f"\t{c},")
        logger.debug("]")

        # Store found openings in their episodes
        self.episode_dao.add_openings(found_openings)

        # Store found endings in their episodes
        self.episode_dao.add_endings(found_endings)

    def create_macro_episode(self, macro_episode_path: str = "macro_episode.mp4"):
        """
        Description: Creates a new video file beggining with an opening, having all the added episodes without their openings and endings and finally, one ending at the end.

        Parameters:
            - macro_episode_path: Path where the output file should be created
        """
        # Get a random opening and ending
        opening = self.episode_dao.get_random_opening()
        ending = self.episode_dao.get_random_ending()

        # Prepare list of chunks: Opening - All Episodes without opening and ending - Ending
        chunk_list = []

        # Add opening
        chunk_list.append(opening)

        # Add every episode without opening or ending
        for episode in self.episode_dao.get_episode_list():
            # Check if episode has an opening
            if episode.opening:
                # Add section before the opening
                chunk_list.append(Chunk(episode, 0, episode.opening.start_frame-1))

                # Check if episode has an ending
                if episode.ending:
                    # Add section between opening and ending
                    chunk_list.append(Chunk(episode, episode.opening.end_frame+1, episode.ending.start_frame-1))

                    # Add section after the ending
                    chunk_list.append(Chunk(episode, episode.ending.end_frame+1, episode.frame_count-1))

                # If there's no ending
                else:
                    # Add section from the end of the opening until end of episode
                    chunk_list.append(Chunk(episode, episode.opening.end_frame+1, episode.frame_count-1))
            
            # If there's no opening
            else:
                # Check if episode has an ending
                if episode.ending:
                    # Add section before ending
                    chunk_list.append(Chunk(episode, 0, episode.ending.start_frame-1))

                    # Add section after ending
                    chunk_list.append(Chunk(episode, episode.ending.end_frame+1, episode.frame_count-1))
                
                # If there's no ending either
                else:
                    # Add the whole episode
                    chunk_list.append(Chunk(episode, 0, episode.frame_count-1))

        # Add ending
        chunk_list.append(ending)
        
        # Assemble the video with the requested chunks
        self.video_assembler.create_video(chunk_list, macro_episode_path)

    def save_episodes_info(self, output_path: str = "episode_info.json"):
        """
        Description: Saves all the found info about the added episodes like openings, endings and their location in every episode in one json file.

        Parameters:
            - output_path: Path where the json file should be created
        """
        self.episode_dao.save_episodes_info(output_path)

    def load_episodes_info(self, input_path: str = "episode_info.json"):
        """
        Description: Load all the info about a set of episodes like openings, endings and their location from a json file.

        Parameters:
            - input_path: Path where the json file is located
        """
        self.episode_dao.load_episodes_info(input_path)

