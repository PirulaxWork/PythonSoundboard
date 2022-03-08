from asyncore import loop
from codecs import lookup_error
from operator import truediv
from typing import Any, List
from dataclasses import dataclass
from typing_extensions import assert_never

import pygame
from .models.Sound import Sound
from .models.SubSampleRecording import SubSampleRecording
from .models.SubSampleRecording import SoundPart
from pygame import time

@dataclass
class OneRecordedSound:
    parts : List[SoundPart] # All the parts necessary to represent this recorded sound - Should be played sequencially (Eg.: One after another)
    active_part_idx = 0
    active = False
    start_tick : int = 0 # Tick wh en the recording of this sound began

    def play(self):
        self.active = True
        self.parts[0].play()

    # If False is returned the playback has finished (or wasnt even started)
    def update(self):
        if not self.active:
            return False

        if self.parts[self.active_part_idx].active:
            return True

        # Go to next part..
        self.active_part_idx += 1
        if self.active_part_idx < len(self.parts):
            self.active = False
            return False # No more parts

        # Start playing next part
        self.parts[self.active_part_idx].play()
        return True

# Handles recording of one sound
class OneSoundRecorder:
    path : str                      # Path of this sound
    sound_duration : int            # Total length/duration of the sound
    record_start_tick : int         # PyGame ticks when the recording of this sound began
    begin_play_pos : float          # Play position when the recording started


    def __init__(self, sound : Sound):
        self.path = sound.path
        self.sound_duration = sound.duration
        self.record_start_tick = pygame.time.get_ticks()
        self.begin_play_pos = sound.curr_pos

    # Convert this recording into a `RecordedSound` object
    def to_recording(self):
        rec = OneRecordedSound()

        rec.start_tick = self.record_start_tick
        total_playtime = (pygame.time.get_ticks() - self.record_start_tick) / 1000 # Total playtime in ms
        rec.parts.append(SoundPart(self.path, self.begin_play_pos, self.sound_duration)) # First part (always present)
        loop_count = self.sound_duration // total_playtime # How many times the sound was looped over
        if loop_count > 1: 
            for _ in range(loop_count): # Add whole parts in-between
                rec.parts.append(SoundPart(self.path, 0, self.sound_duration)) 
            rec.parts.append(SoundPart(self.path, 0, total_playtime % self.sound_duration)) # Last part
        elif loop_count == 0: # Total playtime < sound_duration
            if self.begin_play_pos + total_playtime > self.sound_duration: # Check if sound wrapped over once (Eg.: `current_pos < begin_play_pos`)
                rec.parts.append(SoundPart(self.path, 0, self.sound_duration - (self.begin_play_pos + total_playtime))) 
        
class Recording:
    def __init__(self, base_tick, subsamples):
        self.subsamples = subsamples
        self.active = False
        self.play_begin_tick = pygame.time.get_ticks()
        self.base_tick = base_tick # The tick all parts are relative to
        self.last_scanned_idx = 0

    def update(self):
        # Start playing next sounds
        for i in range(self.last_scanned_idx, len(self.subsamples)):
            if self.subsamples[i].start_tick - self.base_tick <= pygame.time.get_ticks() - self.play_begin_tick:
                break
            self.last_scanned_idx = i
            self.subsamples[i].play()

        for s in self.subsamples[:self.last_scanned_idx]:
            s.update()

    def play(self):
        if not self.active:
            self.active = True
            self.update()

    
        
        
        
 
        
# Sound recorder - starts recording as soon as it's constructed
# have to call `add_sound` immediately after construction to add sounds to be recorded
# `update` should be called repeatedly.
class Recorder:
    def __init__(self):
        self.recored_sounds = {} # Sounds that are being recorded right now
        self.subsamples = []     # The final track basically
        self.start_tick = pygame.time.get_ticks()

    def update(self):
        for s, e in self.recored_sounds:
            if not s.active: # Check if any of the sounds is not active anymore 
                self.remove_sound(s)
        
    def stop_recording(self):
        # Finish up all sounds being recorded
        for s, e in self.recored_sounds:
            self.remove_sound(s)

    # Add a new sound to the recording
    def add_sound(self, sound : Sound):
        assert sound not in self.recored_sounds
        self.recored_sounds[sound] = OneSoundRecorder(sound)

    # Remove a previously added sound from the recording
    def remove_sound(self, sound):
        try: # Might happen sound was remove already, but that's fine
            e = self.recored_sounds[sound]
            self.subsamples.append(e.to_recording()) # Convert to recording and append
            del e # Remove entry from dict
        except KeyError:
            pass
