from episode_binger import Episode_Binger
from episode_binger.Algorithms.Distance import Manhattan_Distance
from episode_binger.Algorithms.Frames import Frame_Algorithm
from episode_binger.Algorithms.Frames.FrameLocator import Sequential_Frame_Locator
from episode_binger.Algorithms.Frames.IdenticalFrameFinder import Recursive_Frame_Finder
from episode_binger.Algorithms.Chunks import Zoomin_Boundary_Finder
from episode_binger.Algorithms import Algorithm_Manager

if __name__ == "__main__":
    # Create episode binger object
    eb = Episode_Binger()

    # Set custom options for algorithms
    thumbnail_resolution = (72, 128)
    identical_frame_finder_max_reshuffles = 30
    max_identical_frames_diff=0.05
    max_loading_frames=5000

    # Create Distance algorithm
    distance_algorithm = Manhattan_Distance()

    # Create Identical Frame Finder Algorithm
    my_identical_frame_finder = Recursive_Frame_Finder(distance_algorithm=distance_algorithm, thumbnail_resolution=thumbnail_resolution, max_reshuffles=identical_frame_finder_max_reshuffles, max_identical_frames_diff=max_identical_frames_diff)

    # Create Frame Locator Algorithm
    my_frame_locator = Sequential_Frame_Locator(distance_algorithm=distance_algorithm, thumbnail_resolution=thumbnail_resolution,max_loading_frames=max_loading_frames,max_identical_frames_diff=max_identical_frames_diff)

    # Join Frame Related algorithms into one object
    custom_frame_algorithms = Frame_Algorithm(identical_frame_finder=my_identical_frame_finder, frame_locator=my_frame_locator)

    # Create Boundary Finder Algorithm
    my_boundary_finder = Zoomin_Boundary_Finder(distance_algorithm=distance_algorithm,thumbnail_resolution=thumbnail_resolution,max_identical_frames_diff=max_identical_frames_diff)

    # Create new Algorithm Manager
    custom_algorithm_manager = Algorithm_Manager(custom_frame_algorithms,my_boundary_finder)

    # Replace Episode Binger object's algorithm manager for our custom one
    eb.algorithm_manager=custom_algorithm_manager

    # Add episodes to episode_binger
    eb.add_episode("./input_data/Episode1.mp4")
    eb.add_episode("./input_data/Episode2.mp4")
    eb.add_episode("./input_data/Episode3.mp4")
    eb.add_episode("./input_data/Episode4.mp4")
    eb.add_episode("./input_data/Episode5.mp4")
    eb.add_episode("./input_data/Episode6.mp4")

    # Blind search for an opening and an ending
    eb.find_opening_ending()

    # Find opening and ending in every episode
    eb.locate_opening_ending_every_episode()

    # Save opening and ending info for every episode in a file
    eb.save_episodes_info()

    # Create macro episode
    eb.create_macro_episode("Six_Episodes.mp4")
