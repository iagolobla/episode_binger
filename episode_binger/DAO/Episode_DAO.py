from episode_binger.Dataclasses import Episode
from episode_binger.Dataclasses import Chunk
from random import sample
import json

class Episode_DAO:
    """
    Class that holds the results and data of the episode binger
    """
    def __init__(self):
        # Episodes Dictionary
        self.episodes = {}
        self.episode_order=[]

    def add_episode(self, path: str):
        """
        Description: Stores the path of an episode and loads it

        Parameters:
            - path: Valid path of the episode to load
        """
        self.episodes[path] = Episode(path)
        self.episode_order.append(path)

    def get_random_episodes(self, num_episodes: int) -> list:
        """
        Description: Selects a random sample of loaded episodes

        Parameters:
            - num_episodes: Amount of episodes to select

        Return Value: List of random loaded episodes
        """
        # Check if there are enough episodes loaded
        if len(self.episodes.keys()) < num_episodes:
            # TODO: Raise exception (There are not that many episodes loaded)
            return []

        # Select x randomly
        return sample(list(self.episodes.values()),num_episodes)
    
    def get_all_fully_located_episodes(self) -> list:
        """
        Description: Selects all the fully located episodes. That means every episode with both opening and ending located

        Return Value: List of Episodes
        """
        located_episodes = []

        # Check every episode to see if it's located
        for episode_path in self.episodes.keys():
            if self.episodes[episode_path].opening != None and self.episodes[episode_path].ending != None:
                located_episodes.append(self.episodes[episode_path])
        
        return located_episodes

    def get_all_located_episodes(self) -> list:
        """
        Description: Selects all the located episodes. That means every episode with either opening, ending or both located

        Return Value: List of Episodes
        """
        located_episodes = []

        # Check every episode to see if it's located
        for episode_path in self.episodes.keys():
            if self.episodes[episode_path].opening != None or self.episodes[episode_path].ending != None:
                located_episodes.append(self.episodes[episode_path])
        
        return located_episodes
    
    def get_all_unlocated_episodes(self) -> list:
        """
        Description: Selects all the unlocated episodes. That means every episode where the opening and ending have not been located

        Return Value: List of Episodes
        """
        unlocated_episodes = []

        # Check every episode to see if it's unlocated
        for episode_path in self.episodes.keys():
            if self.episodes[episode_path].opening == None and self.episodes[episode_path].ending == None:
                unlocated_episodes.append(self.episodes[episode_path])
        
        return unlocated_episodes

    def get_random_located_episodes(self, num_episodes: int) -> list:
        """
        Description: Selects a random sample of located episodes

        Parameters: 
            - num_episodes: Amount of episodes to select

        Return Value: List of Episodes
        """
        # Get all located episodes
        located_episodes = self.get_all_located_episodes()

        # Check if there are enough located episodes
        if len(located_episodes) < num_episodes:
            # TODO: Raise exception (There are not that many located episodes)
            return []
        
        # Select x randomly
        return sample(located_episodes,num_episodes)

    def get_random_fully_located_episodes(self, num_episodes: int) -> list:
        """
        Description: Selects a random sample of fully located episodes

        Parameters: 
            - num_episodes: Amount of episodes to select

        Return Value: List of Episodes
        """
        # Get all fully located episodes
        located_episodes = self.get_all_fully_located_episodes()

        # Check if there are enough fully located episodes
        if len(located_episodes) < num_episodes:
            # TODO: Raise exception (There are not that many fully located episodes)
            return []
        
        # Select x randomly
        return sample(located_episodes,num_episodes)

    def get_random_opening(self) -> Chunk:
        """
        Description: Selects the opening of a random episode

        Return Value: Chunk containing an opening
        """
        # Get random fully located episode
        ref_episode = self.get_random_fully_located_episodes(1)[0]

        # Return opening
        return ref_episode.opening
    
    def get_random_ending(self) -> Chunk:
        """
        Description: Selects the ending of a random episode

        Return Value: Chunk containing an ending
        """
        # Get random fully located episode
        ref_episode = self.get_random_fully_located_episodes(1)[0]

        # Return ending
        return ref_episode.ending

    def get_episode_list(self) -> list:
        """
        Description: Returns the list of episodes in order
        """
        episode_list = []
        for path in self.episode_order:
            episode_list.append(self.episodes[path])
        
        return episode_list

    def add_openings(self, openings: list):
        """
        Description: Adds a list of opening chunks

        Parameters:
            - openings: List of Chunks with the openings from different episodes
        """
        for opening in openings:
            self.episodes[opening.episode.path].opening = opening

    def add_endings(self, endings: list):
        """
        Description: Adds a list of ending chunks

        Parameters:
            - endings: List of Chunks with the endings from different episodes
        """
        for ending in endings:
            self.episodes[ending.episode.path].ending = ending

    def save_episodes_info(self, output_path: str):
        """
        Description: Saves the information gathered from the episodes in a file in json format

        Parameters:
            -output_path: Valid path of the file to be written with the information
        """
        # Build output info dictionary
        episode_info={}
        episode_info["episode_order"]=self.episode_order
        episode_info["episodes"]={}
        for e_path in self.episodes:
            e=self.episodes[e_path]
            episode_info["episodes"][e.path]={}
            if e.opening:
                episode_info["episodes"][e.path]["opening"]=[e.opening.start_frame, e.opening.end_frame]
            if e.ending:
                episode_info["episodes"][e.path]["ending"]=[e.ending.start_frame, e.ending.end_frame]

        # Open output file. Rewrite if exists
        with open(output_path, "w") as file:
            # Dump Json
            file.write(json.dumps(episode_info))
            
    def load_episodes_info(self, input_path: str):
        """
        Description: Loads the information from the episodes into the program from a file in json format

        Parameters:
            -input_path: Valid path of the file to load the information from
        """
        # Load input info into dictionary
        with open(input_path, "r") as file:
            # Load Json
            episode_info=json.load(file)

        # Prepare openings and endings lists
        openings=[]
        endings=[]

        # Insert info in DAO
        for e_path in episode_info["episode_order"]:
            # Add episode in order
            self.add_episode(e_path)

            # Save Opening Chunk
            if "opening" in episode_info["episodes"][e_path]:
                openings.append(Chunk(self.episodes[e_path], *episode_info["episodes"][e_path]["opening"]))
            
            # Save Ending Chunk
            if "ending" in episode_info["episodes"][e_path]:
                endings.append(Chunk(self.episodes[e_path], *episode_info["episodes"][e_path]["ending"]))
        self.add_openings(openings)
        self.add_endings(endings)
