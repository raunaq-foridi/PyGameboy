class TIMER:
    def __init__(self):
        self._div = 0
        self._tma = 0
        self._tima = 0
        self._tac = 0

        self._clock = {"main": 0, "sub": 0, "div": 0}
        self._sdiv = 0  # Added because reset referenced it
        self._tima_pending = False
        print('TIMER', 'Initialized.')

    def reset(self):
        self._div = 0
        self._sdiv = 0
        self._tma = 0
        self._tima = 0
        self._tac = 0
        self._clock = {"main": 0, "sub": 0, "div": 0}
        self._tima_pending = False
        print('TIMER', 'Reset.')

    def step(self):
        self._tima += 1
        #self._clock["main"] = 0
        if self._tima > 255:
            #self._tima = self._tma     ##Overflows are delayed a cycle
            self._tima= 0
            self._tima_pending = True
            #self.MMU._if |= 4  # Timer interrupt

    def inc(self):

        #First, deal with pending overflow
        #TMA reloads/ interrupt reqs take an M cycle

        if self._tima_pending:
            self._tima = self._tma
            self.MMU._if |=4  #Timer interrupt
            self._tima_pending = False

        
        
        #self._clock["sub"] += self.CPU.M
        #DIV increments every 64 M-cycles.
        self._clock["div"] += self.CPU.M

        while self._clock["div"] >= 64:
            self._clock["div"] -= 64
            self._div = (self._div+1) & 0xFF
        ''' if self._clock["sub"] > 3:
            self._clock["main"] += 1
            self._clock["sub"] -= 4

            self._clock["div"] += 1
            if self._clock["div"] == 16:
                self._clock["div"] = 0
                self._div = (self._div + 1) & 0xFF'''
       
        
        if self._tac & 4:
            mode = self._tac & 3
            self._clock["main"] += self.CPU.M
            period = {0: 256, 1: 4, 2: 16, 3: 64}[mode]
            #refactor this loop later to use period
            #Off by factor of 4
            '''
            while ((mode == 0 and self._clock["main"] >= 64) or 
               (mode == 1 and self._clock["main"] >= 1) or 
               (mode == 2 and self._clock["main"] >= 4) or 
               (mode == 3 and self._clock["main"] >= 16)):
                self._clock["main"] -= period
                self.step()'''
            while ((mode == 0 and self._clock["main"] >= 256) or 
               (mode == 1 and self._clock["main"] >= 4) or 
               (mode == 2 and self._clock["main"] >= 16) or 
               (mode == 3 and self._clock["main"] >= 64)):
                self._clock["main"] -= period
                self.step()

    def rb(self, addr):
        if addr == 0xFF04:
            return self._div
        elif addr == 0xFF05:
            return self._tima
        elif addr == 0xFF06:
            return self._tma
        elif addr == 0xFF07:
            return self._tac

    def wb(self, addr, val):
        if addr == 0xFF04:
            self._div = 0
            self._clock["div"]=0
            self._clock["main"] = 0
        elif addr == 0xFF05:
            self._tima = val
        elif addr == 0xFF06:
            self._tma = val
        elif addr == 0xFF07:
            self._tac = val & 7
