#Raunaq Foridi 2026
#A very hacked together Gameboy emulator.
class CPU:

    class RegisterSave:
        def __init__(self):
            self.A = 0
            self.F = 0
            self.B = 0
            self.C = 0
            self.D = 0
            self.E = 0
            self.H = 0
            self.L = 0
            self.SP = 0
            self.PC = 0

            self.M = 0
            self.T = 0

    
    def __init__(self):
        self.A = 0
        self.F = 0
        self.B = 0
        self.C = 0
        self.D = 0
        self.E = 0
        self.H = 0
        self.L = 0
        self.SP = 0
        self.PC = 0

        self.M = 0
        self.T = 0
        self.I = 0
        self.R = 0

        
        self._stop = 0
        self._halt = 0
        self._clock= 0          #Specifically, the M clock
        self._clock_t= 0        #the T cycles
        
        self._map = []          #populate with opcodes after creation
        self._cbmap = []        #purely to avoid mess

        self.rsv = self.RegisterSave()
        self._ops = Ops()

        self.debug=[]

    #Dual registers
        
    @property
    def AF(self):
        return (self.A << 8) | self.F

    @AF.setter
    def AF(self, value):
        self.A = (value >> 8) & 0xFF
        self.F = value & 0xF0  # only upper 4 bits used

    @property
    def BC(self):
        return (self.B << 8) | self.C

    @BC.setter
    def BC(self, value):
        self.B = (value >> 8) & 0xFF
        self.C = value & 0xFF

    @property
    def DE(self):
        return (self.D << 8) | self.E

    @DE.setter
    def DE(self, value):
        self.D = (value >> 8) & 0xFF
        self.E = value & 0xFF

    @property
    def HL(self):
        return (self.H << 8) | self.L

    @HL.setter
    def HL(self, value):
        self.H = (value >> 8) & 0xFF
        self.L = value & 0xFF


    #Basic work

    def reset(self):
        self.A = 0
        self.B = 0
        self.C = 0
        self.D = 0
        self.E = 0
        self.H = 0
        self.L = 0
        self.F = 0

        self.SP = 0
        self.PC = 0
        self.I = 0
        self.R = 0

        self.M = 0
        self._halt = 0
        self._stop = 0

        self._clock = 0
        self.T = 1

        print('Z80', 'Reset.')

    def exec(self):
        # Increment refresh register (7 bits)
        self.R = (self.R + 1) & 0x7F

        # Fetch opcode and execute
        opcode = self.MMU.rb(self.PC)
        self.PC = (self.PC + 1) & 0xFFFF


        '''if 0x1CE0 <=self.PC<=0x1D10:
            print(
                "CPU:",
                hex(self.PC),
                "OP:", hex(opcode),
                "A:", hex(self.A),
                "BC:", hex((self.B << 8) | self.C),
                "DE:", hex((self.D << 8) | self.E),
                "HL:", hex((self.H << 8) | self.L),
                "SP:", hex(self.SP),
                "F:", hex(self.F)
            )
        '''
        self._map[opcode]()

        # Update clock cycles
        self._clock += self.M
        '''print(
            "PC =", hex(self.PC),
            "opcode =", hex(opcode),
            "BIOS =", self.MMU._inbios
        )'''
        

    
    #Helper functions

    def rSave(self):
        self.rsv.A=self.A
        self.rsv.B=self.B
        self.rsv.C=self.C
        self.rsv.D=self.D
        self.rsv.E=self.E
        self.rsv.F=self.F
        self.rsv.H=self.H
        self.rsv.L=self.L

    def rRestore(self):
        self.A=self.rsv.A
        self.B=self.rsv.B
        self.C=self.rsv.C
        self.D=self.rsv.D
        self.E=self.rsv.E
        self.F=self.rsv.F
        self.H=self.rsv.H
        self.L=self.rsv.L

    def MAPcb(self):
        i = self.MMU.rb(self.PC)
        self.PC += 1
        self.PC &= 0xFFFF

        if self._cbmap[i] is not None:
            self._cbmap[i]()
        else:
            print(i)


    def XX(self):
        # Undefined map entry
        opc = self.PC - 1
        print('Z80', 'Unimplemented instruction at $' + format(opc, 'x') + ', stopping.')
        self._stop = 1









### Define the operations. All of them. Be prepared. ###

    
class Ops:
    # --- Load/store: register to register ---
    def LDrr_bb(self): self.CPU.B = self.CPU.B; self.CPU.M = 1
    def LDrr_bc(self): self.CPU.B = self.CPU.C; self.CPU.M = 1
    def LDrr_bd(self): self.CPU.B = self.CPU.D; self.CPU.M = 1
    def LDrr_be(self): self.CPU.B = self.CPU.E; self.CPU.M = 1
    def LDrr_bh(self): self.CPU.B = self.CPU.H; self.CPU.M = 1
    def LDrr_bl(self): self.CPU.B = self.CPU.L; self.CPU.M = 1
    def LDrr_ba(self): self.CPU.B = self.CPU.A; self.CPU.M = 1

    def LDrr_cb(self): self.CPU.C = self.CPU.B; self.CPU.M = 1
    def LDrr_cc(self): self.CPU.C = self.CPU.C; self.CPU.M = 1
    def LDrr_cd(self): self.CPU.C = self.CPU.D; self.CPU.M = 1
    def LDrr_ce(self): self.CPU.C = self.CPU.E; self.CPU.M = 1
    def LDrr_ch(self): self.CPU.C = self.CPU.H; self.CPU.M = 1
    def LDrr_cl(self): self.CPU.C = self.CPU.L; self.CPU.M = 1
    def LDrr_ca(self): self.CPU.C = self.CPU.A; self.CPU.M = 1

    def LDrr_db(self): self.CPU.D = self.CPU.B; self.CPU.M = 1
    def LDrr_dc(self): self.CPU.D = self.CPU.C; self.CPU.M = 1
    def LDrr_dd(self): self.CPU.D = self.CPU.D; self.CPU.M = 1
    def LDrr_de(self): self.CPU.D = self.CPU.E; self.CPU.M = 1
    def LDrr_dh(self): self.CPU.D = self.CPU.H; self.CPU.M = 1
    def LDrr_dl(self): self.CPU.D = self.CPU.L; self.CPU.M = 1
    def LDrr_da(self): self.CPU.D = self.CPU.A; self.CPU.M = 1

    def LDrr_eb(self): self.CPU.E = self.CPU.B; self.CPU.M = 1
    def LDrr_ec(self): self.CPU.E = self.CPU.C; self.CPU.M = 1
    def LDrr_ed(self): self.CPU.E = self.CPU.D; self.CPU.M = 1
    def LDrr_ee(self): self.CPU.E = self.CPU.E; self.CPU.M = 1
    def LDrr_eh(self): self.CPU.E = self.CPU.H; self.CPU.M = 1
    def LDrr_el(self): self.CPU.E = self.CPU.L; self.CPU.M = 1
    def LDrr_ea(self): self.CPU.E = self.CPU.A; self.CPU.M = 1

    def LDrr_hb(self): self.CPU.H = self.CPU.B; self.CPU.M = 1
    def LDrr_hc(self): self.CPU.H = self.CPU.C; self.CPU.M = 1
    def LDrr_hd(self): self.CPU.H = self.CPU.D; self.CPU.M = 1
    def LDrr_he(self): self.CPU.H = self.CPU.E; self.CPU.M = 1
    def LDrr_hh(self): self.CPU.H = self.CPU.H; self.CPU.M = 1
    def LDrr_hl(self): self.CPU.H = self.CPU.L; self.CPU.M = 1
    def LDrr_ha(self): self.CPU.H = self.CPU.A; self.CPU.M = 1

    def LDrr_lb(self): self.CPU.L = self.CPU.B; self.CPU.M = 1
    def LDrr_lc(self): self.CPU.L = self.CPU.C; self.CPU.M = 1
    def LDrr_ld(self): self.CPU.L = self.CPU.D; self.CPU.M = 1
    def LDrr_le(self): self.CPU.L = self.CPU.E; self.CPU.M = 1
    def LDrr_lh(self): self.CPU.L = self.CPU.H; self.CPU.M = 1
    def LDrr_ll(self): self.CPU.L = self.CPU.L; self.CPU.M = 1
    def LDrr_la(self): self.CPU.L = self.CPU.A; self.CPU.M = 1

    def LDrr_ab(self): self.CPU.A = self.CPU.B; self.CPU.M = 1
    def LDrr_ac(self): self.CPU.A = self.CPU.C; self.CPU.M = 1
    def LDrr_ad(self): self.CPU.A = self.CPU.D; self.CPU.M = 1
    def LDrr_ae(self): self.CPU.A = self.CPU.E; self.CPU.M = 1
    def LDrr_ah(self): self.CPU.A = self.CPU.H; self.CPU.M = 1
    def LDrr_al(self): self.CPU.A = self.CPU.L; self.CPU.M = 1
    def LDrr_aa(self): self.CPU.A = self.CPU.A; self.CPU.M = 1

    # --- Load/store: memory addressed by HL ---
    def LDrHLm_b(self): self.CPU.B = self.MMU.rb((self.CPU.H << 8) + self.CPU.L); self.CPU.M = 2
    def LDrHLm_c(self): self.CPU.C = self.MMU.rb((self.CPU.H << 8) + self.CPU.L); self.CPU.M = 2
    def LDrHLm_d(self): self.CPU.D = self.MMU.rb((self.CPU.H << 8) + self.CPU.L); self.CPU.M = 2
    def LDrHLm_e(self): self.CPU.E = self.MMU.rb((self.CPU.H << 8) + self.CPU.L); self.CPU.M = 2
    def LDrHLm_h(self): self.CPU.H = self.MMU.rb((self.CPU.H << 8) + self.CPU.L); self.CPU.M = 2
    def LDrHLm_l(self): self.CPU.L = self.MMU.rb((self.CPU.H << 8) + self.CPU.L); self.CPU.M = 2
    def LDrHLm_a(self): self.CPU.A = self.MMU.rb((self.CPU.H << 8) + self.CPU.L); self.CPU.M = 2

    def LDHLmr_b(self): self.MMU.wb((self.CPU.H << 8) + self.CPU.L, self.CPU.B); self.CPU.M = 2
    def LDHLmr_c(self): self.MMU.wb((self.CPU.H << 8) + self.CPU.L, self.CPU.C); self.CPU.M = 2
    def LDHLmr_d(self): self.MMU.wb((self.CPU.H << 8) + self.CPU.L, self.CPU.D); self.CPU.M = 2
    def LDHLmr_e(self): self.MMU.wb((self.CPU.H << 8) + self.CPU.L, self.CPU.E); self.CPU.M = 2
    def LDHLmr_h(self): self.MMU.wb((self.CPU.H << 8) + self.CPU.L, self.CPU.H); self.CPU.M = 2
    def LDHLmr_l(self): self.MMU.wb((self.CPU.H << 8) + self.CPU.L, self.CPU.L); self.CPU.M = 2
    def LDHLmr_a(self): self.MMU.wb((self.CPU.H << 8) + self.CPU.L, self.CPU.A); self.CPU.M = 2

    # --- Load immediate values into registers ---
    def LDrn_b(self): self.CPU.B = self.MMU.rb(self.CPU.PC); self.CPU.PC += 1; self.CPU.M = 2
    def LDrn_c(self): self.CPU.C = self.MMU.rb(self.CPU.PC); self.CPU.PC += 1; self.CPU.M = 2
    def LDrn_d(self): self.CPU.D = self.MMU.rb(self.CPU.PC); self.CPU.PC += 1; self.CPU.M = 2
    def LDrn_e(self): self.CPU.E = self.MMU.rb(self.CPU.PC); self.CPU.PC += 1; self.CPU.M = 2
    def LDrn_h(self): self.CPU.H = self.MMU.rb(self.CPU.PC); self.CPU.PC += 1; self.CPU.M = 2
    def LDrn_l(self): self.CPU.L = self.MMU.rb(self.CPU.PC); self.CPU.PC += 1; self.CPU.M = 2
    def LDrn_a(self): self.CPU.A = self.MMU.rb(self.CPU.PC); self.CPU.PC += 1; self.CPU.M = 2

    # --- Load/store: immediate values, memory, and indirect addressing ---

    def LDHLmn(self): self.MMU.wb((self.CPU.H << 8) + self.CPU.L, self.MMU.rb(self.CPU.PC)); self.CPU.PC += 1; self.CPU.M = 3

    def LDBCmA(self): self.MMU.wb((self.CPU.B << 8) + self.CPU.C, self.CPU.A); self.CPU.M = 2
    def LDDEmA(self): self.MMU.wb((self.CPU.D << 8) + self.CPU.E, self.CPU.A); self.CPU.M = 2

    def LDmmA(self): self.MMU.wb(self.MMU.rw(self.CPU.PC), self.CPU.A); self.CPU.PC += 2; self.CPU.M = 4

    def LDABCm(self): self.CPU.A = self.MMU.rb((self.CPU.B << 8) + self.CPU.C); self.CPU.M = 2
    def LDADEm(self): self.CPU.A = self.MMU.rb((self.CPU.D << 8) + self.CPU.E); self.CPU.M = 2

    def LDAmm(self): self.CPU.A = self.MMU.rb(self.MMU.rw(self.CPU.PC)); self.CPU.PC += 2; self.CPU.M = 4

    def LDBCnn(self): self.CPU.C = self.MMU.rb(self.CPU.PC); self.CPU.B = self.MMU.rb(self.CPU.PC + 1); self.CPU.PC += 2; self.CPU.M = 3
    def LDDEnn(self): self.CPU.E = self.MMU.rb(self.CPU.PC); self.CPU.D = self.MMU.rb(self.CPU.PC + 1); self.CPU.PC += 2; self.CPU.M = 3
    def LDHLnn(self): self.CPU.L = self.MMU.rb(self.CPU.PC); self.CPU.H = self.MMU.rb(self.CPU.PC + 1); self.CPU.PC += 2; self.CPU.M = 3
    def LDSPnn(self): self.CPU.SP = self.MMU.rw(self.CPU.PC); self.CPU.PC += 2; self.CPU.M = 3

    def LDHLmm(self): 
        i = self.MMU.rw(self.CPU.PC)
        self.CPU.PC += 2
        self.CPU.L = self.MMU.rb(i)
        self.CPU.H = self.MMU.rb(i + 1)
        self.CPU.M = 5

    def LDmmHL(self): 
        i = self.MMU.rw(self.CPU.PC)
        self.CPU.PC += 2
        self.MMU.ww(i, (self.CPU.H << 8) + self.CPU.L)
        self.CPU.M = 5

    def LDHLIA(self): 
        self.MMU.wb((self.CPU.H << 8) + self.CPU.L, self.CPU.A)
        self.CPU.L = (self.CPU.L + 1) & 0xFF
        if self.CPU.L == 0: self.CPU.H = (self.CPU.H + 1) & 0xFF
        self.CPU.M = 2

    def LDAHLI(self): 
        self.CPU.A = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        self.CPU.L = (self.CPU.L + 1) & 0xFF
        if self.CPU.L == 0: self.CPU.H = (self.CPU.H + 1) & 0xFF
        self.CPU.M = 2

    def LDHLDA(self): 
        self.MMU.wb((self.CPU.H << 8) + self.CPU.L, self.CPU.A)
        self.CPU.L = (self.CPU.L - 1) & 0xFF
        if self.CPU.L == 0xFF: self.CPU.H = (self.CPU.H - 1) & 0xFF
        self.CPU.M = 2

    def LDAHLD(self): 
        self.CPU.A = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        self.CPU.L = (self.CPU.L - 1) & 0xFF
        if self.CPU.L == 0xFF: self.CPU.H = (self.CPU.H - 1) & 0xFF
        self.CPU.M = 2

    def LDAIOn(self): 
        self.CPU.A = self.MMU.rb(0xFF00 + self.MMU.rb(self.CPU.PC))
        self.CPU.PC += 1
        self.CPU.M = 3

    def LDIOnA(self): 
        self.MMU.wb(0xFF00 + self.MMU.rb(self.CPU.PC), self.CPU.A)
        self.CPU.PC += 1
        self.CPU.M = 3

    def LDAIOC(self): 
        self.CPU.A = self.MMU.rb(0xFF00 + self.CPU.C)
        self.CPU.M = 2

    def LDIOCA(self): 
        self.MMU.wb(0xFF00 + self.CPU.C, self.CPU.A)
        self.CPU.M = 2

    #DEBUG - all flag fixes might be broken.
    '''
    def LDHLSPn(self): 
        i = self.MMU.rb(self.CPU.PC)
        self.CPU.PC += 1
        if i > 127: i = -((~i + 1) & 0xFF)
        i += self.CPU.SP
        self.CPU.H = (i >> 8) & 0xFF
        self.CPU.L = i & 0xFF
        self.CPU.M = 3
    '''
    #fix missing flags
    def LDHLSPn(self):
        i = self.MMU.rb(self.CPU.PC)
        self.CPU.PC = (self.CPU.PC + 1) & 0xFFFF
        sp = self.CPU.SP
        signed_i = i -256 if i>127 else i
        result = (sp+signed_i) & 0xFFFF

        self.CPU.F = 0
        if ((sp &0xF)+(i&0xF))>0xF:
            self.CPU.F |= 0x20
        if ((sp &0xFF)+(i&0xFF))>0xFF:
            self.CPU.F |= 0x10

        self.CPU.H = (result>>8) & 0xFF
        self.CPU.L = result & 0xFF
        self.CPU.M = 3

    #missed previously?

    def LDSPHL(self):
        self.CPU.SP = (self.CPU.H << 8) + self.CPU.L
        self.CPU.M = 2

    def SWAPHL(self):
        addr = (self.CPU.H << 8) | self.CPU.L
        tr = self.MMU.rb(addr)
        tr = ((tr & 0xF) << 4) | ((tr & 0xF0) >> 4)
        self.MMU.wb(addr, tr)
        self.CPU.F = 0 if tr else 0x80
        self.CPU.M = 4
    
    # --- Swap nibbles ---

    def SWAPr_b(self): 
        tr = self.CPU.B
        self.CPU.B = ((tr & 0xF) << 4) | ((tr & 0xF0) >> 4)
        self.CPU.F = 0 if self.CPU.B else 0x80
        #self.CPU.M = 1
        self.CPU.M = 2      #DEBUG: changed all SWAPs to 2 M cycles

    def SWAPr_c(self): 
        tr = self.CPU.C
        self.CPU.C = ((tr & 0xF) << 4) | ((tr & 0xF0) >> 4)
        self.CPU.F = 0 if self.CPU.C else 0x80
        self.CPU.M = 2

    def SWAPr_d(self): 
        tr = self.CPU.D
        self.CPU.D = ((tr & 0xF) << 4) | ((tr & 0xF0) >> 4)
        self.CPU.F = 0 if self.CPU.D else 0x80
        self.CPU.M = 2

    def SWAPr_e(self): 
        tr = self.CPU.E
        self.CPU.E = ((tr & 0xF) << 4) | ((tr & 0xF0) >> 4)
        self.CPU.F = 0 if self.CPU.E else 0x80
        self.CPU.M = 2

    def SWAPr_h(self): 
        tr = self.CPU.H
        self.CPU.H = ((tr & 0xF) << 4) | ((tr & 0xF0) >> 4)
        self.CPU.F = 0 if self.CPU.H else 0x80
        self.CPU.M = 2

    def SWAPr_l(self): 
        tr = self.CPU.L
        self.CPU.L = ((tr & 0xF) << 4) | ((tr & 0xF0) >> 4)
        self.CPU.F = 0 if self.CPU.L else 0x80
        self.CPU.M = 2

    def SWAPr_a(self): 
        tr = self.CPU.A
        self.CPU.A = ((tr & 0xF) << 4) | ((tr & 0xF0) >> 4)
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 2

    # --- ADD operations (A + r) ---

    def ADDr_b(self): 
        a = self.CPU.A
        self.CPU.A += self.CPU.B
        self.CPU.F = 0x10 if self.CPU.A > 0xFF else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if ((self.CPU.A ^ self.CPU.B ^ a) & 0x10): self.CPU.F |= 0x20
        self.CPU.M = 1

    def ADDr_c(self): 
        a = self.CPU.A
        self.CPU.A += self.CPU.C
        self.CPU.F = 0x10 if self.CPU.A > 0xFF else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if ((self.CPU.A ^ self.CPU.C ^ a) & 0x10): self.CPU.F |= 0x20
        self.CPU.M = 1

    def ADDr_d(self): 
        a = self.CPU.A
        self.CPU.A += self.CPU.D
        self.CPU.F = 0x10 if self.CPU.A > 0xFF else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if ((self.CPU.A ^ self.CPU.D ^ a) & 0x10): self.CPU.F |= 0x20
        self.CPU.M = 1

    def ADDr_e(self): 
        a = self.CPU.A
        self.CPU.A += self.CPU.E
        self.CPU.F = 0x10 if self.CPU.A > 0xFF else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if ((self.CPU.A ^ self.CPU.E ^ a) & 0x10): self.CPU.F |= 0x20
        self.CPU.M = 1

    def ADDr_h(self): 
        a = self.CPU.A
        self.CPU.A += self.CPU.H
        self.CPU.F = 0x10 if self.CPU.A > 0xFF else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if ((self.CPU.A ^ self.CPU.H ^ a) & 0x10): self.CPU.F |= 0x20
        self.CPU.M = 1

    def ADDr_l(self): 
        a = self.CPU.A
        self.CPU.A += self.CPU.L
        self.CPU.F = 0x10 if self.CPU.A > 0xFF else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if ((self.CPU.A ^ self.CPU.L ^ a) & 0x10): self.CPU.F |= 0x20
        self.CPU.M = 1

    def ADDr_a(self): 
        a = self.CPU.A
        self.CPU.A += self.CPU.A
        self.CPU.F = 0x10 if self.CPU.A > 0xFF else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        #if ((self.CPU.A ^ self.CPU.A ^ a) & 0x10): self.CPU.F |= 0x20
        if self.CPU.A & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def ADDHL(self):
        a = self.CPU.A
        m = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        self.CPU.A += m
        self.CPU.F = 0x10 if self.CPU.A > 255 else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ a ^ m) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 2

    def ADDn(self):
        a = self.CPU.A
        m = self.MMU.rb(self.CPU.PC)
        self.CPU.A += m
        self.CPU.PC += 1
        self.CPU.F = 0x10 if self.CPU.A > 255 else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ a ^ m) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 2

    #DEBUG: changing M from 3 cycles to 2
    def ADDHLBC(self):
        hl = (self.CPU.H << 8) + self.CPU.L
        bc = (self.CPU.B << 8) + self.CPU.C
        result = hl+bc

        self.CPU.F &= 0x80  #keep Z, clear N/H/C flags

        if ((hl&0xFFF) + (bc&0xFFF)) > 0xFFF:
            self.CPU.F |= 0x20
        if result > 0xFFFF:
            self.CPU.F |= 0x10
        self.CPU.H = (result >> 8) & 0xFF
        self.CPU.L = result & 0xFF
        self.CPU.M = 2

    def ADDHLDE(self):
        hl = (self.CPU.H << 8) + self.CPU.L
        de = (self.CPU.D << 8) + self.CPU.E
        result = hl+de

        self.CPU.F &= 0x80  #keep Z, clear N/H/C flags

        if ((hl&0xFFF) + (de&0xFFF)) > 0xFFF:
            self.CPU.F |= 0x20
        if result > 0xFFFF:
            self.CPU.F |= 0x10
        self.CPU.H = (result >> 8) & 0xFF
        self.CPU.L = result & 0xFF
        self.CPU.M = 2

    def ADDHLHL(self):
        hl = (self.CPU.H << 8) + self.CPU.L
        result = hl+hl

        self.CPU.F &= 0x80  #keep Z, clear N/H/C flags

        if ((hl&0xFFF) + (hl&0xFFF)) > 0xFFF:
            self.CPU.F |= 0x20
        if result > 0xFFFF:
            self.CPU.F |= 0x10
        self.CPU.H = (result >> 8) & 0xFF
        self.CPU.L = result & 0xFF
        self.CPU.M = 2

    def ADDHLSP(self):
        hl = (self.CPU.H << 8) + self.CPU.L
        sp = self.CPU.SP
        result = hl+sp

        self.CPU.F &= 0x80  #keep Z, clear N/H/C flags

        if ((hl&0xFFF) + (sp&0xFFF)) > 0xFFF:
            self.CPU.F |= 0x20
        if result > 0xFFFF:
            self.CPU.F |= 0x10
        self.CPU.H = (result >> 8) & 0xFF
        self.CPU.L = result & 0xFF
        self.CPU.M = 2

    '''def ADDSPn(self):             #Faulty; doesn't factor in flags
        i = self.MMU.rb(self.CPU.PC)
        if i > 127:
            i = -((~i + 1) & 0xFF)
        self.CPU.PC += 1
        self.CPU.SP = (self.CPU.SP + i) & 0xFFFF
        self.CPU.M = 4'''

    def ADDSPn(self):
        i = self.MMU.rb(self.CPU.PC)
        self.CPU.PC = (self.CPU.PC +1) & 0xFFFF
        sp = self.CPU.SP
        signed_i = i-256 if i>127 else i
        result = (sp+signed_i) & 0xFFFF
        
        self.CPU.F=0
        if ((sp&0xF)+(i&0xF))> 0xF:
            self.CPU.F |= 0x20
        if ((sp&0xFF)+(i&0xFF))>0xFF:
            self.CPU.F|=0x10

        self.CPU.SP=result
        self.CPU.M=4

    def ADCr_b(self):
        a = self.CPU.A
        self.CPU.A += self.CPU.B
        self.CPU.A += 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x10 if self.CPU.A > 255 else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.B ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def ADCr_c(self):
        a = self.CPU.A
        self.CPU.A += self.CPU.C
        self.CPU.A += 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x10 if self.CPU.A > 255 else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.C ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def ADCr_d(self):
        a = self.CPU.A
        self.CPU.A += self.CPU.D
        self.CPU.A += 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x10 if self.CPU.A > 255 else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.D ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def ADCr_e(self):
        a = self.CPU.A
        self.CPU.A += self.CPU.E
        self.CPU.A += 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x10 if self.CPU.A > 255 else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.E ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def ADCr_h(self):
        a = self.CPU.A
        self.CPU.A += self.CPU.H
        self.CPU.A += 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x10 if self.CPU.A > 255 else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.H ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def ADCr_l(self):
        a = self.CPU.A
        self.CPU.A += self.CPU.L
        self.CPU.A += 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x10 if self.CPU.A > 255 else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.L ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def ADCr_a(self):
        a = self.CPU.A
        self.CPU.A += self.CPU.A
        self.CPU.A += 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x10 if self.CPU.A > 255 else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        #if (self.CPU.A ^ self.CPU.A ^ a) & 0x10: self.CPU.F |= 0x20
        if self.CPU.A & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def ADCHL(self):
        a = self.CPU.A
        m = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        self.CPU.A += m
        self.CPU.A += 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x10 if self.CPU.A > 255 else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ m ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 2

    def ADCn(self):
        a = self.CPU.A
        m = self.MMU.rb(self.CPU.PC)
        self.CPU.A += m
        self.CPU.PC += 1
        self.CPU.A += 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x10 if self.CPU.A > 255 else 0
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ m ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 2

    def SUBr_b(self):
        a = self.CPU.A
        self.CPU.A -= self.CPU.B
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.B ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def SUBr_c(self):
        a = self.CPU.A
        self.CPU.A -= self.CPU.C
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.C ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def SUBr_d(self):
        a = self.CPU.A
        self.CPU.A -= self.CPU.D
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.D ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def SUBr_e(self):
        a = self.CPU.A
        self.CPU.A -= self.CPU.E
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.E ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def SUBr_h(self):
        a = self.CPU.A
        self.CPU.A -= self.CPU.H
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.H ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def SUBr_l(self):
        a = self.CPU.A
        self.CPU.A -= self.CPU.L
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.L ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def SUBr_a(self):
        a = self.CPU.A
        self.CPU.A -= self.CPU.A
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        #if (self.CPU.A ^ self.CPU.A ^ a) & 0x10: self.CPU.F |= 0x20
        if self.CPU.A & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def SUBHL(self):
        a = self.CPU.A
        m = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        self.CPU.A -= m
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ m ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 2

    def SUBn(self):
        a = self.CPU.A
        m = self.MMU.rb(self.CPU.PC)
        self.CPU.A -= m
        self.CPU.PC += 1
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ m ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 2

    def SBCr_b(self):
        a = self.CPU.A
        self.CPU.A -= self.CPU.B
        self.CPU.A -= 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.B ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def SBCr_c(self):
        a = self.CPU.A
        self.CPU.A -= self.CPU.C
        self.CPU.A -= 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.C ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def SBCr_d(self):
        a = self.CPU.A
        self.CPU.A -= self.CPU.D
        self.CPU.A -= 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.D ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def SBCr_e(self):
        a = self.CPU.A
        self.CPU.A -= self.CPU.E
        self.CPU.A -= 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.E ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def SBCr_h(self):
        a = self.CPU.A
        self.CPU.A -= self.CPU.H
        self.CPU.A -= 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.H ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def SBCr_l(self):
        a = self.CPU.A
        self.CPU.A -= self.CPU.L
        self.CPU.A -= 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.L ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def SBCr_a(self):
        a = self.CPU.A
        self.CPU.A -= self.CPU.A
        self.CPU.A -= 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        #if (self.CPU.A ^ self.CPU.A ^ a) & 0x10: self.CPU.F |= 0x20
        if self.CPU.A & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def SBCHL(self):
        a = self.CPU.A
        m = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        self.CPU.A -= m
        self.CPU.A -= 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ m ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 2

    def SBCn(self):
        a = self.CPU.A
        m = self.MMU.rb(self.CPU.PC)
        self.CPU.A -= m
        self.CPU.PC += 1
        self.CPU.A -= 1 if self.CPU.F & 0x10 else 0
        self.CPU.F = 0x50 if self.CPU.A < 0 else 0x40
        self.CPU.A &= 0xFF
        if self.CPU.A == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ m ^ a) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 2

    def CPr_b(self):
        i = self.CPU.A
        i -= self.CPU.B
        self.CPU.F = 0x50 if i < 0 else 0x40
        i &= 0xFF
        if i == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.B ^ i) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def CPr_c(self):
        i = self.CPU.A
        i -= self.CPU.C
        self.CPU.F = 0x50 if i < 0 else 0x40
        i &= 0xFF
        if i == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.C ^ i) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def CPr_d(self):
        i = self.CPU.A
        i -= self.CPU.D
        self.CPU.F = 0x50 if i < 0 else 0x40
        i &= 0xFF
        if i == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.D ^ i) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def CPr_e(self):
        i = self.CPU.A
        i -= self.CPU.E
        self.CPU.F = 0x50 if i < 0 else 0x40
        i &= 0xFF
        if i == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.E ^ i) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def CPr_h(self):
        i = self.CPU.A
        i -= self.CPU.H
        self.CPU.F = 0x50 if i < 0 else 0x40
        i &= 0xFF
        if i == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.H ^ i) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def CPr_l(self):
        i = self.CPU.A
        i -= self.CPU.L
        self.CPU.F = 0x50 if i < 0 else 0x40
        i &= 0xFF
        if i == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.L ^ i) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def CPr_a(self):
        i = self.CPU.A
        i -= self.CPU.A
        self.CPU.F = 0x50 if i < 0 else 0x40
        i &= 0xFF
        if i == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ self.CPU.A ^ i) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 1

    def CPHL(self):
        i = self.CPU.A
        m = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        i -= m
        self.CPU.F = 0x50 if i < 0 else 0x40
        i &= 0xFF
        if i == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ i ^ m) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 2

    def CPn(self):
        i = self.CPU.A
        m = self.MMU.rb(self.CPU.PC)
        i -= m
        self.CPU.PC += 1
        self.CPU.F = 0x50 if i < 0 else 0x40
        i &= 0xFF
        if i == 0: self.CPU.F |= 0x80
        if (self.CPU.A ^ i ^ m) & 0x10: self.CPU.F |= 0x20
        self.CPU.M = 2

    '''def DAA(self):  #Doesnt use flags
        a = self.CPU.A
        if (self.CPU.F & 0x20) or (self.CPU.A & 0x0F) > 9:
            self.CPU.A += 6
        self.CPU.F &= 0xEF
        if (self.CPU.F & 0x20) or a > 0x99:
            self.CPU.A += 0x60
            self.CPU.F |= 0x10
        self.CPU.M = 1'''

    def DAA(self):
        a = self.CPU.A
        flagN = self.CPU.F & 0x40
        flagH = self.CPU.F & 0x20
        flagC = self.CPU.F & 0x10

        correction = 0
        set_carry = False

        if flagN:
            if flagH:
                correction |= 0x06
            if flagC:
                correction |= 0x60
                set_carry = True
            a = (a-correction) & 0xFF
        else:
            if flagH or (a& 0x0F) >9:
                correction|= 0x06
            if flagC or a>0x99:
                correction |= 0x60
                set_carry = True
            a = (a+correction)&0xFF

        self.CPU.A = a
        self.CPU.F &= 0x40
        if a==0:
            self.CPU.F |= 0x80
        if set_carry:
            self.CPU.F |= 0x10

        self.CPU.M = 1
    
    def ANDr_b(self):
        self.CPU.A &= self.CPU.B
        self.CPU.A &= 0xFF
        #set H flag if nonzero, otherwise set Z+H flags
        #Turns out, this is a hardware bug on the gameboy, but gotta emulate that too.
        self.CPU.F = 0x20 if self.CPU.A else 0xA0
        self.CPU.M = 1

    def ANDr_c(self):
        self.CPU.A &= self.CPU.C
        self.CPU.A &= 0xFF
        self.CPU.F = 0x20 if self.CPU.A else 0xA0
        self.CPU.M = 1

    def ANDr_d(self):
        self.CPU.A &= self.CPU.D
        self.CPU.A &= 0xFF
        self.CPU.F = 0x20 if self.CPU.A else 0xA0
        self.CPU.M = 1

    def ANDr_e(self):
        self.CPU.A &= self.CPU.E
        self.CPU.A &= 0xFF
        self.CPU.F = 0x20 if self.CPU.A else 0xA0
        self.CPU.M = 1

    def ANDr_h(self):
        self.CPU.A &= self.CPU.H
        self.CPU.A &= 0xFF
        self.CPU.F = 0x20 if self.CPU.A else 0xA0
        self.CPU.M = 1

    def ANDr_l(self):
        self.CPU.A &= self.CPU.L
        self.CPU.A &= 0xFF
        self.CPU.F = 0x20 if self.CPU.A else 0xA0
        self.CPU.M = 1

    def ANDr_a(self):
        self.CPU.A &= self.CPU.A
        self.CPU.A &= 0xFF
        self.CPU.F = 0x20 if self.CPU.A else 0xA0
        self.CPU.M = 1

    def ANDHL(self):
        self.CPU.A &= self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        self.CPU.A &= 0xFF
        self.CPU.F = 0x20 if self.CPU.A else 0xA0
        self.CPU.M = 2

    def ANDn(self):
        self.CPU.A &= self.MMU.rb(self.CPU.PC)
        self.CPU.PC += 1
        self.CPU.A &= 0xFF
        self.CPU.F = 0x20 if self.CPU.A else 0xA0
        self.CPU.M = 2

    def ORr_b(self):
        self.CPU.A |= self.CPU.B
        self.CPU.A &= 0xFF
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 1

    def ORr_c(self):
        self.CPU.A |= self.CPU.C
        self.CPU.A &= 0xFF
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 1

    def ORr_d(self):
        self.CPU.A |= self.CPU.D
        self.CPU.A &= 0xFF
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 1

    def ORr_e(self):
        self.CPU.A |= self.CPU.E
        self.CPU.A &= 0xFF
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 1

    def ORr_h(self):
        self.CPU.A |= self.CPU.H
        self.CPU.A &= 0xFF
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 1

    def ORr_l(self):
        self.CPU.A |= self.CPU.L
        self.CPU.A &= 0xFF
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 1

    def ORr_a(self):
        self.CPU.A |= self.CPU.A
        self.CPU.A &= 0xFF
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 1

    def ORHL(self):
        self.CPU.A |= self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        self.CPU.A &= 0xFF
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 2

    def ORn(self):
        self.CPU.A |= self.MMU.rb(self.CPU.PC)
        self.CPU.PC += 1
        self.CPU.A &= 0xFF
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 2

    def XORr_b(self):
        self.CPU.A ^= self.CPU.B
        self.CPU.A &= 255
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 1

    def XORr_c(self):
        self.CPU.A ^= self.CPU.C
        self.CPU.A &= 255
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 1

    def XORr_d(self):
        self.CPU.A ^= self.CPU.D
        self.CPU.A &= 255
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 1

    def XORr_e(self):
        self.CPU.A ^= self.CPU.E
        self.CPU.A &= 255
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 1

    def XORr_h(self):
        self.CPU.A ^= self.CPU.H
        self.CPU.A &= 255
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 1

    def XORr_l(self):
        self.CPU.A ^= self.CPU.L
        self.CPU.A &= 255
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 1

    def XORr_a(self):
        self.CPU.A ^= self.CPU.A
        self.CPU.A &= 255
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 1

    def XORHL(self):
        self.CPU.A ^= self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        self.CPU.A &= 255
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 2

    def XORn(self):
        self.CPU.A ^= self.MMU.rb(self.CPU.PC)
        self.CPU.PC += 1
        self.CPU.A &= 255
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 2

    '''def INCr_b(self):
        self.CPU.B += 1
        self.CPU.B &= 255
        self.CPU.F = 0 if self.CPU.B else 0x80
        self.CPU.M = 1

    def INCr_c(self):
        self.CPU.C += 1
        self.CPU.C &= 255
        self.CPU.F = 0 if self.CPU.C else 0x80
        self.CPU.M = 1

    def INCr_d(self):
        self.CPU.D += 1
        self.CPU.D &= 255
        self.CPU.F = 0 if self.CPU.D else 0x80
        self.CPU.M = 1

    def INCr_e(self):
        self.CPU.E += 1
        self.CPU.E &= 255
        self.CPU.F = 0 if self.CPU.E else 0x80
        self.CPU.M = 1

    def INCr_h(self):
        self.CPU.H += 1
        self.CPU.H &= 255
        self.CPU.F = 0 if self.CPU.H else 0x80
        self.CPU.M = 1

    def INCr_l(self):
        self.CPU.L += 1
        self.CPU.L &= 255
        self.CPU.F = 0 if self.CPU.L else 0x80
        self.CPU.M = 1

    def INCr_a(self):
        self.CPU.A += 1
        self.CPU.A &= 255
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 1'''

    #redoing above to correctly implement flags
    def INCr_b(self):
        old= self.CPU.B
        new = (old+1) &0xFF
        self.CPU.B=new
        flag = self.CPU.F & 0x10

        if new == 0:
            flag |= 0x80

        if (old&0x0f) == 0x0F:
            flag |= 0x20

        self.CPU.F = flag
        self.CPU.M = 1

    def INCr_c(self):
        old= self.CPU.C
        new = (old+1) &0xFF
        self.CPU.C=new
        flag = self.CPU.F & 0x10

        if new == 0:
            flag |= 0x80

        if (old&0x0f) == 0x0F:
            flag |= 0x20

        self.CPU.F = flag
        self.CPU.M = 1
        
    def INCr_d(self):
        old= self.CPU.D
        new = (old+1) &0xFF
        self.CPU.D=new
        flag = self.CPU.F & 0x10

        if new == 0:
            flag |= 0x80

        if (old&0x0f) == 0x0F:
            flag |= 0x20

        self.CPU.F = flag
        self.CPU.M = 1

    def INCr_e(self):
        old= self.CPU.E
        new = (old+1) &0xFF
        self.CPU.E=new
        flag = self.CPU.F & 0x10

        if new == 0:
            flag |= 0x80

        if (old&0x0f) == 0x0F:
            flag |= 0x20

        self.CPU.F = flag
        self.CPU.M = 1

    def INCr_h(self):
        old= self.CPU.H
        new = (old+1) &0xFF
        self.CPU.H=new
        flag = self.CPU.F & 0x10

        if new == 0:
            flag |= 0x80

        if (old&0x0f) == 0x0F:
            flag |= 0x20

        self.CPU.F = flag
        self.CPU.M = 1

    def INCr_l(self):
        old= self.CPU.L
        new = (old+1) &0xFF
        self.CPU.L=new
        flag = self.CPU.F & 0x10

        if new == 0:
            flag |= 0x80

        if (old&0x0f) == 0x0F:
            flag |= 0x20

        self.CPU.F = flag
        self.CPU.M = 1

    def INCr_a(self):
        old= self.CPU.A
        new = (old+1) &0xFF
        self.CPU.A=new
        flag = self.CPU.F & 0x10

        if new == 0:
            flag |= 0x80

        if (old&0x0f) == 0x0F:
            flag |= 0x20

        self.CPU.F = flag
        self.CPU.M = 1
    
    def INCHLm(self):
        addr = (self.CPU.H << 8) + self.CPU.L
        old = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        i = (old + 1) & 0xFF
        #i &= 255
        self.MMU.wb(addr, i)
        #self.CPU.F = 0 if i else 0x80

        flag = self.CPU.F & 0x10

        if i == 0:
            flag |= 0x80

        if (old&0x0f) == 0x0F:
            flag |= 0x20

        self.CPU.F = flag
        
        self.CPU.M = 3

    '''def DECr_b(self):
        self.CPU.B -= 1
        self.CPU.B &= 255
        self.CPU.F = 0 if self.CPU.B else 0x80
        self.CPU.M = 1

    def DECr_c(self):
        self.CPU.C -= 1
        self.CPU.C &= 255
        self.CPU.F = 0 if self.CPU.C else 0x80
        self.CPU.M = 1

    def DECr_d(self):
        self.CPU.D -= 1
        self.CPU.D &= 255
        self.CPU.F = 0 if self.CPU.D else 0x80
        self.CPU.M = 1

    def DECr_e(self):
        self.CPU.E -= 1
        self.CPU.E &= 255
        self.CPU.F = 0 if self.CPU.E else 0x80
        self.CPU.M = 1

    def DECr_h(self):
        self.CPU.H -= 1
        self.CPU.H &= 255
        self.CPU.F = 0 if self.CPU.H else 0x80
        self.CPU.M = 1

    def DECr_l(self):
        self.CPU.L -= 1
        self.CPU.L &= 255
        self.CPU.F = 0 if self.CPU.L else 0x80
        self.CPU.M = 1

    def DECr_a(self):
        self.CPU.A -= 1
        self.CPU.A &= 255
        self.CPU.F = 0 if self.CPU.A else 0x80
        self.CPU.M = 1'''

    #same again, fixing flag behaviour
    def DECr_b(self):
        old= self.CPU.B
        new = (old-1) &0xFF
        self.CPU.B=new
        
        flag = self.CPU.F & 0x10
        flag|=0x40
        if new == 0:
            flag |= 0x80

        if (old & 0x0F) == 0:
            flag |= 0x20

        self.CPU.F = flag
        self.CPU.M = 1

    def DECr_c(self):
        old= self.CPU.C
        new = (old-1) &0xFF
        self.CPU.C=new
        
        flag = self.CPU.F & 0x10
        flag|=0x40
        if new == 0:
            flag |= 0x80

        if (old & 0x0F) == 0:
            flag |= 0x20

        self.CPU.F = flag
        self.CPU.M = 1
        
    def DECr_d(self):
        old= self.CPU.D
        new = (old-1) &0xFF
        self.CPU.D=new
        
        flag = self.CPU.F & 0x10
        flag |= 0x40
        if new == 0:
            flag |= 0x80

        if (old & 0x0F) == 0:
            flag |= 0x20

        self.CPU.F = flag
        self.CPU.M = 1

    def DECr_e(self):
        old= self.CPU.E
        new = (old-1) &0xFF
        self.CPU.E=new
        
        flag = self.CPU.F & 0x10
        flag |= 0x40
        if new == 0:
            flag |= 0x80

        if (old & 0x0F) == 0:
            flag |= 0x20

        self.CPU.F = flag
        self.CPU.M = 1

    def DECr_h(self):
        old= self.CPU.H
        new = (old-1) &0xFF
        self.CPU.H=new
        
        flag = self.CPU.F & 0x10
        flag |= 0x40
        if new == 0:
            flag |= 0x80

        if (old & 0x0F) == 0:
            flag |= 0x20

        self.CPU.F = flag
        self.CPU.M = 1

    def DECr_l(self):
        old= self.CPU.L
        new = (old-1) &0xFF
        self.CPU.L=new
        
        flag = self.CPU.F & 0x10
        flag |= 0x40
        if new == 0:
            flag |= 0x80

        if (old & 0x0F) == 0:
            flag |= 0x20

        self.CPU.F = flag
        self.CPU.M = 1

    def DECr_a(self):
        old= self.CPU.A
        new = (old-1) &0xFF
        self.CPU.A=new
        
        flag = self.CPU.F & 0x10
        flag |= 0x40
        if new == 0:
            flag |= 0x80

        if (old & 0x0F) == 0:
            flag |= 0x20

        self.CPU.F = flag
        self.CPU.M = 1

    ###
    '''def DECHLm(self):
        i = self.MMU.rb((self.CPU.H << 8) + self.CPU.L) - 1
        i &= 255
        self.MMU.wb((self.CPU.H << 8) + self.CPU.L, i)
        self.CPU.F = 0 if i else 0x80
        self.CPU.M = 3'''

    def DECHLm(self):
        addr = (self.CPU.H << 8) + self.CPU.L
        old = self.MMU.rb(addr)
        i = (old-1) & 0xFF
        self.MMU.wb(addr,i)
        flag = self.CPU.F & 0x10
        flag |= 0x40
        if i == 0:
            flag |= 0x80

        if (old & 0x0F) == 0:
            flag |= 0x20

        self.CPU.F = flag
        self.CPU.M = 3
        

    ###
    def INCBC(self):
        self.CPU.C = (self.CPU.C + 1) & 0xFF
        if self.CPU.C == 0:
            self.CPU.B = (self.CPU.B + 1) & 0xFF
        self.CPU.M = 2

    def INCDE(self):
        self.CPU.E = (self.CPU.E + 1) & 0xFF
        if self.CPU.E == 0:
            self.CPU.D = (self.CPU.D + 1) & 0xFF
        self.CPU.M = 2

    def INCHL(self):
        self.CPU.L = (self.CPU.L + 1) & 0xFF
        if self.CPU.L == 0:
            self.CPU.H = (self.CPU.H + 1) & 0xFF
        self.CPU.M = 2

    def INCSP(self):
        self.CPU.SP = (self.CPU.SP + 1) & 0xFFFF
        self.CPU.M = 2


    def DECBC(self):
        self.CPU.C = (self.CPU.C - 1) & 0xFF
        if self.CPU.C == 0xFF:
            self.CPU.B = (self.CPU.B - 1) & 0xFF
        self.CPU.M = 2

    def DECDE(self):
        self.CPU.E = (self.CPU.E - 1) & 0xFF
        if self.CPU.E == 0xFF:
            self.CPU.D = (self.CPU.D - 1) & 0xFF
        self.CPU.M = 2

    def DECHL(self):
        self.CPU.L = (self.CPU.L - 1) & 0xFF
        if self.CPU.L == 0xFF:
            self.CPU.H = (self.CPU.H - 1) & 0xFF
        self.CPU.M = 2

    def DECSP(self):
        self.CPU.SP = (self.CPU.SP - 1) & 0xFFFF
        self.CPU.M = 2

    def BIT0b(self):
        self.CPU.F &= 0x1F          # Clear upper flag bits except carry & half-carry etc.
        self.CPU.F |= 0x20          # Set the "H" flag (half-carry) always
        self.CPU.F |= 0x80 if not (self.CPU.B & 0x01) else 0  # Set Z flag if bit 0 is 0
        self.CPU.M = 2

    def BIT0c(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20
        self.CPU.F |= 0x80 if not (self.CPU.C & 0x01) else 0
        self.CPU.M = 2

    def BIT0d(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20
        self.CPU.F |= 0x80 if not (self.CPU.D & 0x01) else 0
        self.CPU.M = 2

    def BIT0e(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20
        self.CPU.F |= 0x80 if not (self.CPU.E & 0x01) else 0
        self.CPU.M = 2

    def BIT0h(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20
        self.CPU.F |= 0x80 if not (self.CPU.H & 0x01) else 0
        self.CPU.M = 2

    def BIT0l(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20
        self.CPU.F |= 0x80 if not (self.CPU.L & 0x01) else 0
        self.CPU.M = 2

    def BIT0a(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20
        self.CPU.F |= 0x80 if not (self.CPU.A & 0x01) else 0
        self.CPU.M = 2

    def BIT0m(self):
        val = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20
        self.CPU.F |= 0x80 if not (val & 0x01) else 0
        self.CPU.M = 3

    def RES0b(self):
        self.CPU.B &= 0xFE  # Clear bit 0
        self.CPU.M = 2

    def RES0c(self):
        self.CPU.C &= 0xFE
        self.CPU.M = 2

    def RES0d(self):
        self.CPU.D &= 0xFE
        self.CPU.M = 2

    def RES0e(self):
        self.CPU.E &= 0xFE
        self.CPU.M = 2

    def RES0h(self):
        self.CPU.H &= 0xFE
        self.CPU.M = 2

    def RES0l(self):
        self.CPU.L &= 0xFE
        self.CPU.M = 2

    def RES0a(self):
        self.CPU.A &= 0xFE
        self.CPU.M = 2

    def RES0m(self):
        addr = (self.CPU.H << 8) + self.CPU.L
        val = self.MMU.rb(addr) & 0xFE  # Clear bit 0 of memory value
        self.MMU.wb(addr, val)
        self.CPU.M = 4

    def SET0b(self):
        self.CPU.B |= 0x01  # Set bit 0
        self.CPU.M = 2

    def SET0c(self):
        self.CPU.C |= 0x01
        self.CPU.M = 2

    def SET0d(self):
        self.CPU.D |= 0x01
        self.CPU.M = 2

    def SET0e(self):
        self.CPU.E |= 0x01
        self.CPU.M = 2

    def SET0h(self):
        self.CPU.H |= 0x01
        self.CPU.M = 2

    def SET0l(self):
        self.CPU.L |= 0x01
        self.CPU.M = 2

    def SET0a(self):
        self.CPU.A |= 0x01
        self.CPU.M = 2

    def SET0m(self):
        addr = (self.CPU.H << 8) + self.CPU.L
        val = self.MMU.rb(addr) | 0x01  # Set bit 0 of memory value
        self.MMU.wb(addr, val)
        self.CPU.M = 4

    def BIT1b(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20
        
        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.B & 0x02):
            flag |= 0x80
        self.CPU.F = flag
        self.CPU.M = 2

    def BIT1c(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.C & 0x02):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT1d(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.D & 0x02):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT1e(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.E & 0x02):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT1h(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.H & 0x02):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT1l(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.L & 0x02):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT1a(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.A & 0x02):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT1m(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.MMU.rb((self.CPU.H<<8)+self.CPU.L) & 0x02):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 3

    def RES1b(self):
        self.CPU.B &= 0xFD
        self.CPU.M = 2

    def RES1c(self):
        self.CPU.C &= 0xFD
        self.CPU.M = 2

    def RES1d(self):
        self.CPU.D &= 0xFD
        self.CPU.M = 2

    def RES1e(self):
        self.CPU.E &= 0xFD
        self.CPU.M = 2

    def RES1h(self):
        self.CPU.H &= 0xFD
        self.CPU.M = 2

    def RES1l(self):
        self.CPU.L &= 0xFD
        self.CPU.M = 2

    def RES1a(self):
        self.CPU.A &= 0xFD
        self.CPU.M = 2

    def RES1m(self):
        i = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        i &= 0xFD
        self.MMU.wb((self.CPU.H << 8) + self.CPU.L, i)
        self.CPU.M = 4

    def SET1b(self):
        self.CPU.B |= 0x02
        self.CPU.M = 2

    def SET1c(self):
        self.CPU.C |= 0x02
        self.CPU.M = 2

    def SET1d(self):
        self.CPU.D |= 0x02
        self.CPU.M = 2

    def SET1e(self):
        self.CPU.E |= 0x02
        self.CPU.M = 2

    def SET1h(self):
        self.CPU.H |= 0x02
        self.CPU.M = 2

    def SET1l(self):
        self.CPU.L |= 0x02
        self.CPU.M = 2

    def SET1a(self):
        self.CPU.A |= 0x02
        self.CPU.M = 2

    def SET1m(self):
        i = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        i |= 0x02
        self.MMU.wb((self.CPU.H << 8) + self.CPU.L, i)
        self.CPU.M = 4

    def BIT2b(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.B & 0x04):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT2c(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.C & 0x04):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT2d(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.D & 0x04):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT2e(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.E & 0x04):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT2h(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.H & 0x04):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT2l(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.L & 0x04):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT2a(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.A & 0x04):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT2m(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.MMU.rb((self.CPU.H << 8) + self.CPU.L) & 0x04):
            flag |= 0x80
        self.CPU.F = flag

        self.CPU.M = 3

    def RES2b(self):
        self.CPU.B &= 0xFB
        self.CPU.M = 2

    def RES2c(self):
        self.CPU.C &= 0xFB
        self.CPU.M = 2

    def RES2d(self):
        self.CPU.D &= 0xFB
        self.CPU.M = 2

    def RES2e(self):
        self.CPU.E &= 0xFB
        self.CPU.M = 2

    def RES2h(self):
        self.CPU.H &= 0xFB
        self.CPU.M = 2

    def RES2l(self):
        self.CPU.L &= 0xFB
        self.CPU.M = 2

    def RES2a(self):
        self.CPU.A &= 0xFB
        self.CPU.M = 2

    def RES2m(self):
        i = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        i &= 0xFB
        self.MMU.wb((self.CPU.H << 8) + self.CPU.L, i)
        self.CPU.M = 4

    def SET2b(self):
        self.CPU.B |= 0x04
        self.CPU.M = 2

    def SET2c(self):
        self.CPU.C |= 0x04
        self.CPU.M = 2

    def SET2d(self):
        self.CPU.D |= 0x04
        self.CPU.M = 2

    def SET2e(self):
        self.CPU.E |= 0x04
        self.CPU.M = 2

    def SET2h(self):
        self.CPU.H |= 0x04
        self.CPU.M = 2

    def SET2l(self):
        self.CPU.L |= 0x04
        self.CPU.M = 2

    def SET2a(self):
        self.CPU.A |= 0x04
        self.CPU.M = 2

    def SET2m(self):
        i = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        i |= 0x04
        self.MMU.wb((self.CPU.H << 8) + self.CPU.L, i)
        self.CPU.M = 4

    def BIT3b(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.B & 0x08):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT3c(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.C & 0x08):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT3d(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.D & 0x08):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT3e(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.E & 0x08):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT3h(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.H & 0x08):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT3l(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.L & 0x08):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT3a(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.A & 0x08):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT3m(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20
        
        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.MMU.rb((self.CPU.H << 8) + self.CPU.L) & 0x08):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 3

    def RES3b(self):
        self.CPU.B &= 0xF7
        self.CPU.M = 2

    def RES3c(self):
        self.CPU.C &= 0xF7
        self.CPU.M = 2

    def RES3d(self):
        self.CPU.D &= 0xF7
        self.CPU.M = 2

    def RES3e(self):
        self.CPU.E &= 0xF7
        self.CPU.M = 2

    def RES3h(self):
        self.CPU.H &= 0xF7
        self.CPU.M = 2

    def RES3l(self):
        self.CPU.L &= 0xF7
        self.CPU.M = 2

    def RES3a(self):
        self.CPU.A &= 0xF7
        self.CPU.M = 2

    def RES3m(self):
        i = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        i &= 0xF7
        self.MMU.wb((self.CPU.H << 8) + self.CPU.L, i)
        self.CPU.M = 4

    def SET3b(self):
        self.CPU.B |= 0x08
        self.CPU.M = 2

    def SET3c(self):
        self.CPU.C |= 0x08
        self.CPU.M = 2

    def SET3d(self):
        self.CPU.D |= 0x08
        self.CPU.M = 2

    def SET3e(self):
        self.CPU.E |= 0x08
        self.CPU.M = 2

    def SET3h(self):
        self.CPU.H |= 0x08
        self.CPU.M = 2

    def SET3l(self):
        self.CPU.L |= 0x08
        self.CPU.M = 2

    def SET3a(self):
        self.CPU.A |= 0x08
        self.CPU.M = 2

    def SET3m(self):
        i = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        i |= 0x08
        self.MMU.wb((self.CPU.H << 8) + self.CPU.L, i)
        self.CPU.M = 4

    def BIT4b(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.B & 0x10):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT4c(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.C & 0x10):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT4d(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.D & 0x10):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT4e(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.E & 0x10):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT4h(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.H & 0x10):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT4l(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.L & 0x10):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT4a(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.A & 0x10):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT4m(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.MMU.rb((self.CPU.H << 8) + self.CPU.L) & 0x10):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 3

    def RES4b(self):
        self.CPU.B &= 0xEF
        self.CPU.M = 2

    def RES4c(self):
        self.CPU.C &= 0xEF
        self.CPU.M = 2

    def RES4d(self):
        self.CPU.D &= 0xEF
        self.CPU.M = 2

    def RES4e(self):
        self.CPU.E &= 0xEF
        self.CPU.M = 2

    def RES4h(self):
        self.CPU.H &= 0xEF
        self.CPU.M = 2

    def RES4l(self):
        self.CPU.L &= 0xEF
        self.CPU.M = 2

    def RES4a(self):
        self.CPU.A &= 0xEF
        self.CPU.M = 2

    def RES4m(self):
        i = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        i &= 0xEF
        self.MMU.wb((self.CPU.H << 8) + self.CPU.L, i)
        self.CPU.M = 4

    def SET4b(self):
        self.CPU.B |= 0x10
        self.CPU.M = 2

    def SET4c(self):
        self.CPU.C |= 0x10
        self.CPU.M = 2

    def SET4d(self):
        self.CPU.D |= 0x10
        self.CPU.M = 2

    def SET4e(self):
        self.CPU.E |= 0x10
        self.CPU.M = 2

    def SET4h(self):
        self.CPU.H |= 0x10
        self.CPU.M = 2

    def SET4l(self):
        self.CPU.L |= 0x10
        self.CPU.M = 2

    def SET4a(self):
        self.CPU.A |= 0x10
        self.CPU.M = 2

    def SET4m(self):
        i = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        i |= 0x10
        self.MMU.wb((self.CPU.H << 8) + self.CPU.L, i)
        self.CPU.M = 4

    def BIT5b(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.B & 0x20):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT5c(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.C & 0x20):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT5d(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.D & 0x20):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT5e(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.E & 0x20):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT5h(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.H & 0x20):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT5l(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.L & 0x20):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT5a(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.A & 0x20):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT5m(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.MMU.rb((self.CPU.H << 8) + self.CPU.L) & 0x20):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 3

    def RES5b(self):
        self.CPU.B &= 0xDF
        self.CPU.M = 2

    def RES5c(self):
        self.CPU.C &= 0xDF
        self.CPU.M = 2

    def RES5d(self):
        self.CPU.D &= 0xDF
        self.CPU.M = 2

    def RES5e(self):
        self.CPU.E &= 0xDF
        self.CPU.M = 2

    def RES5h(self):
        self.CPU.H &= 0xDF
        self.CPU.M = 2

    def RES5l(self):
        self.CPU.L &= 0xDF
        self.CPU.M = 2

    def RES5a(self):
        self.CPU.A &= 0xDF
        self.CPU.M = 2

    def RES5m(self):
        i = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        i &= 0xDF
        self.MMU.wb((self.CPU.H << 8) + self.CPU.L, i)
        self.CPU.M = 4

    def SET5b(self):
        self.CPU.B |= 0x20
        self.CPU.M = 2

    def SET5c(self):
        self.CPU.C |= 0x20
        self.CPU.M = 2

    def SET5d(self):
        self.CPU.D |= 0x20
        self.CPU.M = 2

    def SET5e(self):
        self.CPU.E |= 0x20
        self.CPU.M = 2

    def SET5h(self):
        self.CPU.H |= 0x20
        self.CPU.M = 2

    def SET5l(self):
        self.CPU.L |= 0x20
        self.CPU.M = 2

    def SET5a(self):
        self.CPU.A |= 0x20
        self.CPU.M = 2

    def SET5m(self):
        i = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        i |= 0x20
        self.MMU.wb((self.CPU.H << 8) + self.CPU.L, i)
        self.CPU.M = 4

    def BIT6b(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.B & 0x40):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT6c(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.C & 0x40):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT6d(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.D & 0x40):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT6e(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.E & 0x40):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT6h(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.H & 0x40):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT6l(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.L & 0x40):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT6a(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.A & 0x40):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT6m(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.MMU.rb((self.CPU.H << 8) + self.CPU.L) & 0x40):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 3

    def RES6b(self):
        self.CPU.B &= 0xBF
        self.CPU.M = 2

    def RES6c(self):
        self.CPU.C &= 0xBF
        self.CPU.M = 2

    def RES6d(self):
        self.CPU.D &= 0xBF
        self.CPU.M = 2

    def RES6e(self):
        self.CPU.E &= 0xBF
        self.CPU.M = 2

    def RES6h(self):
        self.CPU.H &= 0xBF
        self.CPU.M = 2

    def RES6l(self):
        self.CPU.L &= 0xBF
        self.CPU.M = 2

    def RES6a(self):
        self.CPU.A &= 0xBF
        self.CPU.M = 2

    def RES6m(self):
        i = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        i &= 0xBF
        self.MMU.wb((self.CPU.H << 8) + self.CPU.L, i)
        self.CPU.M = 4

    def SET6b(self):
        self.CPU.B |= 0x40
        self.CPU.M = 2

    def SET6c(self):
        self.CPU.C |= 0x40
        self.CPU.M = 2

    def SET6d(self):
        self.CPU.D |= 0x40
        self.CPU.M = 2

    def SET6e(self):
        self.CPU.E |= 0x40
        self.CPU.M = 2

    def SET6h(self):
        self.CPU.H |= 0x40
        self.CPU.M = 2

    def SET6l(self):
        self.CPU.L |= 0x40
        self.CPU.M = 2

    def SET6a(self):
        self.CPU.A |= 0x40
        self.CPU.M = 2

    def SET6m(self):
        i = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        i |= 0x40
        self.MMU.wb((self.CPU.H << 8) + self.CPU.L, i)
        self.CPU.M = 4

    def BIT7b(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.B & 0x80):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT7c(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.C & 0x80):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT7d(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.D & 0x80):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT7e(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.E & 0x80):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT7h(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.H & 0x80):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT7l(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.L & 0x80):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT7a(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.CPU.A & 0x80):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 2

    def BIT7m(self):
        self.CPU.F &= 0x1F
        self.CPU.F |= 0x20

        flag = self.CPU.F & 0x10
        flag |= 0x20
        if not (self.MMU.rb((self.CPU.H << 8) + self.CPU.L) & 0x80):
            flag |= 0x80
        self.CPU.F = flag
        
        self.CPU.M = 3

    def RES7b(self):
        self.CPU.B &= 0x7F
        self.CPU.M = 2

    def RES7c(self):
        self.CPU.C &= 0x7F
        self.CPU.M = 2

    def RES7d(self):
        self.CPU.D &= 0x7F
        self.CPU.M = 2

    def RES7e(self):
        self.CPU.E &= 0x7F
        self.CPU.M = 2

    def RES7h(self):
        self.CPU.H &= 0x7F
        self.CPU.M = 2

    def RES7l(self):
        self.CPU.L &= 0x7F
        self.CPU.M = 2

    def RES7a(self):
        self.CPU.A &= 0x7F
        self.CPU.M = 2

    def RES7m(self):
        i = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        i &= 0x7F
        self.MMU.wb((self.CPU.H << 8) + self.CPU.L, i)
        self.CPU.M = 4

    def SET7b(self):
        self.CPU.B |= 0x80
        self.CPU.M = 2

    def SET7c(self):
        self.CPU.C |= 0x80
        self.CPU.M = 2

    def SET7d(self):
        self.CPU.D |= 0x80
        self.CPU.M = 2

    def SET7e(self):
        self.CPU.E |= 0x80
        self.CPU.M = 2

    def SET7h(self):
        self.CPU.H |= 0x80
        self.CPU.M = 2

    def SET7l(self):
        self.CPU.L |= 0x80
        self.CPU.M = 2

    def SET7a(self):
        self.CPU.A |= 0x80
        self.CPU.M = 2

    def SET7m(self):
        i = self.MMU.rb((self.CPU.H << 8) + self.CPU.L)
        i |= 0x80
        self.MMU.wb((self.CPU.H << 8) + self.CPU.L, i)
        self.CPU.M = 4

    # Get rotated, idiot

    def RLA(self):
        ci = 1 if self.CPU.F & 0x10 else 0
        co = 0x10 if self.CPU.A & 0x80 else 0
        self.CPU.A = ((self.CPU.A << 1) + ci) & 0xFF
        #self.CPU.F = (self.CPU.F & 0xEF) | co
        self.CPU.F = co
        self.CPU.M = 1

    def RLCA(self):
        ci = 1 if self.CPU.A & 0x80 else 0
        co = 0x10 if self.CPU.A & 0x80 else 0
        self.CPU.A = ((self.CPU.A << 1) + ci) & 0xFF
        #self.CPU.F = (self.CPU.F & 0xEF) | co
        self.CPU.F = co
        self.CPU.M = 1

    def RRA(self):
        ci = 0x80 if self.CPU.F & 0x10 else 0
        co = 0x10 if self.CPU.A & 1 else 0
        self.CPU.A = ((self.CPU.A >> 1) + ci) & 0xFF
        #self.CPU.F = (self.CPU.F & 0xEF) | co
        self.CPU.F = co
        self.CPU.M = 1

    def RRCA(self):
        ci = 0x80 if self.CPU.A & 1 else 0
        co = 0x10 if self.CPU.A & 1 else 0
        self.CPU.A = ((self.CPU.A >> 1) + ci) & 0xFF
        #self.CPU.F = (self.CPU.F & 0xEF) | co
        self.CPU.F = co
        self.CPU.M = 1

    def _RL_reg(self,reg):
        ci = 1 if self.CPU.F & 0x10 else 0
        co = 0x10 if reg & 0x80 else 0
        reg = ((reg << 1) + ci) & 0xFF
        self.CPU.F = 0 if reg else 0x80
        self.CPU.F = (self.CPU.F & 0xEF) | co
        return reg

    def RLr_b(self):
        self.CPU.B = self._RL_reg(self.CPU.B)
        self.CPU.M = 2

    def RLr_c(self):
        #print("CPU C is ",self.CPU.C)
        self.CPU.C = self._RL_reg(self.CPU.C)
        self.CPU.M = 2

    def RLr_d(self):
        self.CPU.D = self._RL_reg(self.CPU.D)
        self.CPU.M = 2

    def RLr_e(self):
        self.CPU.E = self._RL_reg(self.CPU.E)
        self.CPU.M = 2

    def RLr_h(self):
        self.CPU.H = self._RL_reg(self.CPU.H)
        self.CPU.M = 2

    def RLr_l(self):
        self.CPU.L = self._RL_reg(self.CPU.L)
        self.CPU.M = 2

    def RLr_a(self):
        self.CPU.A = self._RL_reg(self.CPU.A)
        self.CPU.M = 2

    def RLHL(self):
        addr = (self.CPU.H << 8) + self.CPU.L
        i = self.MMU.rb(addr)
        ci = 1 if self.CPU.F & 0x10 else 0
        co = 0x10 if i & 0x80 else 0
        i = ((i << 1) + ci) & 0xFF
        self.CPU.F = 0 if i else 0x80
        self.MMU.wb(addr, i)
        self.CPU.F = (self.CPU.F & 0xEF) | co
        self.CPU.M = 4

    def _RLC_reg(self,reg):
        ci = 1 if reg & 0x80 else 0
        co = 0x10 if reg & 0x80 else 0
        reg = ((reg << 1) + ci) & 0xFF
        self.CPU.F = 0 if reg else 0x80
        self.CPU.F = (self.CPU.F & 0xEF) | co
        return reg

    def RLCr_b(self):
        self.CPU.B = self._RLC_reg(self.CPU.B)
        self.CPU.M = 2

    def RLCr_c(self):
        self.CPU.C = self._RLC_reg(self.CPU.C)
        self.CPU.M = 2

    def RLCr_d(self):
        self.CPU.D = self._RLC_reg(self.CPU.D)
        self.CPU.M = 2

    def RLCr_e(self):
        self.CPU.E = self._RLC_reg(self.CPU.E)
        self.CPU.M = 2

    def RLCr_h(self):
        self.CPU.H = self._RLC_reg(self.CPU.H)
        self.CPU.M = 2

    def RLCr_l(self):
        self.CPU.L = self._RLC_reg(self.CPU.L)
        self.CPU.M = 2

    def RLCr_a(self):
        self.CPU.A = self._RLC_reg(self.CPU.A)
        self.CPU.M = 2

    def RLCHL(self):
        addr = (self.CPU.H << 8) + self.CPU.L
        i = self.MMU.rb(addr)
        ci = 1 if i & 0x80 else 0
        co = 0x10 if i & 0x80 else 0
        i = ((i << 1) + ci) & 0xFF
        self.CPU.F = 0 if i else 0x80
        self.MMU.wb(addr, i)
        self.CPU.F = (self.CPU.F & 0xEF) | co
        self.CPU.M = 4

    # Rotate right with carry
    def _RR_reg(self,reg):
        ci = 0x80 if self.CPU.F & 0x10 else 0
        co = 0x10 if reg & 1 else 0
        reg = ((reg >> 1) + ci) & 0xFF
        self.CPU.F = 0 if reg else 0x80
        self.CPU.F = (self.CPU.F & 0xEF) | co
        return reg

    def RRr_b(self):
        self.CPU.B = self._RR_reg(self.CPU.B)
        self.CPU.M = 2

    def RRr_c(self):
        self.CPU.C = self._RR_reg(self.CPU.C)
        self.CPU.M = 2

    def RRr_d(self):
        self.CPU.D = self._RR_reg(self.CPU.D)
        self.CPU.M = 2

    def RRr_e(self):
        self.CPU.E = self._RR_reg(self.CPU.E)
        self.CPU.M = 2

    def RRr_h(self):
        self.CPU.H = self._RR_reg(self.CPU.H)
        self.CPU.M = 2

    def RRr_l(self):
        self.CPU.L = self._RR_reg(self.CPU.L)
        self.CPU.M = 2

    def RRr_a(self):
        self.CPU.A = self._RR_reg(self.CPU.A)
        self.CPU.M = 2

    def RRHL(self):
        addr = (self.CPU.H << 8) + self.CPU.L
        i = self.MMU.rb(addr)
        ci = 0x80 if self.CPU.F & 0x10 else 0
        co = 0x10 if i & 1 else 0
        i = ((i >> 1) + ci) & 0xFF
        self.MMU.wb(addr, i)
        self.CPU.F = 0 if i else 0x80
        self.CPU.F = (self.CPU.F & 0xEF) | co
        self.CPU.M = 4

    def _RRC_reg(self,reg):
        ci = 0x80 if reg & 1 else 0
        co = 0x10 if reg & 1 else 0
        reg = ((reg >> 1) + ci) & 0xFF
        self.CPU.F = 0 if reg else 0x80
        self.CPU.F = (self.CPU.F & 0xEF) | co
        return reg

    def RRCr_b(self):
        self.CPU.B = self._RRC_reg(self.CPU.B)
        self.CPU.M = 2

    def RRCr_c(self):
        self.CPU.C = self._RRC_reg(self.CPU.C)
        self.CPU.M = 2

    def RRCr_d(self):
        self.CPU.D = self._RRC_reg(self.CPU.D)
        self.CPU.M = 2

    def RRCr_e(self):
        self.CPU.E = self._RRC_reg(self.CPU.E)
        self.CPU.M = 2

    def RRCr_h(self):
        self.CPU.H = self._RRC_reg(self.CPU.H)
        self.CPU.M = 2

    def RRCr_l(self):
        self.CPU.L = self._RRC_reg(self.CPU.L)
        self.CPU.M = 2

    def RRCr_a(self):
        self.CPU.A = self._RRC_reg(self.CPU.A)
        self.CPU.M = 2

    def RRCHL(self):
        addr = (self.CPU.H << 8) + self.CPU.L
        i = self.MMU.rb(addr)
        ci = 0x80 if i & 1 else 0
        co = 0x10 if i & 1 else 0
        i = ((i >> 1) + ci) & 0xFF
        self.MMU.wb(addr, i)
        self.CPU.F = 0 if i else 0x80
        self.CPU.F = (self.CPU.F & 0xEF) | co
        self.CPU.M = 4

    # Shift left arithmetic
    def _SLA_reg(self,reg):
        co = 0x10 if reg & 0x80 else 0
        reg = (reg << 1) & 0xFF
        self.CPU.F = 0 if reg else 0x80
        self.CPU.F = (self.CPU.F & 0xEF) | co
        return reg

    def SLAr_b(self):
        self.CPU.B = self._SLA_reg(self.CPU.B)
        self.CPU.M = 2

    def SLAr_c(self):
        self.CPU.C = self._SLA_reg(self.CPU.C)
        self.CPU.M = 2

    def SLAr_d(self):
        self.CPU.D = self._SLA_reg(self.CPU.D)
        self.CPU.M = 2

    def SLAr_e(self):
        self.CPU.E = self._SLA_reg(self.CPU.E)
        self.CPU.M = 2

    def SLAr_h(self):
        self.CPU.H = self._SLA_reg(self.CPU.H)
        self.CPU.M = 2

    def SLAr_l(self):
        self.CPU.L = self._SLA_reg(self.CPU.L)
        self.CPU.M = 2

    def SLAr_a(self):
        self.CPU.A = self._SLA_reg(self.CPU.A)
        self.CPU.M = 2

    def SLAHL(self):
        addr = (self.CPU.H <<8) + self.CPU.L
        i = self.MMU.rb(addr)

        c = 0x10 if (i & 0x80) else 0   #carry flag
        i = (i<<1) & 0xFF               #Left shift

        self.MMU.wb(addr,i)
        self.CPU.F = (0x80 if i==0 else 0) | c
        self.CPU.M = 4
    # ----------------------------
    # SLL (Shift Left Logical, with bit 0 forced to 1)
    # ----------------------------
    def _SLL_reg(self,reg):
        co = 0x10 if reg & 0x80 else 0       # carry = old bit 7
        reg = ((reg << 1) & 0xFF) | 1        # shift left and force bit 0 to 1
        self.CPU.F = 0 if reg else 0x80           # zero flag
        self.CPU.F = (self.CPU.F & 0xEF) | co          # combine carry
        return reg

    def SLLr_b(self):
        self.CPU.B = self._SLL_reg(self.CPU.B)
        self.CPU.M = 2

    def SLLr_c(self):
        self.CPU.C = self._SLL_reg(self.CPU.C)
        self.CPU.M = 2

    def SLLr_d(self):
        self.CPU.D = self._SLL_reg(self.CPU.D)
        self.CPU.M = 2

    def SLLr_e(self):
        self.CPU.E = self._SLL_reg(self.CPU.E)
        self.CPU.M = 2

    def SLLr_h(self):
        self.CPU.H = self._SLL_reg(self.CPU.H)
        self.CPU.M = 2

    def SLLr_l(self):
        self.CPU.L = self._SLL_reg(self.CPU.L)
        self.CPU.M = 2

    def SLLr_a(self):
        self.CPU.A = self._SLL_reg(self.CPU.A)
        self.CPU.M = 2

    # ----------------------------
    # SRA (Shift Right Arithmetic, preserves bit 7)
    # ----------------------------
    def _SRA_reg(self,reg):
        msb = reg & 0x80                     # preserve bit 7
        co = 0x10 if reg & 1 else 0          # carry = old bit 0
        reg = ((reg >> 1) | msb) & 0xFF      # shift right, restore MSB
        self.CPU.F = 0 if reg else 0x80           # zero flag
        self.CPU.F = (self.CPU.F & 0xEF) | co          # combine carry
        return reg

    def SRAr_b(self):
        self.CPU.B = self._SRA_reg(self.CPU.B)
        self.CPU.M = 2

    def SRAr_c(self):
        self.CPU.C = self._SRA_reg(self.CPU.C)
        self.CPU.M = 2

    def SRAr_d(self):
        self.CPU.D = self._SRA_reg(self.CPU.D)
        self.CPU.M = 2

    def SRAr_e(self):
        self.CPU.E = self._SRA_reg(self.CPU.E)
        self.CPU.M = 2

    def SRAr_h(self):
        self.CPU.H = self._SRA_reg(self.CPU.H)
        self.CPU.M = 2

    def SRAr_l(self):
        self.CPU.L = self._SRA_reg(self.CPU.L)
        self.CPU.M = 2

    def SRAr_a(self):
        self.CPU.A = self._SRA_reg(self.CPU.A)
        self.CPU.M = 2

    def SRAHL(self):
        addr = (self.CPU.H <<8) + self.CPU.L
        i = self.MMU.rb(addr)
        
        c = 0x10 if (i&1) else 0        #carry
        i = ((i>>1)|(i&0x80)) & 0xFF    #R shift
        
        self.MMU.wb(addr,i)
        self.CPU.F = (0x80 if i==0 else 0) |c
        self.CPU.M = 4

    # ----------------------------
    # SRL (Shift Right Logical, bit 7 = 0)
    # ----------------------------
    def _SRL_reg(self,reg):
        co = 0x10 if reg & 1 else 0           # carry = old bit 0
        reg = (reg >> 1) & 0xFF               # shift right, MSB = 0
        self.CPU.F = 0 if reg else 0x80            # zero flag
        self.CPU.F = (self.CPU.F & 0xEF) | co           # combine carry
        return reg

    def SRLr_b(self):
        self.CPU.B = self._SRL_reg(self.CPU.B)
        self.CPU.M = 2

    def SRLr_c(self):
        self.CPU.C = self._SRL_reg(self.CPU.C)
        self.CPU.M = 2

    def SRLr_d(self):
        self.CPU.D = self._SRL_reg(self.CPU.D)
        self.CPU.M = 2

    def SRLr_e(self):
        self.CPU.E = self._SRL_reg(self.CPU.E)
        self.CPU.M = 2

    def SRLr_h(self):
        self.CPU.H = self._SRL_reg(self.CPU.H)
        self.CPU.M = 2

    def SRLr_l(self):
        self.CPU.L = self._SRL_reg(self.CPU.L)
        self.CPU.M = 2

    def SRLr_a(self):
        self.CPU.A = self._SRL_reg(self.CPU.A)
        self.CPU.M = 2

    def SRLHL(self):
        addr = (self.CPU.H <<8) +self.CPU.L
        i = self.MMU.rb(addr)

        c = 0x10 if (i&1) else 0
        i >>=1

        self.MMU.wb(addr,i)
        self.CPU.F = (0x80 if i==0 else 0) |c
        self.CPU.M=4
    # ----------------------------
    # CPL (Complement A)
    # ----------------------------
    def CPL(self):
        self.CPU.A ^= 0xFF                       # bitwise NOT
        #self.CPU.F = 0 if self.CPU.A else 0x80        # zero flag [Is wrong]
        self.CPU.F = (self.CPU.F & 0x90) | 0x60
        #0x90 is Z,C; 0x60 is N,H
        
        self.CPU.M = 1

    # ----------------------------
    # NEG (Two's complement)
    # ----------------------------
    def NEG(self):
        self.CPU.A = (-self.CPU.A) & 0xFF             # two's complement
        self.CPU.F = 0x10 if self.CPU.A else 0x80     # set carry if result negative? original code sets half-carry? simplified
        self.CPU.M = 2

    # ----------------------------
    # CCF (Complement Carry Flag)
    # ----------------------------
    def CCF(self):
        '''ci = 0 if self.CPU.F & 0x10 else 0x10     # flip carry
        self.CPU.F = (self.CPU.F & 0xEF) | ci'''
        #above does not clear H,N
        flag = self.CPU.F & 0x80
        if not( self.CPU.F & 0x10):
            flag|=0x10
        self.CPU.F = flag
        
        self.CPU.M = 1

    # ----------------------------
    # SCF (Set Carry Flag)
    # ----------------------------
    def SCF(self):
        #self.CPU.F |= 0x10      #sets C, but doesnt clear N,H
        self.CPU.F = (self.CPU.F & 0x80) | 0x10
        self.CPU.M = 1

    # ----------------------------
    # Stack operations
    # ----------------------------

    def PUSH(self,REG_HIGH, REG_LOW):
        '''self.CPU.SP -= 1
        self.MMU.wb(self.CPU.SP, REG_HIGH)
        self.CPU.SP -= 1
        self.MMU.wb(self.CPU.SP, REG_LOW)
        self.CPU.M = 3'''
        self.CPU.SP = (self.CPU.SP - 1) & 0xFFFF
        self.MMU.wb(self.CPU.SP, REG_HIGH)

        self.CPU.SP = (self.CPU.SP - 1) & 0xFFFF
        self.MMU.wb(self.CPU.SP, REG_LOW)

        self.CPU.M = 4

    def POP(self):
        '''LOW = self.MMU.rb(self.CPU.SP)
        self.CPU.SP += 1
        HIGH = self.MMU.rb(self.CPU.SP)
        self.CPU.SP += 1
        return HIGH, LOW'''
        LOW = self.MMU.rb(self.CPU.SP)
        self.CPU.SP = (self.CPU.SP + 1) & 0xFFFF

        HIGH = self.MMU.rb(self.CPU.SP)
        self.CPU.SP = (self.CPU.SP + 1) & 0xFFFF

        self.CPU.M = 3  #DEBUG CHECK THIS

        return HIGH, LOW
    # ----------------------------
    # PUSH variants
    # ----------------------------
    def PUSHBC(self):
        self.PUSH(self.CPU.B, self.CPU.C)

    def PUSHDE(self):
        self.PUSH(self.CPU.D, self.CPU.E)

    def PUSHHL(self):
        self.PUSH(self.CPU.H, self.CPU.L)

    def PUSHAF(self):
        self.PUSH(self.CPU.A, self.CPU.F)

    # ----------------------------
    # POP variants
    # ----------------------------
    def POPBC(self):
        self.CPU.B, self.CPU.C = self.POP()

    def POPDE(self):
        self.CPU.D, self.CPU.E = self.POP()

    def POPHL(self):
        self.CPU.H, self.CPU.L = self.POP()

    def POPAF(self):

        self.CPU.A, f = self.POP()

        self.CPU.F = f & 0xF0



    # ----------------------------
    # Jump operations
    # ----------------------------

    def JPnn(self):
        self.CPU.PC = self.MMU.rw(self.CPU.PC)
        self.CPU.M = 4      #DEBUG: change from 3 to 4 cycles

    def JPHL(self):
        self.CPU.PC = (self.CPU.H << 8) + self.CPU.L
        self.CPU.M = 1

    def JPNZnn(self):
        self.CPU.M = 3
        if (self.CPU.F & 0x80) == 0x00:
            self.CPU.PC = self.MMU.rw(self.CPU.PC)
            self.CPU.M += 1
        else:
            self.CPU.PC += 2

    def JPZnn(self):
        self.CPU.M = 3
        if (self.CPU.F & 0x80) == 0x80:
            self.CPU.PC = self.MMU.rw(self.CPU.PC)
            self.CPU.M += 1
        else:
            self.CPU.PC += 2

    def JPNCnn(self):
        self.CPU.M = 3
        if (self.CPU.F & 0x10) == 0x00:
            self.CPU.PC = self.MMU.rw(self.CPU.PC)
            self.CPU.M += 1
        else:
            self.CPU.PC += 2

    def JPCnn(self):
        self.CPU.M = 3
        if (self.CPU.F & 0x10) == 0x10:
            self.CPU.PC = self.MMU.rw(self.CPU.PC)
            self.CPU.M += 1
        else:
            self.CPU.PC += 2

    # ----------------------------
    # Relative jumps
    # ----------------------------

    def JRn(self):
        offset = self.MMU.rb(self.CPU.PC)
        if offset > 127:
            offset = -((~offset + 1) & 0xFF)  # signed conversion
        self.CPU.PC += 1
        self.CPU.M = 2
        self.CPU.PC += offset
        self.CPU.M += 1

    def JRNZn(self):
        offset = self.MMU.rb(self.CPU.PC)
        if offset > 127:
            offset = -((~offset + 1) & 0xFF)
        self.CPU.PC += 1
        self.CPU.M = 2
        if (self.CPU.F & 0x80) == 0x00:
            self.CPU.PC += offset
            self.CPU.M += 1

    def JRZn(self):
        offset = self.MMU.rb(self.CPU.PC)
        if offset > 127:
            offset = -((~offset + 1) & 0xFF)
        self.CPU.PC += 1
        self.CPU.M = 2
        if (self.CPU.F & 0x80) == 0x80:
            self.CPU.PC += offset
            self.CPU.M += 1

    def JRNCn(self):
        offset = self.MMU.rb(self.CPU.PC)
        if offset > 127:
            offset = -((~offset + 1) & 0xFF)
        self.CPU.PC += 1
        self.CPU.M = 2
        if (self.CPU.F & 0x10) == 0x00:
            self.CPU.PC += offset
            self.CPU.M += 1

    def JRCn(self):
        offset = self.MMU.rb(self.CPU.PC)
        if offset > 127:
            offset = -((~offset + 1) & 0xFF)
        self.CPU.PC += 1
        self.CPU.M = 2
        if (self.CPU.F & 0x10) == 0x10:
            self.CPU.PC += offset
            self.CPU.M += 1

    # ----------------------------
    # Decrement & Jump
    # ----------------------------

    #This Function probably shouldnt exist. On GB, 0x10 is STOP
    def DJNZn(self):
        offset = self.MMU.rb(self.CPU.PC)
        if offset > 127:
            offset = -((~offset + 1) & 0xFF)  # signed conversion
        self.CPU.PC += 1
        self.CPU.M = 2
        self.CPU.B -= 1
        if self.CPU.B != 0:
            self.CPU.PC += offset
            self.CPU.M += 1

    # ----------------------------
    # Call instructions
    # ----------------------------

    def CALLnn(self):
        '''self.CPU.SP -= 2
        self.MMU.ww(self.CPU.SP, self.CPU.PC + 2)
        self.CPU.PC = self.MMU.rw(self.CPU.PC)          ##SOMETHINGS UP HERE
        self.CPU.M = 5'''

        '''self.CPU.SP -= 2
        self.MMU.ww(self.CPU.SP, self.CPU.PC + 3)
        self.CPU.PC = self.MMU.rw(self.CPU.PC + 1)      #still wrong?
        self.CPU.M = 5'''
    
        target = self.MMU.rw(self.CPU.PC)

        self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF
        self.MMU.ww(self.CPU.SP, (self.CPU.PC + 2) & 0xFFFF)

        self.CPU.PC = target
        self.CPU.M = 6


    #DEBUG: returned non-taken path to +2 from incorrect +3
    def CALLNZnn(self):

        self.CPU.M = 3
        
        if (self.CPU.F & 0x80) == 0x00:
            self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF
            self.MMU.ww(self.CPU.SP, (self.CPU.PC + 2) & 0xFFFF)
            self.CPU.PC = self.MMU.rw(self.CPU.PC)
            self.CPU.M += 3

        else:
            self.CPU.PC += 2



    def CALLZnn(self):

        self.CPU.M = 3

        if (self.CPU.F & 0x80) == 0x80:
            self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF
            self.MMU.ww(self.CPU.SP, (self.CPU.PC + 2) & 0xFFFF)
            self.CPU.PC = self.MMU.rw(self.CPU.PC)
            self.CPU.M += 3

        else:
            self.CPU.PC += 2



    def CALLNCnn(self):

        self.CPU.M = 3
        
        if (self.CPU.F & 0x10) == 0x00:
            self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF
            self.MMU.ww(self.CPU.SP, (self.CPU.PC + 2) & 0xFFFF)
            self.CPU.PC = self.MMU.rw(self.CPU.PC)
            self.CPU.M += 3

        else:
            self.CPU.PC += 2



    def CALLCnn(self):

        self.CPU.M = 3

        if (self.CPU.F & 0x10) == 0x10:
            self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF
            self.MMU.ww(self.CPU.SP, (self.CPU.PC + 2) & 0xFFFF)
            self.CPU.PC = self.MMU.rw(self.CPU.PC)
            self.CPU.M += 3

        else:
            self.CPU.PC += 2



    # ----------------------------

    # Return instructions

    # ----------------------------



    def RET(self):
        
        self.CPU.PC = self.MMU.rw(self.CPU.SP)
        self.CPU.SP = (self.CPU.SP + 2) & 0xFFFF
        self.CPU.M = 4



    def RETI(self):

        self.CPU.T = 1        # renamed from IME
        self.CPU.rSave()        # call the rrs function
        self.CPU.PC = self.MMU.rw(self.CPU.SP)
        self.CPU.SP = (self.CPU.SP + 2) & 0xFFFF
        self.CPU.M = 4          #debug: 3 to 4


    #DEBUG: changed from 1;3 to 2;5
    def RETNZ(self):

        self.CPU.M = 2

        if (self.CPU.F & 0x80) == 0x00:
            self.CPU.PC = self.MMU.rw(self.CPU.SP)
            self.CPU.SP = (self.CPU.SP + 2) & 0xFFFF
            self.CPU.M += 3



    def RETZ(self):

        self.CPU.M = 2

        if (self.CPU.F & 0x80) == 0x80:
            self.CPU.PC = self.MMU.rw(self.CPU.SP)
            self.CPU.SP = (self.CPU.SP + 2) & 0xFFFF
            self.CPU.M += 3



    def RETNC(self):

        self.CPU.M = 2

        if (self.CPU.F & 0x10) == 0x00:
            self.CPU.PC = self.MMU.rw(self.CPU.SP)
            self.CPU.SP = (self.CPU.SP + 2) & 0xFFFF
            self.CPU.M += 3



    def RETC(self):

        self.CPU.M = 2

        if (self.CPU.F & 0x10) == 0x10:
            self.CPU.PC = self.MMU.rw(self.CPU.SP)
            self.CPU.SP = (self.CPU.SP + 2) & 0xFFFF
            self.CPU.M += 3


    #DEBUG - timings. change 3 M cycles to 4
    def RST00(self):

        self.CPU.rSave()

        self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF

        self.MMU.ww(self.CPU.SP, self.CPU.PC)

        self.CPU.PC = 0x00

        self.CPU.M = 4



    def RST08(self):

        self.CPU.rSave()

        self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF

        self.MMU.ww(self.CPU.SP, self.CPU.PC)

        self.CPU.PC = 0x08

        self.CPU.M = 4



    def RST10(self):

        self.CPU.rSave()

        self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF

        self.MMU.ww(self.CPU.SP, self.CPU.PC)

        self.CPU.PC = 0x10

        self.CPU.M = 4



    def RST18(self):

        self.CPU.rSave()

        self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF

        self.MMU.ww(self.CPU.SP, self.CPU.PC)

        self.CPU.PC = 0x18

        self.CPU.M = 4



    def RST20(self):

        self.CPU.rSave()

        self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF

        self.MMU.ww(self.CPU.SP, self.CPU.PC)

        self.CPU.PC = 0x20

        self.CPU.M = 4



    def RST28(self):

        self.CPU.rSave()

        self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF

        self.MMU.ww(self.CPU.SP, self.CPU.PC)

        self.CPU.PC = 0x28

        self.CPU.M = 4



    def RST30(self):

        self.CPU.rSave()

        self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF

        self.MMU.ww(self.CPU.SP, self.CPU.PC)

        self.CPU.PC = 0x30

        self.CPU.M = 4



    def RST38(self):

        self.CPU.rSave()

        self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF

        self.MMU.ww(self.CPU.SP, self.CPU.PC)

        self.CPU.PC = 0x38

        self.CPU.M = 4


    #DEBUG: 5 M-cycles, not 3 nor 4
    def RST40(self):

        self.CPU.rSave()

        self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF

        self.MMU.ww(self.CPU.SP, self.CPU.PC)

        self.CPU.PC = 0x40

        self.CPU.M = 5



    def RST48(self):

        self.CPU.rSave()

        self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF

        self.MMU.ww(self.CPU.SP, self.CPU.PC)

        self.CPU.PC = 0x48

        self.CPU.M = 5



    def RST50(self):

        self.CPU.rSave()

        self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF

        self.MMU.ww(self.CPU.SP, self.CPU.PC)

        self.CPU.PC = 0x50

        self.CPU.M = 5



    def RST58(self):

        self.CPU.rSave()

        self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF

        self.MMU.ww(self.CPU.SP, self.CPU.PC)

        self.CPU.PC = 0x58

        self.CPU.M = 5



    def RST60(self):

        self.CPU.rSave()

        self.CPU.SP = (self.CPU.SP - 2) & 0xFFFF

        self.MMU.ww(self.CPU.SP, self.CPU.PC)

        self.CPU.PC = 0x60

        self.CPU.M = 5



    def NOP(self):
        self.CPU.M = 1

    def HALT(self):
        self.CPU._halt = 1
        self.CPU.M = 1

    def DI(self):
        self.CPU.T = 0 
        self.CPU.M = 1

    def EI(self):
        self.CPU.T = 1
        self.CPU.M = 1

    
    #Now, the ones I somehow missed
    def LDmmSP(self):
        addr = self.MMU.rb(self.CPU.PC) | (self.MMU.rb(self.CPU.PC + 1) << 8)
        self.CPU.PC = (self.CPU.PC + 2) & 0xFFFF
        self.MMU.wb(addr, self.CPU.SP & 0xFF)          # low byte
        self.MMU.wb(addr + 1, (self.CPU.SP >> 8) & 0xFF)  # high byte
        self.CPU.M = 5

    def MAPcb(self):
        #self.CPU.debug.append(self.CPU.C)
        i = self.MMU.rb(self.CPU.PC)
        self.CPU.PC += 1
        self.CPU.PC &= 0xFFFF

        if self.CPU._cbmap[i] is not None:
            self.CPU._cbmap[i]()
        else:
            print(i)


    def XX(self):
        # Undefined map entry
        opc = self.CPU.PC - 1
        print('Z80', 'Unimplemented instruction at $' + format(opc, 'x') + ', stopping.')
        self._stop = 1



##So, Now to actually create the CPU

CPU = CPU()

CPU._map = [
  # 00
  CPU._ops.NOP,		CPU._ops.LDBCnn,	CPU._ops.LDBCmA,	CPU._ops.INCBC,
  CPU._ops.INCr_b,	CPU._ops.DECr_b,	CPU._ops.LDrn_b,	CPU._ops.RLCA,
  CPU._ops.LDmmSP,	CPU._ops.ADDHLBC,	CPU._ops.LDABCm,	CPU._ops.DECBC,
  CPU._ops.INCr_c,	CPU._ops.DECr_c,	CPU._ops.LDrn_c,	CPU._ops.RRCA,
  # 10
  CPU._ops.DJNZn,	CPU._ops.LDDEnn,	CPU._ops.LDDEmA,	CPU._ops.INCDE,
  CPU._ops.INCr_d,	CPU._ops.DECr_d,	CPU._ops.LDrn_d,	CPU._ops.RLA,
  CPU._ops.JRn,		CPU._ops.ADDHLDE,	CPU._ops.LDADEm,	CPU._ops.DECDE,
  CPU._ops.INCr_e,	CPU._ops.DECr_e,	CPU._ops.LDrn_e,	CPU._ops.RRA,
  # 20
  CPU._ops.JRNZn,	CPU._ops.LDHLnn,	CPU._ops.LDHLIA,	CPU._ops.INCHL,
  CPU._ops.INCr_h,	CPU._ops.DECr_h,	CPU._ops.LDrn_h,	CPU._ops.DAA,
  CPU._ops.JRZn,	CPU._ops.ADDHLHL,	CPU._ops.LDAHLI,	CPU._ops.DECHL,
  CPU._ops.INCr_l,	CPU._ops.DECr_l,	CPU._ops.LDrn_l,	CPU._ops.CPL,
  # 30
  CPU._ops.JRNCn,	CPU._ops.LDSPnn,	CPU._ops.LDHLDA,	CPU._ops.INCSP,
  CPU._ops.INCHLm,	CPU._ops.DECHLm,	CPU._ops.LDHLmn,	CPU._ops.SCF,
  CPU._ops.JRCn,	CPU._ops.ADDHLSP,	CPU._ops.LDAHLD,	CPU._ops.DECSP,
  CPU._ops.INCr_a,	CPU._ops.DECr_a,	CPU._ops.LDrn_a,	CPU._ops.CCF,
  # 40
  CPU._ops.LDrr_bb,	CPU._ops.LDrr_bc,	CPU._ops.LDrr_bd,	CPU._ops.LDrr_be,
  CPU._ops.LDrr_bh,	CPU._ops.LDrr_bl,	CPU._ops.LDrHLm_b,	CPU._ops.LDrr_ba,
  CPU._ops.LDrr_cb,	CPU._ops.LDrr_cc,	CPU._ops.LDrr_cd,	CPU._ops.LDrr_ce,
  CPU._ops.LDrr_ch,	CPU._ops.LDrr_cl,	CPU._ops.LDrHLm_c,	CPU._ops.LDrr_ca,
  # 50
  CPU._ops.LDrr_db,	CPU._ops.LDrr_dc,	CPU._ops.LDrr_dd,	CPU._ops.LDrr_de,
  CPU._ops.LDrr_dh,	CPU._ops.LDrr_dl,	CPU._ops.LDrHLm_d,	CPU._ops.LDrr_da,
  CPU._ops.LDrr_eb,	CPU._ops.LDrr_ec,	CPU._ops.LDrr_ed,	CPU._ops.LDrr_ee,
  CPU._ops.LDrr_eh,	CPU._ops.LDrr_el,	CPU._ops.LDrHLm_e,	CPU._ops.LDrr_ea,
  # 60
  CPU._ops.LDrr_hb,	CPU._ops.LDrr_hc,	CPU._ops.LDrr_hd,	CPU._ops.LDrr_he,
  CPU._ops.LDrr_hh,	CPU._ops.LDrr_hl,	CPU._ops.LDrHLm_h,	CPU._ops.LDrr_ha,
  CPU._ops.LDrr_lb,	CPU._ops.LDrr_lc,	CPU._ops.LDrr_ld,	CPU._ops.LDrr_le,
  CPU._ops.LDrr_lh,	CPU._ops.LDrr_ll,	CPU._ops.LDrHLm_l,	CPU._ops.LDrr_la,
  # 70
  CPU._ops.LDHLmr_b,	CPU._ops.LDHLmr_c,	CPU._ops.LDHLmr_d,	CPU._ops.LDHLmr_e,
  CPU._ops.LDHLmr_h,	CPU._ops.LDHLmr_l,	CPU._ops.HALT,		CPU._ops.LDHLmr_a,
  CPU._ops.LDrr_ab,	CPU._ops.LDrr_ac,	CPU._ops.LDrr_ad,	CPU._ops.LDrr_ae,
  CPU._ops.LDrr_ah,	CPU._ops.LDrr_al,	CPU._ops.LDrHLm_a,	CPU._ops.LDrr_aa,
  # 80
  CPU._ops.ADDr_b,	CPU._ops.ADDr_c,	CPU._ops.ADDr_d,	CPU._ops.ADDr_e,
  CPU._ops.ADDr_h,	CPU._ops.ADDr_l,	CPU._ops.ADDHL,		CPU._ops.ADDr_a,
  CPU._ops.ADCr_b,	CPU._ops.ADCr_c,	CPU._ops.ADCr_d,	CPU._ops.ADCr_e,
  CPU._ops.ADCr_h,	CPU._ops.ADCr_l,	CPU._ops.ADCHL,		CPU._ops.ADCr_a,
  # 90
  CPU._ops.SUBr_b,	CPU._ops.SUBr_c,	CPU._ops.SUBr_d,	CPU._ops.SUBr_e,
  CPU._ops.SUBr_h,	CPU._ops.SUBr_l,	CPU._ops.SUBHL,		CPU._ops.SUBr_a,
  CPU._ops.SBCr_b,	CPU._ops.SBCr_c,	CPU._ops.SBCr_d,	CPU._ops.SBCr_e,
  CPU._ops.SBCr_h,	CPU._ops.SBCr_l,	CPU._ops.SBCHL,		CPU._ops.SBCr_a,
  # A0
  CPU._ops.ANDr_b,	CPU._ops.ANDr_c,	CPU._ops.ANDr_d,	CPU._ops.ANDr_e,
  CPU._ops.ANDr_h,	CPU._ops.ANDr_l,	CPU._ops.ANDHL,		CPU._ops.ANDr_a,
  CPU._ops.XORr_b,	CPU._ops.XORr_c,	CPU._ops.XORr_d,	CPU._ops.XORr_e,
  CPU._ops.XORr_h,	CPU._ops.XORr_l,	CPU._ops.XORHL,		CPU._ops.XORr_a,
  # B0
  CPU._ops.ORr_b,	CPU._ops.ORr_c,		CPU._ops.ORr_d,		CPU._ops.ORr_e,
  CPU._ops.ORr_h,	CPU._ops.ORr_l,		CPU._ops.ORHL,		CPU._ops.ORr_a,
  CPU._ops.CPr_b,	CPU._ops.CPr_c,		CPU._ops.CPr_d,		CPU._ops.CPr_e,
  CPU._ops.CPr_h,	CPU._ops.CPr_l,		CPU._ops.CPHL,		CPU._ops.CPr_a,
  # C0
  CPU._ops.RETNZ,	CPU._ops.POPBC,		CPU._ops.JPNZnn,	CPU._ops.JPnn,
  CPU._ops.CALLNZnn,	CPU._ops.PUSHBC,	CPU._ops.ADDn,		CPU._ops.RST00,
  CPU._ops.RETZ,	CPU._ops.RET,		CPU._ops.JPZnn,		CPU._ops.MAPcb,
  CPU._ops.CALLZnn,	CPU._ops.CALLnn,	CPU._ops.ADCn,		CPU._ops.RST08,
  # D0
  CPU._ops.RETNC,	CPU._ops.POPDE,		CPU._ops.JPNCnn,	CPU._ops.XX,
  CPU._ops.CALLNCnn,	CPU._ops.PUSHDE,	CPU._ops.SUBn,		CPU._ops.RST10,
  CPU._ops.RETC,	CPU._ops.RETI,		CPU._ops.JPCnn,		CPU._ops.XX,
  CPU._ops.CALLCnn,	CPU._ops.XX,		CPU._ops.SBCn,		CPU._ops.RST18,
  # E0
  CPU._ops.LDIOnA,	CPU._ops.POPHL,		CPU._ops.LDIOCA,	CPU._ops.XX,
  CPU._ops.XX,		CPU._ops.PUSHHL,	CPU._ops.ANDn,		CPU._ops.RST20,
  CPU._ops.ADDSPn,	CPU._ops.JPHL,		CPU._ops.LDmmA,		CPU._ops.XX,
  CPU._ops.XX,		CPU._ops.XX,		CPU._ops.XORn,		CPU._ops.RST28,
  # F0
  CPU._ops.LDAIOn,	CPU._ops.POPAF,		CPU._ops.LDAIOC,	CPU._ops.DI,
  CPU._ops.XX,		CPU._ops.PUSHAF,	CPU._ops.ORn,		CPU._ops.RST30,
  CPU._ops.LDHLSPn,	CPU._ops.LDSPHL,    	CPU._ops.LDAmm,		CPU._ops.EI,
  CPU._ops.XX,		CPU._ops.XX,		CPU._ops.CPn,		CPU._ops.RST38
];

CPU._cbmap = [
  # CB00
  CPU._ops.RLCr_b,	CPU._ops.RLCr_c,	CPU._ops.RLCr_d,	CPU._ops.RLCr_e,
  CPU._ops.RLCr_h,	CPU._ops.RLCr_l,	CPU._ops.RLCHL,		CPU._ops.RLCr_a,
  CPU._ops.RRCr_b,	CPU._ops.RRCr_c,	CPU._ops.RRCr_d,	CPU._ops.RRCr_e,
  CPU._ops.RRCr_h,	CPU._ops.RRCr_l,	CPU._ops.RRCHL,		CPU._ops.RRCr_a,
  # CB10
  CPU._ops.RLr_b,	CPU._ops.RLr_c,		CPU._ops.RLr_d,		CPU._ops.RLr_e,
  CPU._ops.RLr_h,	CPU._ops.RLr_l,		CPU._ops.RLHL,		CPU._ops.RLr_a,
  CPU._ops.RRr_b,	CPU._ops.RRr_c,		CPU._ops.RRr_d,		CPU._ops.RRr_e,
  CPU._ops.RRr_h,	CPU._ops.RRr_l,		CPU._ops.RRHL,		CPU._ops.RRr_a,
  # CB20
  CPU._ops.SLAr_b,	CPU._ops.SLAr_c,	CPU._ops.SLAr_d,	CPU._ops.SLAr_e,
  CPU._ops.SLAr_h,	CPU._ops.SLAr_l,	CPU._ops.SLAHL,		CPU._ops.SLAr_a,
  CPU._ops.SRAr_b,	CPU._ops.SRAr_c,	CPU._ops.SRAr_d,	CPU._ops.SRAr_e,
  CPU._ops.SRAr_h,	CPU._ops.SRAr_l,	CPU._ops.SRAHL,		CPU._ops.SRAr_a,
  # CB30
  CPU._ops.SWAPr_b,	CPU._ops.SWAPr_c,	CPU._ops.SWAPr_d,	CPU._ops.SWAPr_e,
  CPU._ops.SWAPr_h,	CPU._ops.SWAPr_l,	CPU._ops.SWAPHL,	CPU._ops.SWAPr_a,
  CPU._ops.SRLr_b,	CPU._ops.SRLr_c,	CPU._ops.SRLr_d,	CPU._ops.SRLr_e,
  CPU._ops.SRLr_h,	CPU._ops.SRLr_l,	CPU._ops.SRLHL,		CPU._ops.SRLr_a,
  # CB40
  CPU._ops.BIT0b,	CPU._ops.BIT0c,		CPU._ops.BIT0d,		CPU._ops.BIT0e,
  CPU._ops.BIT0h,	CPU._ops.BIT0l,		CPU._ops.BIT0m,		CPU._ops.BIT0a,
  CPU._ops.BIT1b,	CPU._ops.BIT1c,		CPU._ops.BIT1d,		CPU._ops.BIT1e,
  CPU._ops.BIT1h,	CPU._ops.BIT1l,		CPU._ops.BIT1m,		CPU._ops.BIT1a,
  # CB50
  CPU._ops.BIT2b,	CPU._ops.BIT2c,		CPU._ops.BIT2d,		CPU._ops.BIT2e,
  CPU._ops.BIT2h,	CPU._ops.BIT2l,		CPU._ops.BIT2m,		CPU._ops.BIT2a,
  CPU._ops.BIT3b,	CPU._ops.BIT3c,		CPU._ops.BIT3d,		CPU._ops.BIT3e,
  CPU._ops.BIT3h,	CPU._ops.BIT3l,		CPU._ops.BIT3m,		CPU._ops.BIT3a,
  # CB60
  CPU._ops.BIT4b,	CPU._ops.BIT4c,		CPU._ops.BIT4d,		CPU._ops.BIT4e,
  CPU._ops.BIT4h,	CPU._ops.BIT4l,		CPU._ops.BIT4m,		CPU._ops.BIT4a,
  CPU._ops.BIT5b,	CPU._ops.BIT5c,		CPU._ops.BIT5d,		CPU._ops.BIT5e,
  CPU._ops.BIT5h,	CPU._ops.BIT5l,		CPU._ops.BIT5m,		CPU._ops.BIT5a,
  # CB70
  CPU._ops.BIT6b,	CPU._ops.BIT6c,		CPU._ops.BIT6d,		CPU._ops.BIT6e,
  CPU._ops.BIT6h,	CPU._ops.BIT6l,		CPU._ops.BIT6m,		CPU._ops.BIT6a,
  CPU._ops.BIT7b,	CPU._ops.BIT7c,		CPU._ops.BIT7d,		CPU._ops.BIT7e,
  CPU._ops.BIT7h,	CPU._ops.BIT7l,		CPU._ops.BIT7m,		CPU._ops.BIT7a,
  # CB80
  CPU._ops.RES0b,	CPU._ops.RES0c,		CPU._ops.RES0d,		CPU._ops.RES0e,
  CPU._ops.RES0h,	CPU._ops.RES0l,		CPU._ops.RES0m,		CPU._ops.RES0a,
  CPU._ops.RES1b,	CPU._ops.RES1c,		CPU._ops.RES1d,		CPU._ops.RES1e,
  CPU._ops.RES1h,	CPU._ops.RES1l,		CPU._ops.RES1m,		CPU._ops.RES1a,
  # CB90
  CPU._ops.RES2b,	CPU._ops.RES2c,		CPU._ops.RES2d,		CPU._ops.RES2e,
  CPU._ops.RES2h,	CPU._ops.RES2l,		CPU._ops.RES2m,		CPU._ops.RES2a,
  CPU._ops.RES3b,	CPU._ops.RES3c,		CPU._ops.RES3d,		CPU._ops.RES3e,
  CPU._ops.RES3h,	CPU._ops.RES3l,		CPU._ops.RES3m,		CPU._ops.RES3a,
  # CBA0
  CPU._ops.RES4b,	CPU._ops.RES4c,		CPU._ops.RES4d,		CPU._ops.RES4e,
  CPU._ops.RES4h,	CPU._ops.RES4l,		CPU._ops.RES4m,		CPU._ops.RES4a,
  CPU._ops.RES5b,	CPU._ops.RES5c,		CPU._ops.RES5d,		CPU._ops.RES5e,
  CPU._ops.RES5h,	CPU._ops.RES5l,		CPU._ops.RES5m,		CPU._ops.RES5a,
  # CBB0
  CPU._ops.RES6b,	CPU._ops.RES6c,		CPU._ops.RES6d,		CPU._ops.RES6e,
  CPU._ops.RES6h,	CPU._ops.RES6l,		CPU._ops.RES6m,		CPU._ops.RES6a,
  CPU._ops.RES7b,	CPU._ops.RES7c,		CPU._ops.RES7d,		CPU._ops.RES7e,
  CPU._ops.RES7h,	CPU._ops.RES7l,		CPU._ops.RES7m,		CPU._ops.RES7a,
  # CBC0
  CPU._ops.SET0b,	CPU._ops.SET0c,		CPU._ops.SET0d,		CPU._ops.SET0e,
  CPU._ops.SET0h,	CPU._ops.SET0l,		CPU._ops.SET0m,		CPU._ops.SET0a,
  CPU._ops.SET1b,	CPU._ops.SET1c,		CPU._ops.SET1d,		CPU._ops.SET1e,
  CPU._ops.SET1h,	CPU._ops.SET1l,		CPU._ops.SET1m,		CPU._ops.SET1a,
  # CBD0
  CPU._ops.SET2b,	CPU._ops.SET2c,		CPU._ops.SET2d,		CPU._ops.SET2e,
  CPU._ops.SET2h,	CPU._ops.SET2l,		CPU._ops.SET2m,		CPU._ops.SET2a,
  CPU._ops.SET3b,	CPU._ops.SET3c,		CPU._ops.SET3d,		CPU._ops.SET3e,
  CPU._ops.SET3h,	CPU._ops.SET3l,		CPU._ops.SET3m,		CPU._ops.SET3a,
  # CBE0
  CPU._ops.SET4b,	CPU._ops.SET4c,		CPU._ops.SET4d,		CPU._ops.SET4e,
  CPU._ops.SET4h,	CPU._ops.SET4l,		CPU._ops.SET4m,		CPU._ops.SET4a,
  CPU._ops.SET5b,	CPU._ops.SET5c,		CPU._ops.SET5d,		CPU._ops.SET5e,
  CPU._ops.SET5h,	CPU._ops.SET5l,		CPU._ops.SET5m,		CPU._ops.SET5a,
  # CBF0
  CPU._ops.SET6b,	CPU._ops.SET6c,		CPU._ops.SET6d,		CPU._ops.SET6e,
  CPU._ops.SET6h,	CPU._ops.SET6l,		CPU._ops.SET6m,		CPU._ops.SET6a,
  CPU._ops.SET7b,	CPU._ops.SET7c,		CPU._ops.SET7d,		CPU._ops.SET7e,
  CPU._ops.SET7h,	CPU._ops.SET7l,		CPU._ops.SET7m,		CPU._ops.SET7a,
];

#yay?

    
