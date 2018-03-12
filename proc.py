#
# demo processor
#
# jan@uwinloc.com
#
#

from myhdl import *

import conf


def mem(dinp, wrad, dout, rdad, CLK100MHZ, mem_size=256):                        # {{{
    """
    memory accesses
    """

    return write, read
# }}}
def rom(dout, rdad, CLK100MHZ, prog=()):                              # {{{
    """
    ROM accesses
    """

    return read
# }}}

def proc(LED, SW, CLK100MHZ, prog=()):                                        # {{{
    """
    shallow stack processor
    """
    # definitions                                                       {{{
    mem = [Signal(modbv(0)[conf.reg_bits:]) for i in range(conf.mem_size)]

    A = Signal(modbv(0, -conf.reg_size, +conf.reg_size))
    B = Signal(modbv(0, -conf.reg_size, +conf.reg_size))
    C = Signal(modbv(0, -conf.reg_size, +conf.reg_size))
    I = Signal(modbv(0, -conf.reg_size, +conf.reg_size))

    ma   = Signal(modbv(0, -conf.reg_size, +conf.reg_size))
    md   = Signal(modbv(0, -conf.reg_size, +conf.reg_size))
    wr   = Signal(bool(0))
    rd   = Signal(bool(0))
    ext  = Signal(bool(0))
    skip = Signal(intbv(0)[3:])

    # instructions
    inst = Signal(intbv(0)[conf.rom_bits:])
    cnst = intbv(0)[1:]
    oper = intbv(0)[4:]

    # control signals
    asel = intbv(0)[3:]
    amux = intbv(0)[2:]
    imux = intbv(0)[1:]
    stck = intbv(0)[2:]

    # intermediate signals
    dinp = Signal(modbv(0, -conf.reg_size, +conf.reg_size))
    alu  = modbv(0, -conf.reg_size, +conf.reg_size)
    jmp  = modbv(0, -conf.reg_size, +conf.reg_size)

    # simulator signals
    halt = False
    # }}}
    # memory access                                                 # {{{
    @always(CLK100MHZ.posedge)
    def mem_wr():
        if wr:
            if ma == -1: LED.next = md
            else:        mem[int(ma)].next = md

    @always_comb
    def mem_rd():
        if A == -1: dinp.next = SW
        else:       dinp.next = mem[A]

    @always_comb
    def rom_rd():
        inst.next = prog[int(I)]
    # }}}
    # processor                                                     # {{{
    @always(CLK100MHZ.posedge)                                          
    def logic():
        # reset control signals                                 # {{{
        ext.next = False
        rd.next  = 0
        wr.next  = 0
        jmp[:]   = I + 1
        halt = False
        # }}}
        # decode                                                # {{{
        cnst[:] = inst[5:4]     # top bit 1 = constant, else instruction
        oper[:] = inst[4:0]     # constant or instruction
        # }}}
        if skip > 0:                                                # {{{ 
            skip.next = skip - 1
            I.next = I + 1
        # }}}
        elif cnst:
            # read constant in A                                    # {{{
            ext.next = True
            if ext: 
                A.next = (A << 4) | oper
            else:
                A.next = oper.signed()
                B.next = A
                C.next = B
                stck[:] = 1     # push
        # }}}
        else:
            # execute instruction                                   # {{{
            if   oper ==  0: A.next = ~A;                                # NOT
            elif oper ==  1: A.next = -A;                                # NEG
            elif oper ==  2: A.next =  A << 1                            # SHL
            elif oper ==  3: A.next =  A >> 1                            # SHR
            elif oper ==  4: A.next =  B;     B.next = C                 # DROP
            elif oper ==  5:                  B.next = A; C.next = B     # DUP
            elif oper ==  6: A.next =  C;     B.next = A; C.next = B     # OVER
            elif oper ==  7: A.next =  A ^ B; B.next = C                 # XOR
            elif oper ==  8: A.next =  A & B; B.next = C                 # AND
            elif oper ==  9: A.next =  A + B; B.next = C                 # ADD
            elif oper == 10: A.next =  dinp[:];           rd.next = 1    # READ
            elif oper == 11:                                             # WRITE
                ma.next = A 
                md.next = B 
                wr.next = 1    
                A.next = C     
                B.next = C 
            elif oper == 12: jmp[:] =  A;     A.next = I + 1             # CALL
            elif oper == 13: jmp[:] =  I + A; A.next = B; B.next = C     # JUMP
            elif oper == 14:                                             # SKIP
                if B == 0: skip.next = A[3:]
                A.next = C 
                B.next = C 
            elif oper == 15:                                             # HALT   
                if __debug__: halt = True
        # }}}
        # handle jumps                                          {{{    
        I.next = jmp
        # }}}
        # debug output                                          {{{
        if __debug__:
            mnem = ["NOT", "NEG", "SHL", "SHR", "DROP", "DUP", "OVER", "XOR", "AND", "ADD", "RMEM", "WMEM", "CALL", "JUMP", "SKIP", "HALT"]
            if skip: sstr = "S%1d" % skip
            else:    sstr = "  "
            if cnst: ostr = "0x%01X " % oper
            else:    ostr = mnem[oper]   
            if   oper==11: wstr = "write 0x%03X -> 0x%03X" % (int(B), int(A))
            elif oper==10: wstr = "read  0x%03X -> x0%03X" % (int(A), int(mem[int(A)]))
            else:          wstr = "                      "
            print("%s   I:%04X i:%02X %-5s  A:%03X B:%03X C:%03X    %s" % (
                sstr, int(I), int(inst), ostr, int(A)&0xFFF, int(B)&0xFFF, int(C)&0xFFF, wstr)) 
            if jmp[:] != I+1: print "-"*50
            if halt: raise StopSimulation()
        # }}}
    # }}}

    return mem_wr, mem_rd, rom_rd, logic
# }}}
def bench (prog = ()):                                                    # {{{
    """ Exercise timegen """

    # clock and reset
    CLK100MHZ   = Signal(bool(0))
    reset = Signal(bool(1)) 

    # I/O
    oport = Signal(intbv(0)[12:])
    iport = Signal(intbv(0)[12:])

    # clock generator
    @always(delay(1))
    def clockgen():
        CLK100MHZ.next = not CLK100MHZ

    # reset generator
    @always(delay(5))
    def resetgen():
        reset.next = 0

    procinst = proc(oport, iport, CLK100MHZ, tuple(prog))

    # test
    @instance
    def stimulus(): 
        while True:
            yield CLK100MHZ.negedge
            pass

    return clockgen, resetgen, procinst, stimulus
# }}}
def test_bench(prog=None):                                              # {{{
    # program
    #       #0x4  #0x2  DUP   #0x5  #0x3  ADD   HALT
    if not prog: prog = (0x14, 0x12, 0x05, 0x15, 0x13, 0x09, 0x0F)
    else:        prog = tuple(prog)

    tb = traceSignals(bench, prog)
    sim = Simulation(tb)
    sim.run(5000)
# }}}
def make_vhdl(prog=None):                                               # {{{
    # clock and reset
    CLK100MHZ = Signal(bool(0))

    # I/O
    LED = Signal(intbv(0)[12:])
    SW  = Signal(intbv(0)[12:])

    # program
    if not prog: prog = (0x14, 0x12, 0x0B, 0x00, 0x00, 0x00)
    else:        prog = tuple(prog)

    procvhdl = toVHDL(proc, LED, SW, CLK100MHZ, prog)
# }}}

if __name__ == "__main__":
    import sys
    import json
    with open(sys.argv[1]) as f:
        (labels,prog) = json.load(f)
        make_vhdl(prog)
        test_bench(prog)

