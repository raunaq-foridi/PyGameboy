from cpu import CPU
from mmu import MMU
from key import KEY
from timer import TIMER
from gpu import DummyGPU
import gpu
from gpu import GPU

# Initialize components
cpu = CPU
mmu = MMU()
#gpu = DummyGPU()
gpu = GPU()
key = KEY()
timer = TIMER()

# Link components if needed
cpu._ops.CPU = cpu
cpu.MMU = mmu
cpu._ops.MMU = mmu
cpu.GPU = gpu
cpu.KEY = key
cpu.TIMER = timer

mmu.CPU = cpu
mmu.GPU = gpu
mmu.KEY = key
mmu.TIMER = timer

timer.CPU = cpu
timer.MMU = mmu

gpu.CPU = cpu
gpu.MMU = mmu
gpu.TIMER = timer
gpu.KEY = key
# Reset everything
cpu.reset()
mmu.reset()
key.reset()
timer.reset()
gpu.reset()  # dummy GPU will just log writes

#test
gpu.wb(0xFF40, 0x91)

# Load a ROM
mmu.load("Tetris.gb")
#mmu.load("pkmn_red.gb")
#mmu.load("cpu_instrs.gb")
#mmu.load("instr_timing.gb")
#mmu.load("mem_timing.gb")
#mmu.load("halt_bug.gb")


#Functions
def frame():

    fclock = CPU._clock + 17556
    #brk = document.getElementById('breakpoint').value  # Keep as string, parse later
    #t0 = datetime.datetime.now()

    while CPU._clock < fclock:
        if CPU._halt:
            CPU.M = 1
            CPU._clock += CPU.M
            #if any interupt becomes nonzero, wake the CPU up from HALT
            if mmu._ie & mmu._if:
                CPU._halt = 0
        else:
            # Execute instruction at PC (proper fetch/increment/execute order).
            # exec() already adds its own M-cost to CPU._clock internally.
            CPU.exec()

        # Handle interrupts
        if CPU.T and (mmu._ie & mmu._if):
            CPU._halt = 0
            CPU.T = 0
            ifired = mmu._ie & mmu._if

            if ifired & 1:
                mmu._if &= 0xFE
                CPU._ops.RST40()
                CPU._clock += CPU.M
                
            elif ifired & 2:
                mmu._if &= 0xFD
                CPU._ops.RST48()
                CPU._clock += CPU.M

            elif ifired & 4:
                mmu._if &= 0xFB
                CPU._ops.RST50()
                CPU._clock += CPU.M

            elif ifired & 8:
                mmu._if &= 0xF7
                CPU._ops.RST58()
                CPU._clock += CPU.M

            elif ifired & 16:
                mmu._if &= 0xEF
                CPU._ops.RST60()
                CPU._clock += CPU.M

            else:
                CPU.T = 1

        # Update GPU and timers
        gpu.checkline()
        timer.inc()

        # Breakpoint or stop
        if CPU._stop:
            break 

    #t1 = datetime.datetime.now()
    #elapsed_ms = (t1 - t0).total_seconds() * 1000
    #fps = round(10000 / elapsed_ms, 1)




# Main loop
running = True
CPU.PC=0x100
print("Reading memory address: ",CPU.PC)
print("Which should be instruction: ", hex(mmu.rb(CPU.PC)))
import pygame
while running:
   
    
    #input("Press enter to simulate a single frame x 1000: ")
    #for i in range(0,1000):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            key.keydown(event.key)
        elif event.type == pygame.KEYUP:
            key.keyup(event.key)
    frame()             
    '''CPU._map[mmu.rb(CPU.PC)]()
    CPU.PC = (CPU.PC + 1) & 0xFFFF
    CPU._clock += CPU.M'''

    '''CPU.exec()
        
    gpu.checkline()
    #pygame.event.pump()
    timer.inc()'''
    #print("Reading memory address: ", hex(mmu._debug))
    #print("Which should be instruction: ", hex(mmu.rb(mmu._debug)))
   

pygame.quit()

