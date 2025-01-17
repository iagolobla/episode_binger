import cv2 as cv
import numpy as np

class Episode():
    """
    Class that represents an episode an holds its information
    """
    def __init__(self, path: str):
        """
        Description: Creates a new Episode

        Parameters:
            - path: Valid path of the episode to load
        """
        self.path = path
        cap=cv.VideoCapture(path)
        width  = cap.get(cv.CAP_PROP_FRAME_WIDTH)
        height  = cap.get(cv.CAP_PROP_FRAME_HEIGHT)
        self.frame_count = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
        self.frame_shape = (int(height), int(width),3)
        self.fps = cap.get(cv.CAP_PROP_FPS)
        cap.release()

        self.opening = None
        self.ending = None

    def __eq__(self, other):
        return self.path == other.path

    def __str__(self):
        return f"Episode({self.path}): Opening:{self.opening}, Ending:{self.ending}"

    def load_frame_list(self, indexes: list, thumbnail_resolution: tuple, reversed_list: bool, output_frames: list):
        """
        Description: Function meant for threads that loads the frames in the given output_frames list

        Parameters:
            - indexes: List of frame indexes to load
            - thumbnail_resolution: Thumbnail dimensions for frame processing
            - reversed_list: Flag to indicate if the frame list should be reversed
            - output_frames: Output parameter that holds the list with the loaded frames

        Return Value: List of loaded frames
        """
        cap = cv.VideoCapture(self.path)
        for index in indexes:
            cap.set(1,index)    # Set frame to start
            ret, frame = cap.read()
            frame=cv.resize(frame,(thumbnail_resolution[1],thumbnail_resolution[0]),interpolation=cv.INTER_AREA)
            output_frames.append(frame.astype(np.int16))
        
        cap.release()
        if reversed_list:
            output_frames.reverse()

        return output_frames

    def load_consecutive_frames(self, start_frame_index: int, number_of_frames: int, thumbnail_resolution: tuple, reversed_list: bool, output_frames: list):
        """
        Description: Function meant for threads that loads the frames in the given output_frames list

        Parameters:
            - start_frame_index: Index of the first frame to load
            - number_of_frames: Amount of frames to load
            - thumbnail_resolution: Performance Parameter. It's the size to resize frames. Generally, the lower the better but a 10th part from the original resolution should be fine.
            - output_frames: Output parameter that holds the list with the loaded frames

        Return Value: List of loaded frames
        """
        cap = cv.VideoCapture(self.path)
        cap.set(1,start_frame_index)    # Set frame to start
        for i in range(number_of_frames):
            ret, frame = cap.read()
            frame=cv.resize(frame,(thumbnail_resolution[1],thumbnail_resolution[0]),interpolation=cv.INTER_AREA)
            output_frames.append(frame.astype(np.int16))
            
        cap.release()
        if reversed_list:
            output_frames.reverse()

        return output_frames