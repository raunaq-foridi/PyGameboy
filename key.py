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

    def keydown(self, keycode):
        if keycode == 39:   # Right
            self._keys[1] &= 0xE
        elif keycode == 37: # Left
            self._keys[1] &= 0xD
        elif keycode == 38: # Up
            self._keys[1] &= 0xB
        elif keycode == 40: # Down
            self._keys[1] &= 0x7
        elif keycode == 90: # Z
            self._keys[0] &= 0xE
        elif keycode == 88: # X
            self._keys[0] &= 0xD
        elif keycode == 32: # Space
            self._keys[0] &= 0xB
        elif keycode == 13: # Enter
            self._keys[0] &= 0x7

    def keyup(self, keycode):
        if keycode == 39:   # Right
            self._keys[1] |= 0x1
        elif keycode == 37: # Left
            self._keys[1] |= 0x2
        elif keycode == 38: # Up
            self._keys[1] |= 0x4
        elif keycode == 40: # Down
            self._keys[1] |= 0x8
        elif keycode == 90: # Z
            self._keys[0] |= 0x1
        elif keycode == 88: # X
            self._keys[0] |= 0x2
        elif keycode == 32: # Space
            self._keys[0] |= 0x5
        elif keycode == 13: # Enter
            self._keys[0] |= 0x8
