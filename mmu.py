#Raunaq Foridi 2026
#Memory Unit for Gameboy.

import time
import os
import struct

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
        self._ramenabled = False

        #Clock
        self._rtc_regs = {"s":0, "m":0, "h":0, "dl":0, "dh":0}
        self._rtc_latched_regs = dict(self._rtc_regs)
        self._rtc_base_time = None #Set when ROM loads
        
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

        self._ramenabled = False
        self._rtc_regs = {"s":0, "m":0, "h":0, "dl":0, "dh":0}
        self._rtc_latched_regs = dict(self._rtc_regs)
        self._rtc_base_time = None
        
        print("MMU","Reset.")

    def load(self, file_path):
        # Open the file in binary mode
        with open(file_path, "rb") as f:
            self._rom = f.read()  # Read the whole file into bytes

        # Cartridge type is the byte at 0x0147
        self._carttype = self._rom[0x0147]
        self._rtc_base_time = time.time()
        self._rom_path = file_path
        
        print(f"MMU: ROM loaded, {len(self._rom)} bytes.")
        print("Starting Bios...")


    # MBC Support

    def _check_mbc(self):
        t = self._carttype
        if t in (0x00, 0x08, 0x09):
            return "none"
        if t in (0x01, 0x02, 0x03):
            return "mbc1"
        if t in (0x05, 0x06):
            return "mbc2"
        if t in (0x0F, 0x10, 0x11, 0x12, 0x13):
            return "mbc3"
        if t in (0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E):
            return "mbc5"
        return "none"

    def _mbc1_bank(self):
        #MBC1 bumps up 0x00, 0x20, 0x40 and 0x60 by 1

        bank = self._mbc[1]["rombank"]
        if bank in (0x00,0x20,0x40,0x60):
            bank+=1
        return bank

    def _rtc_latch(self):
        #take in the live time to the latched registers

        elapsed = int(time.time() - (self._rtc_base_time or time.time() ))
        days,rem = divmod(elapsed,86400)
        h, rem = divmod(rem, 3600)
        m, s = divmod(rem,60)

        #DEBUG: later add halt/carry flags
        self._rtc_latched_regs = {
            "s": s, "m": m, "h": h, "dl": (days & 0xFF), "dh": (days>>8)&1
            }

    def _rtc_read(self):
        select = self._mb[1].get("rtc_select")
        key = {0x08: "s", 0x09:"m", 0x0A:"h", 0x0B:"dl", 0x0C:"dh"}.get(select)
        return self._rtc_latched_regs.get(key, 0xFF) if key else 0xFF

    def _rtc_write(self, val):
        select = self._mb[1].get("rtc_select")
        key = {0x08: "s", 0x09:"m", 0x0A:"h", 0x0B:"dl", 0x0C:"dh"}.get(select)
        if key:
            self._rtc_latched_regs[key] = val

    #Save Persistence - Battery backed RAM and RTC

    def _has_battery(self):
        return self._carttype in (0x03,0x06,0x09,0x0F,0x10,0x13,0x1B,0x1E)


    def _has_rtc(self):
        return self._carttype in (0x0F, 0x10)   #MBC3+TIMER variants

    def _cart_ram_size(self):
        if self._check_mbc() == "mbc2":
            return 512
        if len(self._rom) <= 0x149:
            return 0
        code = self._rom[0x149]
        sizes = {0x00:0, 0x01: 0x800, 0x02: 0x2000, 0x03: 0x8000,
                 0x04: 0x20000, 0x05: 0x10000}
        return sizes.get(code,0)

    def _default_save_path(self):
        import os
        base, _ = os.path.splitext(getattr(self, "_rom_path", "rom"))
        return base + ".sav"

    def save_ram(self, path = None):
        #Write battery-backed RAM and RTC to disk
        if not self._has_battery():
            return False

        path = path or self._default_save_path()
        size = self._cart_ram_size()

        with open(path, "wb") as f:
            f.write(b"GBSAVE01")
            f.write(struct.pack("<I", size))
            f.write(bytes(self._eram[:size]))

            has_rtc = 1 if self._has_rtc() else 0
            f.write(struct.pack("<B",has_rtc))
            if has_rtc:
                regs = self._rtc_latched_regs
                f.write(struct.pack(
                    "<BBBBB",
                    regs["s"] &0xFF, regs["m"]&0xFF, regs["h"]&0xFF,
                    regs["dl"]&0xFF, regs["dh"] &0xFF,))

                elapsed = time.time() - (self._rtc_base_time or time.time())
                f.write(struct.pack("<d", elapsed))

            print(f"MMU: Saved RAM. {size} bytes to {path}")
            return True

    def load_ram(self, path=None):
        #Load pre-saved RAM and RTC state.

        if not self._has_battery():
            return False
        path = path or self._default_save_path()
        if not os.path.exists(path):
            return False

        with open(path, "rb") as f:
            header = f.read(8)
            if header!= b"GBSAVE01":
                print("MMU: Unrecognised save file format.")
                return False

            size = struct.unpack("<I", f.read(4))[0]
            #print(size)
            data = f.read(size)
        
            for i in range(min(size, len(self._eram))):
                self._eram[i] = data[i]

            '''print("Current position:", f.tell())
            print("File size:", os.fstat(f.fileno()).st_size)

            data = f.read(1)
            print("Read:", repr(data))'''

            has_rtc = struct.unpack("<B", f.read(1))[0]
            if has_rtc:
                s,m,h,dl,dh = struct.unpack("<BBBBB", f.read(5))
                self._rtc_latched_regs = {"s":s, "m":m, "h":h, "dl":dl, "dh":dh}
                elapse = struct.unpack("<d", f.read(8))[0]
                self._rtc_base_time = time.time() - elapsed

            print(f"MMU: Loaded RAM from {path}")
            return True
        
    #le big read function
        
    def rb(self,addr):
        #self._debug = addr         #DEBUG CODE
        # ROM bank 0
        if (addr & 0xF000) == 0x0000:
            if self._inbios:
                #print("Doing a Bios instruction: ")
                if addr < 0x0100:
                    return self._bios[addr]
                else:
                    if self.CPU.PC == 0x0100:
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

        # External RAM and MBC3 RTC registers
        elif (addr & 0xF000) in (0xA000, 0xB000):
            ctype = self._check_mbc()
            if ctype == "mbc3" and self._mbc[1].get("rtc_select") is not None:
                return self._rtc_read()
            if ctype != "none" and not self._ramenabled:
                return 0xFF
            
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

            # Zeropage RAM, I/O, interrupts (and Audio?)
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
                        #Audio - for now, only channel 1 and 2, no sweep
                        if 0x11<=(addr&0xFF)<=0x26:
                            return self.APU.rb(addr)
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

        ctype = self._check_mbc()
        
        # ROM bank 0 / MBC1: Enable external RAM
        if high in (0x0000, 0x1000):
            if ctype == "mbc2":
                #MBC2 uses bit 8 to distinguish RAM enable from ROM bank select
                if (addr & 0x0100) == 0:
                    self._ramenabled = True if (val & 0xF) == 0xA else 0

            elif ctype in ("mbc1", "mbc3", "mbc5"):
                self._ramenabled = True if (val & 0xF) == 0xA else 0
                #self._mbc[1]["ramon"] = 1 if (val & 0xF) == 0xA else 0

        # ROM bank select
        elif high in (0x2000, 0x3000):
            #MBC1
            if ctype == "mbc1":
                self._mbc[1]["rombank"] &= 0x60
                val &= 0x1F
                if val == 0:
                    val = 1
                self._mbc[1]["rombank"] |= val
                #self._romoffs = self._mbc[1]["rombank"] * 0x4000
                self._romoffs = self._mbc1_bank() * 0x4000 #account for mbc funkiness
            #MBC2
            elif ctype == "mbc2":
                if (addr & 0x0100) != 0:
                    val &= 0x0F
                    if val == 0:
                        val = 1
                    self._mbc[1]["rombank"] = val
                    self._romoffs = val * 0x4000
            #MBC3
            elif ctype == "mbc3":
                #Just uses all 7 bits directly
                val &= 0x7F
                if val == 0:
                    val = 1
                self._mbc[1]["rombank"] = val
                self._romoffs = val*0x4000
            #MBC5
            elif ctype == "mbc5":
                if high == 0x200:
                    # use the low 8 bits of the 9 bit rombank number
                    self._mbc[1]["rombank"] = (self._mbc[1]["rombank"] & 0x100)
                else:
                    # high bit
                    self._mbc[1]["rombank"] = (self._mbc[1]["rombank"] & 0xFF) | ((val & 1)<<8)
                self._romoffs = self._mbc[1]["rombank"] * 0x4000

        # RAM bank switch / MBC1 extended ROM bank / MBC3 RTC reg select
        elif high in (0x4000, 0x5000):
            if ctype == "mbc1":
                if self._mbc[1]["mode"]:
                    self._mbc[1]["rambank"] = val & 3
                    self._ramoffs = self._mbc[1]["rambank"] * 0x2000
                else:
                    self._mbc[1]["rombank"] &= 0x1F
                    self._mbc[1]["rombank"] |= ((val & 3) << 5)
                    self._romoffs = self._mbc1_bank() * 0x4000
            elif ctype == "mbc3":
                if val<=3:
                    self._mbc[1]["rtc_select"] = None
                    self._mbc[1]["rambank"] = val
                    self._ramoffs = val * 0x2000
                elif 0x08<= val <= 0x0C:
                    self._mbc[1]["rtc_select"] = val

            elif ctype == "mbc5":
                self._mbc[1]["rambank"] = val & 0x0F
                self._ramoffs = self._mbc[1]["rambank"] * 0x2000

        # MBC1: mode select / MBC3: RTC latch
        elif high in (0x6000, 0x7000):
            if ctype == "mbc1":
                self._mbc[1]["mode"] = val & 1
            elif ctype == "mbc3":
                if self._mbc[1].get("_rtc_latch_prev")==0 and val == 1:
                    self._rtc_latch()
                self._mbc[1]["_rtc_latch_prev"] = val

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

        # External RAM / MBC3 RTC registers
        elif high in (0xA000, 0xB000):
            if ctype == "mbc3" and self._mbc[1].get("rtc_select") is not None:
                self._rtc_write(val)
            elif ctype == "none" or self._ramenabled:
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
                        #Audio regs DEBUG
                        if 0x11<=(addr&0xFF)<=0x26:
                            self.APU.wb(addr, val)
                        #pass
                    elif hi_nibble in (0x40, 0x50, 0x60, 0x70):
                        self.GPU.wb(addr, val)

        
    def ww(self, addr, val):
        self.wb(addr, val & 0xFF)       # write low byte
        self.wb(addr + 1, (val >> 8) & 0xFF)  # write high byte


#MMU = MMU()
