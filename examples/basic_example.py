import episode_binger

if __name__ == "__main__":
    # Create episode binger object
    eb = episode_binger.Episode_Binger()

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
