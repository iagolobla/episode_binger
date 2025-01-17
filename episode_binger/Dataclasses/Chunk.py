from episode_binger.Dataclasses.Episode import Episode

class Chunk():
    """
    Class that represents a video chunk and holds its information
    """
    def __init__(self, episode: Episode, start_frame: int, end_frame: int):
        """
        Description: Creates a new chunk

        Parameters:
            - episode: Episode object where the chunk belongs
            - start_frame: First frame of the chunk
            - end_frame: Last frame of the chunk
        """
        self.episode = episode
        self.start_frame = start_frame
        self.end_frame = end_frame

    def __str__(self):
        return f"Chunk({self.episode.path}):[{self.start_frame},{self.end_frame}]"
    
    def isOpening(self):
        """
        Description: Determines if a chunk is an opening or an ending based in its position within the episode

        Return Value: True if the chunk is an opening, False if it is an ending
        """
        return self.start_frame < (self.episode.frame_count-self.end_frame)