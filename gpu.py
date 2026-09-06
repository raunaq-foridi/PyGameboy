import pygame
import numpy as np


WIDTH = 160
HEIGHT = 144

screen = pygame.display.set_mode((WIDTH,HEIGHT))

class DummyGPU:
    def __init__(self):
        self._vram = [0] * 0x2000
        self._oam = [0] * 0xA0

    # Read a memory-mapped GPU byte
    def rb(self, addr):
        return 0  # dummy value

    # Write a memory-mapped GPU byte
    def wb(self, addr, val):
        if 0x8000 <= addr <= 0x9FFF:
            self._vram[addr & 0x1FFF] = val
        elif 0xFE00 <= addr <= 0xFE9F:
            self._oam[addr & 0xFF] = val

    # Called when a VRAM tile changes
    def updatetile(self, index, val):
        pass

    # Called when OAM sprite changes
    def updateoam(self, addr, val):
        pass

    def reset(self):
        print("DummyGPU doesn't do anything so it can't be reset")
#GPU = DummyGPU()

class GPU:

    def __init__(self):
        self.CPU = None
        self.MMU = None

        # Game Boy VRAM and OAM
        self._vram = [0] * 0x2000
        self._oam = [0] * 0xA0

        # LCD registers
        self._reg = [0] * 0x40

        # Each tile is 8x8 pixels.
        # Pixel values are 0-3.
        self._tilemap = [
            [[0 for _ in range(8)] for _ in range(8)]
            for _ in range(512)
        ]

        # OAM objects
        self._objdata = []
        self._objdatasorted = []

        # Game Boy palettes.
        # Values are actual RGB grayscale values.
        self._palette = {
            'bg':  [255, 255, 255, 255],
            'obj0': [255, 255, 255, 255],
            'obj1': [255, 255, 255, 255],
        }

        # Background colour index for each pixel of the
        # current scanline. Used for sprite priority.
        self._scanrow = [0] * WIDTH

        # Framebuffer: WIDTH x HEIGHT x RGBA
        self._scrn = [255] * (WIDTH * HEIGHT * 4)

        # PPU state
        self._curline = 0
        self._curscan = 0
        self._linemode = 2
        self._modeclocks = 0

        # LCD state
        self._yscrl = 0
        self._xscrl = 0
        self._raster = 0
        self._ints = 0

        self._lcdon = 0
        self._bgon = 0
        self._objon = 0
        self._winon = 0
        self._objsize = 0

        self._winx = 0
        self._winy = 0
        self._winline = 0
        
        # VRAM tile addressing
        self._bgtilebase = 0x0000
        self._bgmapbase = 0x1800
        self._wintilebase = 0x1800

        #Cache
        #self._tile_cache = {}

        self.reset()

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self):
        self._vram = [0] * 0x2000
        self._oam = [0] * 0xA0

        self._tilemap = [
            [[0 for _ in range(8)] for _ in range(8)]
            for _ in range(512)
        ]

        self._scanrow = [0] * WIDTH

        self._objdata = []

        for i in range(40):
            self._objdata.append({
                'y': -16,
                'x': -8,
                'tile': 0,
                'palette': 0,
                'yflip': 0,
                'xflip': 0,
                'prio': 0,
                'num': i,
            })

        self._objdatasorted = list(self._objdata)

        self._palette = {
            'bg':  [255, 255, 255, 255],
            'obj0': [255, 255, 255, 255, 255],
            'obj1': [255, 255, 255, 255],
        }

        # Framebuffer starts white.
        self._scrn = [255] * (WIDTH * HEIGHT * 4)

        self._curline = 0
        self._curscan = 0
        self._linemode = 2
        self._modeclocks = 0

        self._winx = 0
        self._winy = 0
        self._winline = 0

        #self._tile_cache = {}
        
        print("GPU Reset")
        self._scrn = [0] * (WIDTH * HEIGHT * 4)

        for i in range(WIDTH * HEIGHT):
            self._scrn[i * 4 + 0] = 255  # R
            self._scrn[i * 4 + 1] = 0    # G
            self._scrn[i * 4 + 2] = 0    # B
            self._scrn[i * 4 + 3] = 255  # A
        print("GPU Redset")

    # ------------------------------------------------------------------
    # PPU timing
    # ------------------------------------------------------------------

    def checkline(self):
        """
        Advance the PPU by the number of machine cycles used by
        the most recently executed CPU instruction.
        """

        if self.CPU is None:
            raise RuntimeError("CPU not linked to GPU")

        self._modeclocks += self.CPU.M

        # Keep processing until all cycles have been consumed.
        while True:

            # ----------------------------------------------------------
            # Mode 2: OAM search
            # ----------------------------------------------------------
            if self._linemode == 2:

                if self._modeclocks < 20:
                    break

                self._modeclocks -= 20
                self._linemode = 3

                # Continue immediately in case the CPU instruction
                # supplied enough cycles to cross another boundary.
                continue

            # ----------------------------------------------------------
            # Mode 3: VRAM transfer
            # ----------------------------------------------------------
            elif self._linemode == 3:

                if self._modeclocks < 43:
                    break

                self._modeclocks -= 43
                self._linemode = 0

                if self._lcdon and self._curline < HEIGHT:
                    #print(">>> RENDER SCANLINE", self._curline)
                    self.render_scanline()

                continue

            # ----------------------------------------------------------
            # Mode 0: HBlank
            # ----------------------------------------------------------
            elif self._linemode == 0:

                if self._modeclocks < 51:
                    break

                self._modeclocks -= 51

                self._curline += 1
                self._curscan = self._curline * WIDTH * 4

                if self._curline >= 144:

                    # Enter VBlank.
                    self._linemode = 1

                    #print(">>> ENTER VBLANK")

                    # Display completed frame.
                    self.render_screen()

                    # Request VBlank interrupt.
                    if self.MMU:
                        self.MMU._if |= 1

                else:

                    # Begin OAM search for next visible line.
                    self._linemode = 2

                continue

            # ----------------------------------------------------------
            # Mode 1: VBlank
            # ----------------------------------------------------------
            elif self._linemode == 1:

                if self._modeclocks < 114:
                    break

                self._modeclocks -= 114
                self._curline += 1

                if self._curline > 153:

                    self._curline = 0
                    self._curscan = 0
                    self._linemode = 2
                    self._winline = 0

                continue

            else:
                raise RuntimeError(
                    f"Invalid PPU mode: {self._linemode}"
                )

    # ------------------------------------------------------------------
    # VRAM tile handling
    # ------------------------------------------------------------------

    def updatetile(self, addr, val):
        """
        Rebuild the cached 8x8 tile affected by a VRAM write.
        """

        # Tile data consists of two bytes per row.
        if addr & 1:
            addr -= 1

        tile = (addr >> 4) & 0x1FF
        y = (addr >> 1) & 7

        low = self._vram[addr]
        high = self._vram[addr + 1]

        for x in range(8):
            mask = 1 << (7 - x)

            colour = 0

            if low & mask:
                colour |= 1

            if high & mask:
                colour |= 2

            self._tilemap[tile][y][x] = colour

    # ------------------------------------------------------------------
    # OAM handling
    # ------------------------------------------------------------------

    def updateoam(self, addr, val):
        """
        Update the cached sprite corresponding to an OAM write.
        """

        addr -= 0xFE00

        if addr < 0 or addr >= 0xA0:
            return

        obj = addr >> 2

        if obj >= 40:
            return

        entry = self._objdata[obj]

        field = addr & 3

        if field == 0:
            # OAM Y coordinate is displayed Y + 16.
            entry['y'] = val - 16

        elif field == 1:
            # OAM X coordinate is displayed X + 8.
            entry['x'] = val - 8

        elif field == 2:
            # In 8x16 mode, the bottom bit is ignored.
            if self._objsize:
                entry['tile'] = val & 0xFE
            else:
                entry['tile'] = val

        elif field == 3:
            entry['palette'] = 1 if (val & 0x10) else 0
            entry['xflip'] = 1 if (val & 0x20) else 0
            entry['yflip'] = 1 if (val & 0x40) else 0
            entry['prio'] = 1 if (val & 0x80) else 0

        # Hardware prioritises lower X coordinates, and then lower
        # OAM index when X coordinates are equal.
        self._objdatasorted = sorted(
            self._objdata,
            key=lambda o: (o['x'], o['num'])
        )

    # ------------------------------------------------------------------
    # Register reads
    # ------------------------------------------------------------------

    def rb(self, addr):
        gaddr = addr - 0xFF40

        if gaddr == 0:
            # LCDC
            return (
                (0x80 if self._lcdon else 0)
                | (0x40 if self._wintilebase == 0x1C00 else 0)
                | (0x20 if self._winon else 0)
                | (0x10 if self._bgtilebase == 0x0000 else 0)
                | (0x08 if self._bgmapbase == 0x1C00 else 0)
                | (0x04 if self._objsize else 0)
                | (0x02 if self._objon else 0)
                | (0x01 if self._bgon else 0)
            )

        elif gaddr == 1:
            # STAT
            coincidence = 4 if self._curline == self._raster else 0
            return coincidence | self._linemode

        elif gaddr == 2:
            return self._yscrl

        elif gaddr == 3:
            return self._xscrl

        elif gaddr == 4:
            return self._curline

        elif gaddr == 5:
            return self._raster

        elif gaddr == 10:
            return self._winy

        elif gaddr == 11:
            return self._winx
        return self._reg[gaddr]

    # ------------------------------------------------------------------
    # Register writes
    # ------------------------------------------------------------------

    def wb(self, addr, val):
        gaddr = addr - 0xFF40

        if gaddr < 0 or gaddr >= len(self._reg):
            return

        self._reg[gaddr] = val & 0xFF

        # LCDC
        if gaddr == 0:

            was_on = self._lcdon

            self._lcdon = 1 if (val & 0x80) else 0

            self._wintilebase = (
                0x1C00 if (val & 0x40)
                else 0x1800
            )
            
            self._winon = 1 if (val & 0x20) else 0
            
            self._bgtilebase = (
                0x0000 if (val & 0x10)
                else 0x0800
            )

            self._bgmapbase = (
                0x1C00 if (val & 0x08)
                else 0x1800
            )

            self._objsize = 1 if (val & 0x04) else 0
            self._objon = 1 if (val & 0x02) else 0
            self._bgon = 1 if (val & 0x01) else 0

            # LCD was just enabled.
            if not was_on and self._lcdon:
                self._curline = 0
                self._curscan = 0
                self._modeclocks = 0
                self._linemode = 2
                self._winline = 0

            # LCD was disabled.
            elif was_on and not self._lcdon:
                self._curline = 0
                self._curscan = 0
                self._modeclocks = 0
                self._winline = 0

        # STAT
        elif gaddr == 1:
            pass

        # SCY
        elif gaddr == 2:
            self._yscrl = val

        # SCX
        elif gaddr == 3:
            self._xscrl = val

        # LY
        elif gaddr == 4:
            # LY is normally read-only.
            pass

        # LYC
        elif gaddr == 5:
            self._raster = val

        # DMA
        elif gaddr == 6:

            if self.MMU is None:
                raise RuntimeError("MMU not linked to GPU")

            source = val << 8

            for i in range(160):
                v = self.MMU.rb(source + i)

                self._oam[i] = v
                self.updateoam(0xFE00 + i, v)

        # BGP
        elif gaddr == 7:
            self._update_palette(
                self._palette['bg'],
                val
            )

        # OBP0
        elif gaddr == 8:
            self._update_palette(
                self._palette['obj0'],
                val
            )

        # OBP1
        elif gaddr == 9:
            self._update_palette(
                self._palette['obj1'],
                val
            )
            
        # WY
        elif gaddr == 10:
            self._winy = val

        # WX
        elif gaddr == 11:
            self._winx = val

    # ------------------------------------------------------------------
    # Palette
    # ------------------------------------------------------------------

    def _update_palette(self, palette, val):
        """
        Convert the Game Boy's 2-bit palette entries to grayscale RGB.

        0 = white
        1 = light gray
        2 = dark gray
        3 = black
        """

        colours = [
            255,
            192,
            96,
            0,
        ]

        for i in range(4):
            shade = (val >> (i * 2)) & 3
            palette[i] = colours[shade]

    # ------------------------------------------------------------------
    # Tile lookup
    # ------------------------------------------------------------------

    def _get_tile(self, tile_number):
        """
        Return an 8x8 tile decoded from VRAM.

        tile_number is the tile number as stored in the BG map.
        """

        # Tile data starts at VRAM offset 0x0000 (address 0x8000).
        #
        # In unsigned mode:
        #   tile 0x00 -> VRAM 0x0000
        #   tile 0x01 -> VRAM 0x0010
        #
        # In signed mode (0x8800 tile data):
        #   0x80 -> tile -128 -> VRAM 0x0800
        #   0x81 -> tile -127 -> VRAM 0x0810
        #   ...
        #   0xFF -> tile -1   -> VRAM 0x0FF0

        '''if self._bgtilebase == 0x0800:
            # Convert unsigned byte to signed 8-bit value.
            if tile_number >= 128:
                tile_number -= 256

            # Signed tile numbering is centred on VRAM offset 0x1000.
            cache_key = tile_number + 256
            base = 0x1000 + tile_number * 16
        else:
            cache_key = tile_number
            base = tile_number * 16

        if cache_key in self._tile_cache:
            return self._tile_cache[cache_key]
        tile = []

        for y in range(8):
            lo = self._vram[base + y * 2]
            hi = self._vram[base + y * 2 + 1]

            row = []

            for x in range(8):
                bit = 7 - x

                colour = (
                    ((hi >> bit) & 1) << 1
                    | ((lo >> bit) & 1)
                )

                row.append(colour)

            tile.append(row)

        self._tile_cache[cache_key] = tile
        return tile'''
        if self._bgtilebase == 0x0800 and tile_number<128:
            tile_number+=256
        return self._tilemap[tile_number]


    # ------------------------------------------------------------------
    # Background rendering
    # ------------------------------------------------------------------

    def _render_background(self):
        """
        Render the background for the current scanline.

        Game Boy background is a 256x256 pixel tile map.
        SCX/SCY select which portion is visible.
        """

        screen_y = self._curline

        # Background disabled:
        # fill the line with colour 0.
        if not self._bgon:

            colour = self._palette['bg'][0]

            for x in range(WIDTH):
                '''self._put_pixel(
                    x,
                    screen_y,
                    colour
                )'''
                offset = screen_y*WIDTH*4 + x*4
                self._scrn[offset] = colour
                self._scrn[offset+1] = colour
                self._scrn[offset+2] = colour
                self._scrn[offset+3] = 255

                self._scanrow[x] = 0

            return

        # Coordinates in the 256x256 background.
        bg_y = (screen_y + self._yscrl) & 0xFF

        tile_y = bg_y >> 3
        pixel_y = bg_y & 7

        for screen_x in range(WIDTH):

            bg_x = (screen_x + self._xscrl) & 0xFF

            tile_x = bg_x >> 3
            pixel_x = bg_x & 7

            # Tile map is 32 x 32 tiles.
            map_index = (
                self._bgmapbase
                + tile_y * 32
                + tile_x
            )

            tile_number = self._vram[map_index & 0x1FFF]

            # 0x8800 addressing mode.
            #
            # Tile numbers 0x80-0xFF are interpreted as
            # signed values, giving tile indices 256-383.
            '''if self._bgtilebase == 0x0800:
                if tile_number < 128:
                    tile_number += 256'''

            tile = self._get_tile(tile_number)

            colour_index = tile[pixel_y][pixel_x]

            colour = self._palette['bg'][colour_index]

            '''self._put_pixel(
                screen_x,
                screen_y,
                colour
            )'''
            offset = screen_y*WIDTH*4 + screen_x*4
            self._scrn[offset] = colour
            self._scrn[offset+1] = colour
            self._scrn[offset+2] = colour
            self._scrn[offset+3] = 255

            self._scanrow[screen_x] = colour_index

    # ------------------------------------------------------------------
    # Window rendering
    # ------------------------------------------------------------------

    def _render_window(self):
        """
        Render the window for the current scanline
        Fixed 160x144 overlay, with position controlled by WY/WX, not SCX/SCY
        """

        if not self._winon:
            return
        if not self._bgon:
            return

        screen_y = self._curline

        #Ignor if too high vertically
        if screen_y < self._winy:
            return

        window_x = self._winx - 7
        win_y = self._winline & 0xFF

        tile_y = win_y >>3
        pixel_y = win_y & 7

        for screen_x in range(WIDTH):

            window_pixel_x = screen_x - window_x
            if window_pixel_x<0 or window_pixel_x>256:
                continue

            tile_x = window_pixel_x >>3
            pixel_x = window_pixel_x &7

            map_index = (self._wintilebase + tile_y*32 + tile_x)

            tile_number = self._vram[map_index & 0x1FFF]
            tile = self._get_tile(tile_number)

            colour_index = tile[pixel_y][pixel_x]
            colour = self._palette["bg"][colour_index]

            offset = screen_y * WIDTH * 4 + screen_x*4

            self._scrn[offset] = colour
            self._scrn[offset+1] = colour
            self._scrn[offset+2] = colour
            self._scrn[offset+3] = 255

            self._scanrow[screen_x] = colour_index

        self._winline+=1
    
    # ------------------------------------------------------------------
    # Sprite rendering
    # ------------------------------------------------------------------

    def _render_sprites(self):
        """
        Render sprites for the current scanline.

        Maximum of 10 sprites per scanline on original Game Boy hardware.
        """

        screen_y = self._curline

        height = 16 if self._objsize else 8

        count = 0

        for obj in self._objdatasorted:

            # Is the sprite on this scanline?
            if not (
                obj['y'] <= screen_y
                and screen_y < obj['y'] + height
            ):
                continue

            count += 1

            # Hardware limit.
            if count > 10:
                break

            line = screen_y - obj['y']

            # Vertical flip.
            if obj['yflip']:
                line = height - 1 - line

            tile_number = obj['tile']

            if self._objsize:
                # 8x16 sprites use two consecutive tiles.
                #
                # The first tile is the top 8 pixels.
                # The second is the bottom 8 pixels.
                if line >= 8:
                    tile_number += 1
                    line -= 8

            #tile = self._get_tile(tile_number)
            tile = self._tilemap[tile_number & 0xFF]

            palette = (
                self._palette['obj1']
                if obj['palette']
                else self._palette['obj0']
            )

            for px in range(8):

                screen_x = obj['x'] + px

                if screen_x < 0 or screen_x >= WIDTH:
                    continue

                tile_x = 7 - px if obj['xflip'] else px

                colour_index = tile[line][tile_x]

                # Colour 0 is transparent for sprites.
                if colour_index == 0:
                    continue

                # Sprite priority bit means the sprite is behind
                # non-zero background pixels.
                #
                # Note: the Game Boy's priority behaviour is a little
                # more subtle than this, but this is the correct basic
                # behaviour for a first PPU implementation.
                if obj['prio'] and self._scanrow[screen_x] != 0:
                    continue

                colour = palette[colour_index]

                self._put_pixel(
                    screen_x,
                    screen_y,
                    colour
                )

    # ------------------------------------------------------------------
    # Pixel output
    # ------------------------------------------------------------------

    def _put_pixel(self, x, y, colour):
        """
        Write an RGB pixel into the framebuffer.
        """

        if x < 0 or x >= WIDTH:
            return

        if y < 0 or y >= HEIGHT:
            return

        offset = (y * WIDTH + x) * 4

        self._scrn[offset + 0] = colour
        self._scrn[offset + 1] = colour
        self._scrn[offset + 2] = colour
        self._scrn[offset + 3] = 255

    # ------------------------------------------------------------------
    # Scanline rendering
    # ------------------------------------------------------------------

    def render_scanline(self):
        """
        Render one complete visible scanline into the framebuffer.
        """
        '''
        print(
                "LINE:",
                self._curline,
                "VRAM:",
                self._vram[:16],
                "TILE0:",
                self._tilemap[0]
            )
        if self._curline == 0:
            print("RENDERING!")

            print("LCDC:", hex(self.rb(0xFF40)))
            print("VRAM first 32:", self._vram[:32])
            print("BG MAP:", self._vram[self._bgmapbase:self._bgmapbase + 32])
            print("TILE 0:")
            for row in self._tilemap[0]:
                print(row)

                '''
        if not self._lcdon:
            return

        if self._curline >= HEIGHT:
            return

        # Reset background information.
        self._scanrow = [0] * WIDTH

        # Background first.
        self._render_background()

        # Windows replace backgrounds. unsure of before/after sprite
        self._render_window()
        
        # Sprites are drawn over the background.
        if self._objon:
            self._render_sprites()

    # ------------------------------------------------------------------
    # Pygame framebuffer output
    # ------------------------------------------------------------------
    '''
    def render_screen(self):
        """
        Copy the completed framebuffer into a Pygame surface.

        Call this once per completed frame, not once per scanline.
        """

        rgba = np.asarray(
            self._scrn,
            dtype=np.uint8
        ).reshape(
            HEIGHT,
            WIDTH,
            4
        )

        # Pygame's surfarray expects:
        #     (width, height, channels)
        #
        # Our framebuffer is:
        #     (height, width, channels)
        rgb = rgba[:, :, :3]

        rgb = np.transpose(
            rgb,
            (1, 0, 2)
        )

        pygame.surfarray.blit_array(
            screen,
            rgb
        )

        pygame.display.flip()
        pygame.event.pump()
'''

    '''def render_screen(self):
        #print("yohoho")
        rgba = np.asarray(
            self._scrn,
            dtype=np.uint8
        ).reshape(HEIGHT, WIDTH, 4)

        rgb = rgba[:, :, :3]

        pygame.surfarray.blit_array(
            screen,
            np.transpose(rgb, (1, 0, 2))
        )

        pygame.display.flip()
        pygame.event.pump()'''


    def render_screen(self):
    # Convert our RGBA screen buffer into a NumPy array
        arr = np.array(self._scrn, dtype=np.uint8)
        arr = arr.reshape((HEIGHT, WIDTH, 4))

        # Pygame's surfarray uses (WIDTH, HEIGHT, RGB)
        arr = np.transpose(arr[:, :, :3], (1, 0, 2))

        pygame.surfarray.blit_array(screen, arr)
        pygame.display.flip()
        pygame.event.pump()
