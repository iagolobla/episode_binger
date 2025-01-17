import ffmpeg

class Video_Assembler:
    """
    Class that creates a video from a specification
    """
    def __init__(self):
        pass

    def create_video(self, chunk_list: list, result_video_path: str):
        """
        Description: Creates a video file containing the specified video chunks

        Parameters:
            - chunk_list: A list of Chunk objects that define what chunks of video should be included and their order
            - result_video_path: A valid path to save the result video
        """
        # Create video clips and audio clips
        video_clips = []

        # Open every chunk's episode to trim corresponding clip
        for chunk in chunk_list:
            # Open episode
            video = ffmpeg.input(chunk.episode.path)

            # Trim video
            video_clips.append(video.trim(start=chunk.start_frame/chunk.episode.fps, end=chunk.end_frame/chunk.episode.fps).setpts('PTS-STARTPTS'))

            # Trim audio
            video_clips.append(video.filter_('atrim', start = chunk.start_frame/chunk.episode.fps, end = chunk.end_frame/chunk.episode.fps).filter_('asetpts', 'PTS-STARTPTS'))

        # Build video from clips
        final_video = ffmpeg.concat(*video_clips,v=1, a=1)

        # Write the video into a file
        ffmpeg.output(final_video,result_video_path, preset='veryfast').overwrite_output().run()
