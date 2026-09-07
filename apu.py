#Audio Processing Unit

import numpy as np

class APU:
    CPU_CLOCK = 4194304 #Hertz
    SAMPLE_RATE = 44100 #APU Hz

    def __init__(self):

        #Channel 2: $FF16 - $FF19
        self.nr21= 0x00     #Sound length, duty
        self.nr22= 0x00     #Volume envelope
        self.nr23= 0x00     #Frequency, lower 8 bits
        self.nr24= 0x00     #Frequency, upper 3 bits + trigger + length enable

        #Master Volume - $FF24
        self.nr50= 0x00

        #Channel Panning/Routing - $FF25
        self.nr51= 0x00

        # Mute / unmute - $FF26
        self.nr52= 0x00

        #CH2 state

        self.ch2_enabled = False
        self.ch2_timer = 0
        self.ch2_phase = 0

        self.ch2_period = 4
        #Timing

        self._sample_clock = 0.0
        #self._sample_period = self.CPU_CLOCK / self.SAMPLE_RATE
        self._sample_period = 1048576 / self.SAMPLE_RATE

        self._samples =[] #samples waiting for output

        

    def rb(self,addr):
        if addr == 0xFF16:
            return self.nr21

        if addr == 0xFF17:
            return self.nr22

        if addr == 0xFF18:
            return self.nr23

        if addr == 0xFF19:
            return self.nr24

        if addr == 0xFF24:
            return self.nr50

        if addr == 0xFF25:
            return self.nr51

        if addr == 0xFF26:
            return self.nr52

        return 0xFF

    def wb(self, addr, val):

        val &= 0xFF

        if addr == 0xFF16:
            self.nr21 = val

        elif addr == 0xFF17:
            self.nr22 = val

        elif addr == 0xFF18:
            self.nr23 = val
            self._update_ch2_period()

        elif addr == 0xFF19:
            self.nr24 = val
            self._update_ch2_period()

            #Bit 7 acts as a trigger
            if val&0x80:
                self.trigger_channel_2()

        if addr == 0xFF24:
            self.nr50 = val

        if addr == 0xFF25:
            self.nr51 = val

        if addr == 0xFF26:
            self.nr52 = val & 0x80 #DEBUG: temp, only keep master enable bit


    #######################################################################
    # Channel 2
    #######################################################################

    def get_ch2_frequency(self):
        return ((self.nr24 & 0x07) << 8) | self.nr23

    def get_ch2_frequency_hz(self):
        freq = self.get_ch2_frequency()

        if freq>=2048:
            return 0

        return 131072/( 2048-frequency)


    def trigger_channel_2(self):
        self.ch2_enabled = True

        freq = self.get_ch2_frequency()

        '''if freq:
            self.ch2_timer = (2048 -freq) *4
        else:
            self.ch2_timer = 4'''

        if freq >=2048:
            self.ch2_period = 4
        else:
            self.ch2_period = (2048 - freq) #* 4

        self.ch2_timer = self.ch2_period
        self.ch2_phase = 0

    def get_ch2_duty(self):
        #NR21, top 2 bits
        return (self.nr21 >> 6) & 0x03

    def get_ch2_volume(self):
        #Nr22 top 4 bits
        return (self.nr22 >>4) & 0x0F

    def get_ch2_wave_bit(self):
        #turn Duty into the correct Patterns, then extract where in the pattern
        patterns = (
            0b00000001,     #12.5%
            0b10000001,     #25%
            0b10000111,     #50%
            0b01111110,     #75%
        )
        pattern = patterns[self.get_ch2_duty()]

        bit = 7 - self.ch2_phase
        return (pattern >>bit) & 1

    def _update_ch2_period(self):
        freq = self.get_ch2_frequency()

        if freq >= 2048:
            self.ch2_period = 4
        else:
            self.ch2_period = (2048 - freq) #*4
    #######################################################################
    # APU Clock
    #######################################################################

    '''def step(self, cycles):
        #Advance the APU by the number of M cycles passed.

        if not (self.nr52 & 0x80): #mute
            return
        
        for i in range(cycles):
            self._step_one()'''

    def step(self, cycles):
        if not (self.nr52 & 0x80):
            return

        # Advance the sample clock.
        self._sample_clock += cycles

        # Advance CH2 timer.
        if self.ch2_enabled:
            self.ch2_timer -= cycles

        # Most instructions end here.
        if (
            self._sample_clock < self._sample_period
            and (not self.ch2_enabled or self.ch2_timer > 0)
        ):
            return

        # Handle events that were crossed.
        while self._sample_clock >= self._sample_period:
            self._sample_clock -= self._sample_period
            self._generate_sample()

        if self.ch2_enabled:
            while self.ch2_timer <= 0:
                self.ch2_timer += self.ch2_period
                self.ch2_phase = (self.ch2_phase + 1) & 7




    def _step_one(self):

        ### Ch2 Frequency Timer ###

        if self.ch2_enabled:
            self.ch2_timer -= 1

            if self.ch2_timer <= 0:
                frequency = self.get_ch2_frequency()
                period = (2048-frequency) #*4

                if period<=0:
                    period = 4

                self.ch2_timer = period
                self.ch2_phase = (self.ch2_phase +1) &7

        ### Generate Sample ###

        self._sample_clock += 1

        if self._sample_clock >= self._sample_period:
            self._sample_clock -= self._sample_period
            self._generate_sample()


    #######################################################################
    # Audio Mixing
    #######################################################################

    def _generate_sample(self):

        if not self.ch2_enabled:
            self._samples.append((0.0,0.0))
            return

        volume = self.get_ch2_volume()

        if volume == 0:
            value = 0.0
        else:
            wave = self.get_ch2_wave_bit()

            if wave:
                value = volume/15.0
            else:
                value = -(volume / 15.0)

        left = 0.0
        right= 0.0

        #NR51:
        # bit 1 = CH2 Right
        # bit 5 = CH2 Left

        if self.nr51 & 0x02:
            right+=value

        if self.nr51 & 0x20:
            left+=value

        #NR50:
        # bits 2-0: right volume
        # bits 6-4: left volume

        r_volume = self.nr50 & 0x07
        l_volume = (self.nr50 >>4) &0x07

        right *= r_volume/7.0
        left *= l_volume/7.0

        #cast from [0,1] to [-1,1]

        #right = right * 2.0 - 1.0
        #left = left * 2.0 - 1.0

        self._samples.append((left,right))

    #######################################################################
    # Audio Output
    #######################################################################

    def get_samples(self):
        #Return numpy array (N,2) with all stereo samples, clears queue

        if not self._samples:
            #return np.empty((0,2), dtype=np.float32)
            return None

        samples = np.asarray(self._samples, dtype= np.float32)
        self._samples.clear()

        return samples

import pygame
import queue
#from pygame._sdl2 import AudioDevice, AUDIO_F32
class AudioOutput:

    SAMPLE_RATE = 44100
    CHANNELS = 2
    CHUNK_SIZE = 1024

    def __init__(self):
        pygame.mixer.init(
            frequency = self.SAMPLE_RATE,
            size=-16,
            channels = self.CHANNELS,
            buffer = 512
        )

        self._sound = None
        self._channel=None
        self._queue = np.empty((0,2),dtype=np.float32)

        self._sounds = [] #keep Sound objects alive

    def push(self, samples):

        if samples is None or len(samples) == 0:
            return

        self._queue = np.concatenate((self._queue, samples))

        self._play()

    def _make_sound(self,samples):

        pcm = np.clip(samples, -1.0, 1.0)
        pcm = (pcm * 32767).astype(np.int16)

        return pygame.sndarray.make_sound(pcm)
    
    def _play(self):
        #If already playing, don't replace.
        if self._channel is not None and self._channel.get_busy():
            return

        #if len(self._queue)==0:
        #    return

        if len(self._queue) < 2048:
            return

        
        count = min(len(self._queue),2048)

        samples = self._queue[:count]
        self._queue = self._queue[count:]

        #convert Float to 16 bit signed PCM

        pcm = np.clip(samples, -1.0, 1.0)
        pcm = (pcm * 32767).astype(np.int16)

        self._sound = pygame.sndarray.make_sound(pcm)

        #self._sound.play()
        self._channel = self._sound.play()


            
    def update(self):
        self._play()

        '''#cull dead queue
        if self._channel is not None:
            queued = self._channel.get_queue()

            if queued is None:
                if not self._channel.get_busy():
                    self._sounds.clear()
                elif self._sounds:
                    self._sounds = self._sounds[-1:]'''

    def close(self):
        pygame.mixer.quit()
