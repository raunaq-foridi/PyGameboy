#Audio Processing Unit

import numpy as np

class APU:
    CPU_CLOCK = 4194304 #Hertz
    SAMPLE_RATE = 44100 #APU Hz

    def __init__(self):

        #Channel 1:
        self.nr10= 0x00     #Frequency Sweep
        self.nr11= 0x00     #Sound length, duty
        self.nr12= 0x00     #Volume envelope
        self.nr13= 0x00     #Frequency, lower 8 bits
        self.nr14= 0x00     #Frequency, upper 3 bits + trigger + length enable

        
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

        #CH1 state
        self.ch1_enabled = False
        self.ch1_timer = 0
        self.ch1_phase = 0
        
        self.ch1_period = 4

                
        #CH2 state

        self.ch2_enabled = False
        self.ch2_timer = 0
        self.ch2_phase = 0

        self.ch2_period = 4

        #Envelope state
        self.ch1_volume = 0
        self.ch1_envelope_timer = 0
        
        self.ch2_volume = 0
        self.ch2_envelope_timer = 0

        #Length counter
        self.ch1_length_counter = 64
        self.ch2_length_counter = 64
        #Frame Sequencer
        self.frame_seq_step = 0
        self._prev_div_bit4 = 0
        
        #Timing

        self._sample_clock = 0.0
        #self._sample_period = self.CPU_CLOCK / self.SAMPLE_RATE
        self._sample_period = 1048576 / self.SAMPLE_RATE

        self._samples =[] #samples waiting for output

        
    def _power_off(self):
        #instant full zero
        return
        self.nr10 = 0x00
        self.nr11 = 0x00
        self.nr12 = 0x00
        self.nr13 = 0x00
        self.nr14 = 0x00
        
        self.nr21 = 0x00
        self.nr22 = 0x00
        self.nr23 = 0x00
        self.nr24 = 0x00

        self.nr50 = 0x00
        self.nr51 = 0x00

        self.ch1_enabled = False
        self.ch1_timer = 0
        self.ch1_phase = 0
        self.ch1_period = 4
        self.ch1_volume = 0
        self.ch1_envelope_timer = 0

        self.ch2_enabled = False
        self.ch2_timer = 0
        self.ch2_phase = 0
        self.ch2_period = 4
        self.ch2_volume = 0
        self.ch2_envelope_timer = 0
        
    def rb(self,addr):

        #Channel 1
        if addr == 0xFF10:
            return self.nr10
        
        if addr == 0xFF11:
            return self.nr11

        if addr == 0xFF12:
            return self.nr12

        if addr == 0xFF13:
            return self.nr13

        if addr == 0xFF14:
            return self.nr14

        #Channel 2
        if addr == 0xFF16:
            return self.nr21

        if addr == 0xFF17:
            return self.nr22

        if addr == 0xFF18:
            return self.nr23

        if addr == 0xFF19:
            return self.nr24

        #Controllers
        if addr == 0xFF24:
            return self.nr50

        if addr == 0xFF25:
            return self.nr51

        if addr == 0xFF26:
            #bit7: master enable
            #bits 6-4 unused, read as 1
            #bit 3-0: per-channel status; CH4 to CH1 respectively
            status = 0x0
            if self.ch1_enabled:
                status|= 0x01
            if self.ch2_enabled:
                status|= 0x02
            return (self.nr52 & 0x80) | 0x70 | status

        return 0xFF

    def wb(self, addr, val):
    
        val &= 0xFF

        power_on = bool(self.nr52 & 0x80)
        #if not power_on:
            #return

        #Channel 1
        
        if addr == 0xFF11:
            #print("a")
            self.nr11 = val

            self.ch1_length_counter =  64 - (val & 0x3F)

        elif addr == 0xFF12:
            self.nr12 = val

            #Top 5 bits==0 is DAC-off
            if (val & 0xF8) == 0:
                self.ch1_enabled = False

        elif addr == 0xFF13:
            self.nr13 = val
            self._update_ch1_period()

        elif addr == 0xFF14:
            self.nr14 = val
            self._update_ch1_period()

            #Bit 7 acts as a trigger
            if val&0x80:
                self.trigger_channel_1()

        #Channel 2
        if addr == 0xFF16:
            self.nr21 = val

            self.ch2_length_counter =  64 - (val & 0x3F)

        elif addr == 0xFF17:
            self.nr22 = val

            #Top 5 bits==0 is DAC-off
            if (val & 0xF8) == 0:
                self.ch2_enabled = False

        elif addr == 0xFF18:
            self.nr23 = val
            self._update_ch2_period()

        elif addr == 0xFF19:
            self.nr24 = val
            self._update_ch2_period()

            #Bit 7 acts as a trigger
            if val&0x80:
                self.trigger_channel_2()
                
        #Controllers
        if addr == 0xFF24:
            self.nr50 = val

        if addr == 0xFF25:
            self.nr51 = val

        if addr == 0xFF26:
            #was_on = bool(self.nr52 & 0x80)
            #now_on = bool(val &0x80)
            self.nr52 = val & 0x80 #DEBUG: temp, only keep master enable bit

            #if was_on and not now_on:
            #    self._power_off()

            #return

    #######################################################################
    # Channel 1
    #######################################################################

    def get_ch1_frequency(self):
        return ((self.nr14 & 0x07) << 8) | self.nr13

    def get_ch1_frequency_hz(self):
        freq = self.get_ch1_frequency()

        if freq>=2048:
            return 0

        return 131072/( 2048-freq)


    def trigger_channel_1(self):

        #DAC off (top 5 bits of NR12 zero) forces channel off
        if (self.nr12 & 0xF8) == 0:
            self.ch1_enabled = False
            return
        
        self.ch1_enabled = True

        freq = self.get_ch1_frequency()

        if freq >=2048:
            self.ch1_period = 4
        else:
            self.ch1_period = (2048 - freq) #* 4

        self.ch1_timer = self.ch1_period
        self.ch1_phase = 0

        #Envelope reload if triggered
        self.ch1_volume = (self.nr12 >>4) & 0x0F
        pace = self.nr12 & 0x07
        self.ch1_envelope_timer = pace if pace!=0 else 8 #0 treated as 8, never fires

        if self.ch1_length_counter==0:
            self.ch1_length_counter = 64

    def get_ch1_duty(self):
        #NR11, top 2 bits
        return (self.nr11 >> 6) & 0x03

    def get_ch1_volume(self):
        return self.ch1_volume

    def get_ch1_wave_bit(self):
        #turn Duty into the correct Patterns, then extract where in the pattern
        patterns = (
            0b00000001,     #12.5%
            0b10000001,     #25%
            0b10000111,     #50%
            0b01111110,     #75%
        )
        pattern = patterns[self.get_ch1_duty()]

        bit = 7 - self.ch1_phase
        return (pattern >>bit) & 1
            
    def _update_ch1_period(self):
        freq = self.get_ch1_frequency()

        if freq >= 2048:
            self.ch1_period = 4
        else:
            self.ch1_period = (2048 - freq) #*4

    #######################################################################
    # Channel 2
    #######################################################################

    def get_ch2_frequency(self):
        return ((self.nr24 & 0x07) << 8) | self.nr23

    def get_ch2_frequency_hz(self):
        freq = self.get_ch2_frequency()

        if freq>=2048:
            return 0

        return 131072/( 2048-freq)


    def trigger_channel_2(self):

        #DAC off (top 5 bits of NR22 zero) forces channel off
        if (self.nr22 & 0xF8) == 0:
            self.ch2_enabled = False
            return
        
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

        #Envelope reload if triggered
        self.ch2_volume = (self.nr22 >>4) & 0x0F
        pace = self.nr22 & 0x07
        self.ch2_envelope_timer = pace if pace!=0 else 8 #0 treated as 8, never fires

        if self.ch2_length_counter==0:
            self.ch2_length_counter = 64

    def get_ch2_duty(self):
        #NR21, top 2 bits
        return (self.nr21 >> 6) & 0x03

    def get_ch2_volume(self):
        #used to be Nr22 top 4 bits (initial value). Envelope changes it.
        #return (self.nr22 >>4) & 0x0F
        return self.ch2_volume

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
    # Frame Sequencing
    #######################################################################

    def step_length_1(self):
        #called at 256Hz, steps 0,2,4,6, only if NR14 bit 6 is set

        if not self.ch1_enabled:
            return

        if not bool(self.nr14 & 0x40):
            return

        if self.ch1_length_counter >0:
            self.ch1_length_counter -=1

            if self.ch1_length_counter == 0:
                self.ch1_enabled = False


    def step_length_2(self):
        #called at 256Hz, steps 0,2,4,6, only if NR24 bit 6 is set

        if not self.ch2_enabled:
            return

        if not bool(self.nr24 & 0x40):
            return

        if self.ch2_length_counter >0:
            self.ch2_length_counter -=1

            if self.ch2_length_counter == 0:
                self.ch2_enabled = False

    def step_envelope_1(self):
        #For CH1
        #Once per envelope tick, so once every 8 sequencer step
        if not self.ch1_enabled:
            return

        pace = self.nr12 & 0x07
        if pace==0:
            return
        self.ch1_envelope_timer -= 1

        if self.ch1_envelope_timer <= 0:
            self.ch1_envelope_timer = pace

            direction_up = bool(self.nr12 & 0x08)

            if direction_up:
                if self.ch1_volume<15:
                    self.ch1_volume+=1
                else:
                    if self.ch1_volume >0:
                        self.ch1_volume -= 1

    def step_envelope_2(self):
        #For CH2
        #Once per envelope tick, so once every 8 sequencer step
        if not self.ch2_enabled:
            return

        pace = self.nr22 & 0x07
        if pace==0:
            return
        self.ch2_envelope_timer -= 1

        if self.ch2_envelope_timer <= 0:
            self.ch2_envelope_timer = pace

            direction_up = bool(self.nr22 & 0x08)

            if direction_up:
                if self.ch2_volume<15:
                    self.ch2_volume+=1
                else:
                    if self.ch2_volume >0:
                        self.ch2_volume -= 1

    def _step_frame_sequencer(self):
        #DIV bit 4 has falling edge at exactly 512Hz.
        #Peek for this to count 512Hz. Does not account for DIV resets via $FF04 yet

        if self.MMU is None:
            return

        bit4 = (self.MMU.TIMER._div >> 4) & 1

        if self._prev_div_bit4 == 1 and bit4 ==0:
            self._advance_frame_sequencer()

        self._prev_div_bit4 = bit4

    def _advance_frame_sequencer(self):
        self.frame_seq_step = (self.frame_seq_step + 1) &7

        _step = self.frame_seq_step
        #Length counter: steps 0,2,4,6
        if _step in (0,2,4,6):
            self.step_length_1()
            self.step_length_2()
        #CH1 sweep, steps 2,6
        #CH2 Enveloper: step 7
        if _step == 7:
            self.step_envelope_1()
            self.step_envelope_2()
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

        # Advance CH1, CH2 timers.
        if self.ch1_enabled:
            self.ch1_timer -= cycles
            
        if self.ch2_enabled:
            self.ch2_timer -= cycles

        # Frame Sequence check
        self._step_frame_sequencer()
        
        # Most instructions end here.
        if (
            self._sample_clock < self._sample_period
            and (not self.ch2_enabled or self.ch2_timer > 0)
            and (not self.ch1_enabled or self.ch1_timer > 0)
        ):
            return


        if self.ch2_enabled:
            while self.ch2_timer <= 0:
                self.ch2_timer += self.ch2_period
                self.ch2_phase = (self.ch2_phase + 1) & 7

        if self.ch1_enabled:
            while self.ch1_timer <= 0:
                self.ch1_timer += self.ch1_period
                self.ch1_phase = (self.ch1_phase + 1) & 7

                
        # Handle events that were crossed.
        while self._sample_clock >= self._sample_period:
            self._sample_clock -= self._sample_period
            self._generate_sample()






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

        '''if not self.ch2_enabled:
            self._samples.append((0.0,0.0))
            return'''
        
        left = 0.0
        right= 0.0

        ####CH1
        if self.ch1_enabled:
            volume = self.get_ch1_volume()
            if volume == 0:
                value = 0.0
            else:
                wave = self.get_ch1_wave_bit()

                if wave:
                    value = volume/15.0
                else:
                    value = -(volume / 15.0)

            #NR51:
            # bit 0 = CH1 Right
            # bit 4 = CH1 Left

            if self.nr51 & 0x01:
                right+=value

            if self.nr51 & 0x10:
                left+=value
        
        ####CH2
        if self.ch2_enabled:
            volume = self.get_ch2_volume()

            if volume == 0:
                value = 0.0
            else:
                wave = self.get_ch2_wave_bit()

                if wave:
                    value = volume/15.0
                else:
                    value = -(volume / 15.0)

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

    VOLUME_MULTIPLIER = 0.03

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

        pcm = np.clip(samples, -1.0, 1.0) * self.VOLUME_MULTIPLIER
        pcm = (pcm * 32767).astype(np.int16)

        return pygame.sndarray.make_sound(pcm)
    
    def _play_old(self):
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

    def _play(self):

        if len(self._queue) < self.CHUNK_SIZE:
            return

        if self._channel is None:
            self._channel = pygame.mixer.find_channel()

            if self._channel is None:
                return

        if not self._channel.get_busy():
            samples = self._queue[:self.CHUNK_SIZE]
            self._queue = self._queue[self.CHUNK_SIZE:]

            sound = self._make_sound(samples)# * self.VOLUME_MULTIPLIER
            self._sounds.append(sound)
            self._channel.play(sound)

            return

        #if something IS playing, queue the next chunk
        if self._channel.get_queue() is None:
            samples = self._queue[:self.CHUNK_SIZE]
            self._queue= self._queue[self.CHUNK_SIZE:]

            sound = self._make_sound(samples)# * self.VOLUME_MULTIPLIER

            self._sounds.append(sound)
            self._channel.queue(sound)
            
    def update(self):
        self._play()

        #cull dead queue
        if self._channel is not None:
            queued = self._channel.get_queue()

            if queued is None:
                if not self._channel.get_busy():
                    self._sounds.clear()
                elif self._sounds:
                    self._sounds = self._sounds[-1:]

    def close(self):
        pygame.mixer.quit()
