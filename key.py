import pygame
class KEY:
    def __init__(self):
        self._keys = [0x0F, 0x0F]
        self._colidx = 0

    def reset(self):
        self._keys = [0x0F, 0x0F]
        self._colidx = 0
        print('KEY', 'Reset.')

    def rb(self):
        if self._colidx == 0x00:
            return 0x00
        elif self._colidx == 0x10:
            return self._keys[0]
        elif self._colidx == 0x20:
            return self._keys[1]
        else:
            return 0x00

    def wb(self, v):
        self._colidx = v & 0x30

    def _press(self, group, bit):
        #Group 0: buttons, Group 1: Dpad
        mask = 1 << bit
        was_up = bool(self._keys[group] & mask)
        self._keys[group] &= (~mask & 0xF)

        #Joypad interrupt
        if was_up and self.MMU is not None:
            select_bit = 0x20 if group==0 else 0x10
            if (self._colidx & select_bit) == 0:
                self.MMU._if |= 0x10
                
    def keydown(self, keycode):
        if keycode == pygame.K_RIGHT:   # Right
            #self._keys[1] &= 0xE
            self._press(1,0)
        elif keycode == pygame.K_LEFT: # Left
            #self._keys[1] &= 0xD
            self._press(1,1)
        elif keycode == pygame.K_UP: # Up
            #self._keys[1] &= 0xB
            self._press(1,2)
        elif keycode == pygame.K_DOWN: # Down
            #self._keys[1] &= 0x7
            self._press(1,3)
        elif keycode == pygame.K_z: # Z  (A)
            #self._keys[0] &= 0xE
            self._press(0,0)
        elif keycode == pygame.K_x: # X  (B)
            #self._keys[0] &= 0xD
            self._press(0,1)
        elif keycode == 32: # Space      (Select)
            #self._keys[0] &= 0xB
            self._press(0,2)
        elif keycode == 13: # Enter      (Start)
            #self._keys[0] &= 0x7
            self._press(0,3)

    def keyup(self, keycode):
        if keycode == pygame.K_RIGHT:   # Right
            self._keys[1] |= 0x1
        elif keycode == pygame.K_LEFT: # Left
            self._keys[1] |= 0x2
        elif keycode == pygame.K_UP: # Up
            self._keys[1] |= 0x4
        elif keycode == pygame.K_DOWN: # Down
            self._keys[1] |= 0x8
        elif keycode == pygame.K_z: # Z
            self._keys[0] |= 0x1
        elif keycode == pygame.K_x: # X
            self._keys[0] |= 0x2
        elif keycode == 32: # Space
            self._keys[0] |= 0x4
        elif keycode == 13: # Enter
            self._keys[0] |= 0x8
