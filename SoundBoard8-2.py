import imp
import sys
from typing import Tuple
from xml.sax import make_parser
import pygame
import pprint
from pygame.locals import *
from dataclasses import dataclass

from SubSampleRecorder import Recorder
from .models import SoundButton

# Init pygame
pygame.init()
pygame.display.set_caption('Soundboard')
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()

# Sound Buttons - Main array index is the joystick instance_id, inner array is the button id
sound_buttons = [
    [
        SoundButton('Loops/130BPM/ET_130_C_UKGSnareLoop_4bars_Beats_130BPM_BANDLAB.wav'),
        SoundButton('Loops/130BPM/ET_130_C_UKGPercLoop_4bars_Beats_130BPM_BANDLAB.wav'),
        SoundButton('Loops/130BPM/ET_130_C_UKGKickLoop_4bars_Beats_130BPM_BANDLAB.wav'),
        SoundButton('Loops/130BPM/ET_130_C_UKGHatLoop_4bars_Beats_130BPM_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Gold_108_Emin_SynthPad01_4bar_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Gold_108_Emin_LeadPad_4bar_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Gold_108_Emin_SubBass1_4bar_BANDLAB.wav'),
        SoundButton('Loops/130BPM/ts_128_Em_Pad_LoFi_8bars_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Chill03_85_Em_EPChords6_8bar_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Chill04_90_Em_VinylNoise_4bar_Fx_BANDLAB.wav'),
    ],
    [
        SoundButton('Loops/130BPM/YouBrokeMe_130_Fm_Kick_BANDLAB.wav'),
        SoundButton('Loops/130BPM/YouBrokeMe_130_Fm_RetroSnare_BANDLAB.wav'),
        SoundButton('Loops/130BPM/YouBrokeMe_130_Fm_Bass_BANDLAB.wav'),
        SoundButton('Loops/130BPM/YouBrokeMe_130_Fm_Strings_BANDLAB.wav'),
        SoundButton('Loops/130BPM/YouBrokeMe_130_Fm_NylonGuitar_BANDLAB.wav'),
        SoundButton('Loops/130BPM/YouBrokeMe_130_Fm_HighNylon_BANDLAB.wav'),
        SoundButton('Loops/130BPM/YouBrokeMe_130_Fm_MoonGuitar_BANDLAB.wav'),
        SoundButton('Loops/130BPM/YouBrokeMe_130_Fm_LowFlute_BANDLAB.wav'),
        SoundButton('Loops/130BPM/YouBrokeMe_130_Fm_HighFlute_BANDLAB.wav'),
        SoundButton('Loops/120BPM/Malarkey_120_Am_Piano3_4bar_BANDLAB.wav'),
    ],
    [
        SoundButton('Loops/130BPM/Toxic_130_Gm_Trumpet_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Toxic_130_Gm_LongTrumpet_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Toxic_130_Gm_Saxophone_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Toxic_130_Gm_RetroPiano_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Toxic_130_Gm_LeadKey_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Toxic_130_Gm_GrandPiano_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Vox_BB_127_Emin_pluck_vocal_8_4_4_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Synth_BB_120_Emin_synth_4_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Keys_BB_140_Fmin_keys_synth_8_4_4_BANDLAB.wav'),
    ],
    [
        SoundButton('Loops/130BPM/PT_135_Cm_Arp_04_8bars_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Kit2_LeadChords3_C_128_8bar_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Kit2_LeadChords2_C_128_8bar_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Kit2_LeadChords1_C_128_8bar_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Kit2_LeadChords_C_128_4bar_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Kit2_LeadSynth1_C_128_8bar_BANDLAB.wav'),
        SoundButton('Loops/130BPM/Kit2_FilterChords_C_128_4bar_BANDLAB.wav'),
        SoundButton('Loops/130BPM/NM_Mux_Kick_124_BANDLAB.wav'),
        SoundButton('Loops/130BPM/DMH_Kit_01_DR_TopLoop_01_126bpm_BANDLAB.wav'),
    ]
]

# If the toggle mode is on right now
in_toggle_mode = False

# If the mixer is paused right now
is_mixer_paused = False


pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joystick in joysticks:
    print(joystick.get_name())

print("joysticks:")
pprint.pprint(joysticks)

pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 30) 

sound_recorder = None
recorded_sound = None

# event - The pygame event
# button_state - True if "down", False if "up"
def process_button_event(event, button_state):
    global in_toggle_mode
    global is_mixer_paused

    if event.button == 9 and event.instance_id == 2: # Pause/unpause mixer
        is_mixer_paused = not is_mixer_paused # TODO
        if is_mixer_paused:
            pygame.mixer.pause()
        else:
            pygame.mixer.unpause()
            
    elif event.button == 9 and event.instance_id == 3: # Mute/unmute all
        for row in sound_buttons:
            for button in row:
                if button.IsMuteable:
                    button.Sound.set_volume(1 if button_state else 0)

    elif event.button == 9 and event.instance_id == 0: # Toggle toggle_mode state
        in_toggle_mode = button_state
    elif event.button == 9 and event.instance_id == 1: # Start recorder
        if button_state:
            # Create recorder instance
            sound_recorder = Recorder()

            # Add all currently playing sounds to the recording
            for row in sound_buttons:
                for button in row:
                    if button.Sound.active:
                        sound_recorder.add_sound(button.Sound)
        else:
            sound_recorder.
    else:
        try:
            button = sound_buttons[event.instance_id][event.button]
            if in_toggle_mode: # In toggle mode just toggle state
                if button_state: # Ignore button up
                    button.State = not button.State # Flip state
                    if button.State: 
                        button.Sound.play()
                        if sound_recorder:
                            sound_recorder.add_sound(button.Sound)
                    else: 
                        button.Sound.stop()
                        if sound_recorder:
                            sound_recorder.remove_sound(button.Sound)
            else:
                if button.State != button_state:
                    if button_state:
                        button.Sound.stop()
                        button.Sound.play()
                        if sound_recorder:
                            sound_recorder.add_sound(button.Sound)
                    else:
                        button.Sound.stop()
                        if sound_recorder:
                            sound_recorder.remove_sound(button.Sound)

        except IndexError:
            print(f"Button {event.button} [instance_id: {event.instance_id}] not yet implemented!")


# Main render loop
while True:
    # Render toggle mode text
    screen.fill((0, 0, 0))
    screen.blit(font.render(f"in_toggle_mode: {in_toggle_mode}", True, (255, 255, 255)), (0,0))

    # Process pygame events
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP: # Process button event
            process_button_event(event, event.type == pygame.JOYBUTTONDOWN)

        elif event.type == pygame.JOYDEVICEADDED or event.type == pygame.JOYDEVICEREMOVED: # Update joysticks
            joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            
        elif event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): # Quit if event is QUIT or if ESCAPE is pressed
            pygame.quit()
            sys.exit()

    # Update pygame
    pygame.display.update()
    if sound_recorder:
        sound_recorder.update()
    clock.tick(60)