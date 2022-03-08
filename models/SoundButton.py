import pygame
from dataclasses import dataclass

# IsPlaying toggles sound if looping is true and hold is false
# if Hold is True, button only plays when held down
# -1 for infinite looping any other int for that number of loops plus one
@dataclass
class SoundButton:
    Sound : ...
    State : bool = False     # If the sound is being played
    IsMuteable : bool = True 
    NumLoops : int = -1
    Toggle : bool = False

    def __init__(self, soundPath):
        self.Sound = pygame.mixer.Sound(soundPath)
