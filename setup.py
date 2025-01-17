from setuptools import setup, find_packages

setup(
    name="episode_binger",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "ffmpeg-python",
        "opencv-python"
    ],
    author="Iago Loureiro Blanco",
    author_email="iagoloureiroblanco@gmail.com",
    description="A python package to take episodes, remove openings and endings and join them all with an initial opening and a last ending",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/iagolobla/episode_binger",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)