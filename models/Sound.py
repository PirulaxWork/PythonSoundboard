import just_playback as jpb
#from dataclasses import dataclass
#from typing import Optional

# Just a little wrapper around Playback to store the path as well
class Sound(jpb.Playback):
    path : str # Sound's path

    def __init__(self, path):
        super().__init__(path)
        self.path = path