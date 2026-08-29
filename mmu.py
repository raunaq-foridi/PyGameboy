#Raunaq Foridi 2026
#Memory Unit for Gameboy.

class MMU:
    def __init__(self):

        self._bios = [
    0x31, 0xFE, 0xFF, 0xAF, 0x21, 0xFF, 0x9F, 0x32, 0xCB, 0x7C, 0x20, 0xFB, 0x21, 0x26, 0xFF, 0x0E,
    0x11, 0x3E, 0x80, 0x32, 0xE2, 0x0C, 0x3E, 0xF3, 0xE2, 0x32, 0x3E, 0x77, 0x77, 0x3E, 0xFC, 0xE0,
    0x47, 0x11, 0x04, 0x01, 0x21, 0x10, 0x80, 0x1A, 0xCD, 0x95, 0x00, 0xCD, 0x96, 0x00, 0x13, 0x7B,
    0xFE, 0x34, 0x20, 0xF3, 0x11, 0xD8, 0x00, 0x06, 0x08, 0x1A, 0x13, 0x22, 0x23, 0x05, 0x20, 0xF9,
    0x3E, 0x19, 0xEA, 0x10, 0x99, 0x21, 0x2F, 0x99, 0x0E, 0x0C, 0x3D, 0x28, 0x08, 0x32, 0x0D, 0x20,
    0xF9, 0x2E, 0x0F, 0x18, 0xF3, 0x67, 0x3E, 0x64, 0x57, 0xE0, 0x42, 0x3E, 0x91, 0xE0, 0x40, 0x04,
    0x1E, 0x02, 0x0E, 0x0C, 0xF0, 0x44, 0xFE, 0x90, 0x20, 0xFA, 0x0D, 0x20, 0xF7, 0x1D, 0x20, 0xF2,
    0x0E, 0x13, 0x24, 0x7C, 0x1E, 0x83, 0xFE, 0x62, 0x28, 0x06, 0x1E, 0xC1, 0xFE, 0x64, 0x20, 0x06,
    0x7B, 0xE2, 0x0C, 0x3E, 0x87, 0xF2, 0xF0, 0x42, 0x90, 0xE0, 0x42, 0x15, 0x20, 0xD2, 0x05, 0x20,
    0x4F, 0x16, 0x20, 0x18, 0xCB, 0x4F, 0x06, 0x04, 0xC5, 0xCB, 0x11, 0x17, 0xC1, 0xCB, 0x11, 0x17,
    0x05, 0x20, 0xF5, 0x22, 0x23, 0x22, 0x23, 0xC9, 0xCE, 0xED, 0x66, 0x66, 0xCC, 0x0D, 0x00, 0x0B,
    0x03, 0x73, 0x00, 0x83, 0x00, 0x0C, 0x00, 0x0D, 0x00, 0x08, 0x11, 0x1F, 0x88, 0x89, 0x00, 0x0E,
    0xDC, 0xCC, 0x6E, 0xE6, 0xDD, 0xDD, 0xD9, 0x99, 0xBB, 0xBB, 0x67, 0x63, 0x6E, 0x0E, 0xEC, 0xCC,
    0xDD, 0xDC, 0x99, 0x9F, 0xBB, 0xB9, 0x33, 0x3E, 0x3c, 0x42, 0xB9, 0xA5, 0xB9, 0xA5, 0x42, 0x4C,
    0x21, 0x04, 0x01, 0x11, 0xA8, 0x00, 0x1A, 0x13, 0xBE, 0x20, 0xFE, 0x23, 0x7D, 0xFE, 0x34, 0x20,
    0xF5, 0x06, 0x19, 0x78, 0x86, 0x23, 0x05, 0x20, 0xFB, 0x86, 0x20, 0xFE, 0x3E, 0x01, 0xE0, 0x50
  ]
        self._rom=""
        self._carttype= 0
        self._mbc= [{},{"rombank":0, "rambank":0, "ramon":0, "mode":0}]
        self._romoffs= 0x4000
        self._ramoffs= 0

        '''self._eram= []
        self._wram= []
        self._zram= []'''
        self._wram = [0] * 0x2000  # 8192 bytes initialized to zero
        self._eram = [0] * 0x8000
        self._zram = [0] * 0x7F

        self._inbios= 1
        self._ie= 0
        self._if= 0
        self._sb = 0
        self._sc = 0

        self._debug = 0
    def reset(self):
        for i in range(0,8192):
            self._wram[i]=0
        for i in range(0,32768):
            self._eram[i]=0
        for i in range(0,127):
            self._zram[i]=0

        self._inbios= 1
        self._ie= 0
        self._if= 0
        self._sb = 0
        self._sc = 0
        
        self._carttype= 0
        self._mbc= [{},{"rombank":0, "rambank":0, "ramon":0, "mode":0}]
        self._romoffs= 0x4000
        self._ramoffs= 0

        print("MMU","Reset.")

    def load(self, file_path):
        # Open the file in binary mode
        with open(file_path, "rb") as f:
            self._rom = f.read()  # Read the whole file into bytes

        # Cartridge type is the byte at 0x0147
        self._carttype = self._rom[0x0147]
        print(f"MMU: ROM loaded, {len(self._rom)} bytes.")
        print("Starting Bios...")


    #le big read function
        
    def rb(self,addr):
        #self._debug = addr         #DEBUG CODE
        # ROM bank 0
        if (addr & 0xF000) == 0x0000:
            if self._inbios:
                #print("Doing a Bios instruction: ")
                if addr < 0x0100:
                    return self._bios[addr]
                elif self.CPU.PC == 0x0100:
                    self._inbios = 0
                    print('MMU', 'Leaving BIOS.')
                    return self._rom[addr]
            else:
                return self._rom[addr]

        elif (addr & 0xF000) in (0x1000, 0x2000, 0x3000):
            return self._rom[addr]

        # ROM bank 1
        elif (addr & 0xF000) in (0x4000, 0x5000, 0x6000, 0x7000):
            return self._rom[self._romoffs + (addr & 0x3FFF)]

        # VRAM
        elif (addr & 0xF000) in (0x8000, 0x9000):
            return self.GPU._vram[addr & 0x1FFF]

        # External RAM
        elif (addr & 0xF000) in (0xA000, 0xB000):
            return self._eram[self._ramoffs + (addr & 0x1FFF)]

        # Work RAM and echo
        elif (addr & 0xF000) in (0xC000, 0xD000, 0xE000):
            return self._wram[addr & 0x1FFF]

        # F000+ space: Echo RAM, OAM, Zeropage RAM, I/O, interrupts
        elif (addr & 0xF000) == 0xF000:
            sub = addr & 0x0F00

            # Echo RAM
            if sub in (0x000, 0x100, 0x200, 0x300,
                       0x400, 0x500, 0x600, 0x700,
                       0x800, 0x900, 0xA00, 0xB00,
                       0xC00, 0xD00):
                return self._wram[addr & 0x1FFF]

            # OAM
            elif sub == 0xE00:
                return self.GPU._oam[addr & 0xFF] if (addr & 0xFF) < 0xA0 else 0

            # Zeropage RAM, I/O, interrupts
            elif sub == 0xF00:
                if addr == 0xFFFF:
                    return self._ie
                elif addr > 0xFF7F:
                    return self._zram[addr & 0x7F]
                else:
                    top_nibble = addr & 0xF0
                    if top_nibble == 0x00:
                        low_nibble = addr & 0xF
                        if low_nibble == 0:
                            return self.KEY.rb()       # JOYP
                        elif low_nibble == 1:
                            return self._sb             # Serial data
                        elif low_nibble == 2:
                            return self._sc             # Serial control
                        elif low_nibble in (4, 5, 6, 7):
                            return self.TIMER.rb(addr)
                        elif low_nibble == 15:
                            return self._if        # Interrupt flags
                        else:
                            return 0
                    elif top_nibble in (0x10, 0x20, 0x30):
                        return 0
                    elif top_nibble in (0x40, 0x50, 0x60, 0x70):
                        return self.GPU.rb(addr)

        
        return 0xFF

    def rw(self, addr):
        return self.rb(addr) + (self.rb(addr + 1) << 8)

    def wb(self, addr, val):

        '''test'''
        if addr < 0 or addr > 0xFFFF:
            print(
                "!!!!!!!! NEGATIVE/INVALID ADDRESS !!!!!!!!"
            )
            print("addr =", addr)
            print("val  =", hex(val))
            print("PC   =", hex(self.CPU.PC))
            print("H    =", hex(self.CPU.H))
            print("L    =", hex(self.CPU.L))
            print("B    =", hex(self.CPU.B))
            print("C    =", hex(self.CPU.C))
            print("D    =", hex(self.CPU.D))
            print("E    =", hex(self.CPU.E))
            print("SP   =", hex(self.CPU.SP))
            raise RuntimeError("Invalid memory address")

        
        high = addr & 0xF000

        # ROM bank 0 / MBC1: Enable external RAM
        if high in (0x0000, 0x1000):
            if self._carttype == 1:
                self._mbc[1]["ramon"] = 1 if (val & 0xF) == 0xA else 0

        # MBC1: ROM bank switch
        elif high in (0x2000, 0x3000):
            if self._carttype == 1:
                self._mbc[1]["rombank"] &= 0x60
                val &= 0x1F
                if val == 0:
                    val = 1
                self._mbc[1]["rombank"] |= val
                self._romoffs = self._mbc[1]["rombank"] * 0x4000

        # MBC1: RAM bank switch or extended ROM bank
        elif high in (0x4000, 0x5000):
            if self._carttype == 1:
                if self._mbc[1]["mode"]:
                    self._mbc[1]["rambank"] = val & 3
                    self._ramoffs = self._mbc[1]["rambank"] * 0x2000
                else:
                    self._mbc[1]["rombank"] &= 0x1F
                    self._mbc[1]["rombank"] |= ((val & 3) << 5)
                    self._romoffs = self._mbc[1]["rombank"] * 0x4000

        # MBC1: mode select
        elif high in (0x6000, 0x7000):
            if self._carttype == 1:
                self._mbc[1]["mode"] = val & 1

        # VRAM
        elif high in (0x8000, 0x9000):
            '''print(
                "VRAM WRITE:",
                hex(addr),
                hex(val),
                "PC:", hex(self.CPU.PC),
                "A:", hex(self.CPU.A),
                "B:", hex(self.CPU.B),
                "C:", hex(self.CPU.C),
                "D:", hex(self.CPU.D),
                "E:", hex(self.CPU.E),
                "H:", hex(self.CPU.H),
                "L:", hex(self.CPU.L),
            )'''
            
            self.GPU._vram[addr & 0x1FFF] = val
            self.GPU.updatetile(addr & 0x1FFF, val)
            '''if 0x8000 <= addr <= 0x97FF and val != 0:
                print(
                    "TILE DATA WRITE:",
                    hex(addr),
                    hex(val),
                    "PC:", hex(self.CPU.PC),
                    "A:", hex(self.CPU.A),
                    "HL:", hex((self.CPU.H << 8) | self.CPU.L)
                )'''

        # External RAM
        elif high in (0xA000, 0xB000):
            self._eram[self._ramoffs + (addr & 0x1FFF)] = val

        # Work RAM and echo
        elif high in (0xC000, 0xD000, 0xE000):
            self._wram[addr & 0x1FFF] = val

        # Everything else (F000+)
        elif high == 0xF000:
            sub = addr & 0x0F00

            # Echo RAM
            if sub in (0x000, 0x100, 0x200, 0x300, 0x400, 0x500, 0x600, 0x700,
                       0x800, 0x900, 0xA00, 0xB00, 0xC00, 0xD00):
                self._wram[addr & 0x1FFF] = val

            # OAM
            elif sub == 0xE00:
                if (addr & 0xFF) < 0xA0:
                    self.GPU._oam[addr & 0xFF] = val
                self.GPU.updateoam(addr, val)

            # Zeropage RAM, I/O, interrupts
            elif sub == 0xF00:
                if addr == 0xFFFF:
                    self._ie = val
                elif addr > 0xFF7F:
                    self._zram[addr & 0x7F] = val
                else:
                    hi_nibble = addr & 0xF0
                    if hi_nibble == 0x00:
                        low = addr & 0xF
                        if low == 0:
                            self.KEY.wb(val)
                        elif low == 1:
                            self._sb = val               # Serial data
                        elif low == 2:
                            self._sc = val                # Serial control
                            # Blargg test ROMs (and real link-cable transfers
                            # with no partner attached) set bit7 (start) and
                            # bit0 (internal clock) to shift SB out one byte
                            # at a time. Print it so test output is visible
                            # in the console regardless of PPU correctness.
                            if val & 0x81 == 0x81:
                                import sys
                                sys.stdout.write(chr(self._sb))
                                sys.stdout.flush()
                        elif low in (4, 5, 6, 7):
                            self.TIMER.wb(addr, val)
                        elif low == 15:
                            self._if = val
                    elif hi_nibble in (0x10, 0x20, 0x30):
                        pass
                    elif hi_nibble in (0x40, 0x50, 0x60, 0x70):
                        self.GPU.wb(addr, val)

        
    def ww(self, addr, val):
        self.wb(addr, val & 0xFF)       # write low byte
        self.wb(addr + 1, (val >> 8) & 0xFF)  # write high byte


#MMU = MMU()
