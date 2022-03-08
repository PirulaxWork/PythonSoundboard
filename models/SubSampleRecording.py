from dataclasses import dataclass
from typing import List, Optional, Union
from xmlrpc.client import boolean
import just_playback as jpb
from . import Sound

# Part of a sound. Eg.: From the 10th second to the 15th
class SoundPart(Sound):
    begin_pos : float # In seconds
    end_pos : float   # In seconds


    #playcount : int   # How many times to play it

    #playtime_total : float   # Total playtime, if more than the length of the sound or `end_pos < begin_pos` the sound will be played more than once

    def __init__(self, path, rec_begin_pos, rec_end_pos):
        super().__init__(path)

        self.begin_pos = rec_begin_pos
        self.end_pos = rec_end_pos
        

    def play(self):
        if self.active: # Already playing?
            return

        #self.looped = loop

        #self.playback = jpb.Playback(self.path)
        #assert(self.playback) # Check if Playback object could be created
        self.play()
        self.seek(self.begin_pos) # Seek to where the recording beginning is
        #self.loop_at_end(self.looped) # Update loop attribute of Playback
        
    # Update the playback
    # Should be called in the update loop 
    # It wraps the audio play pos to be between [begin, end]
    def update(self):
        if not self.active: # Sound ended
            return
        
        # Check if we should stop the playback
        if self.curr_pos >= self.end_pos:
            self.end_pb()

        # Looping
        #if self.curr_pos < self.begin_pos or self.curr_pos > self.end_pos:
        #    self.seek(self.begin_pos) # Wrap back to beginning 


""" # A recoding - contains all sounds that were playing at the momment it was created
@dataclass
class SubSampleRecording:
    parts : List[SoundPart]
    active : bool = False             # Is it active right now (Are the sounds being played back)

    
    def add_sound()

    # Start playing all recorded sounds
    def start_all(self, loop = True):
        if self.active:
           return

        # Start all samples
        for part in self.parts:
            part.start_pb(loop)

    # Stop all sounds playing currently (Has no effect if nothing is playing)
    def stop_all(self):
        for part in self.parts:
            part.stop_pb()

    def update(self):
        for part in self.parts:
            part.update_pb()
 """