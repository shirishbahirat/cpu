from myhdl import block, always_comb, instance, intbv, delay, always, instances
from myhdl import Signal as signal
from myhdl import ResetSignal as rsig
from myhdl import StopSimulation as expectation
from defs import *
from random import randrange


@block
def clock(clk):

    @always(delay(10))
    def clck():
        clk.next = not clk

    return clck


@block
def pc_mux(reset, pc, pc_addr, jmp_addr, pc_sel):

    @always_comb
    def pmux():
        if reset.next == INACTIVE_HIGH:
            if pc_sel:
                pc.next = jmp_addr
            else:
                pc.next = pc_addr

    return pmux


@block
def wda_mux(reset, wda, mem_to_rgs, result, read_data):

    @always_comb
    def wmux():
        if reset.next == INACTIVE_HIGH:
            if mem_to_rgs:
                wda.next = read_data
            else:
                wda.next = result

    return wmux


@block
def alu_mux(reset, im_gen, rdb, rdx, alu_src):

    @always_comb
    def amux():
        if reset.next == INACTIVE_HIGH:
            if alu_src:
                rdx.next = im_gen
            else:
                rdx.next = rdb

    return amux


@block
def taken(result, brnch, pc_sel):

    @always_comb
    def take():

        if (result == 0) & (brnch):
            pc_sel.next = True
        else:
            pc_sel.next = False

    return take


@block
def reg_file(reset, clk, ra, rb, wa, wda, reg_wr, rda, rdb):

    registers = [signal(intbv(10 + i)[CPU_BITS:]) for i in range(32)]

    @always_comb
    def read():
        if reset.next == INACTIVE_HIGH:
            if ra:
                rda.next = registers[ra]

            if rb:
                rdb.next = registers[rb]

    @always(clk.posedge)
    def write():
        if reset.next == INACTIVE_HIGH:
            if reg_wr and (wa > 0):
                registers[wa].next = wda

    return read, write


@block
def alu(reset, alu_decode, rda, rdx, result):

    @always_comb
    def operation():
        if reset.next == INACTIVE_HIGH:
            if alu_decode == AND:
                result.next = rda & rdx
            elif alu_decode == OR:
                result.next = rda | rdx
            elif alu_decode == ADD:
                result.next = rda + rdx
            elif alu_decode == SUB:
                result.next = rda - rdx
            elif alu_decode == XOR:
                result.next = rda ^ rdx
            elif alu_decode == SLL:
                result.next = rda << rdx
            elif alu_decode == SRL:
                result.next = rda.signed() >> rdx
            elif alu_decode == SLT:
                result.next = True if (rda.signed() < rdx.signed()) else False
            elif alu_decode == SLTU:
                result.next = True if (rda.unsigned() < rdx.unsigned()) else False
            elif alu_decode == SRA:
                if rda[31] == 0:
                    result.next = rda.signed() >> rdx
                elif rda[31] == 1:
                    temp = (2**rdx) - 1
                    pad = signal(intbv(temp)[rdx:])
                    result.next = rda.signed() >> rdx
                    result.next[32:(31 - rdx)] = pad

    return operation


@block
def alu_control(reset, instruction, alu_op, alu_decode):

    @always_comb
    def alucont():
        if reset.next == INACTIVE_HIGH:
            if alu_op == 2:
                if instruction[32:25] == 0:
                    if instruction[15:12] == 0:
                        alu_decode.next = ADD
                    elif instruction[15:12] == 1:
                        alu_decode.next = SLL
                    elif instruction[15:12] == 2:
                        alu_decode.next = SLT
                    elif instruction[15:12] == 3:
                        alu_decode.next = SLTU
                    elif instruction[15:12] == 4:
                        alu_decode.next = XOR
                    elif instruction[15:12] == 5:
                        alu_decode.next = SRL
                    elif instruction[15:12] == 6:
                        alu_decode.next = OR
                    elif instruction[15:12] == 7:
                        alu_decode.next = AND
                elif instruction[32:25] == 32:
                    if instruction[15:12] == 0:
                        alu_decode.next = SUB
                    elif instruction[15:12] == 5:
                        alu_decode.next = SRA
            elif alu_op == 0:
                alu_decode.next = ADD
            elif alu_op == 7:
                if instruction[15:12] == 0:
                    alu_decode.next = XOR

    return alucont


@block
def imm_gen(reset, instruction, im_gen):

    @always_comb
    def immgen():
        if reset.next == INACTIVE_HIGH:

            if instruction[7:0] == ITYPE:
                im_gen.next[12:] = instruction[32:20]

            elif instruction[7:0] == STYPE:
                im_gen.next[12:5] = instruction[32:25]
                im_gen.next[5:] = instruction[12:7]

            elif instruction[7:0] == SBTYPE:
                im_gen.next[12] = instruction[31]
                im_gen.next[11:5] = instruction[31:25]
                im_gen.next[11] = instruction[7]
                im_gen.next[5:1] = instruction[12:8]
                im_gen.next[0] = 0

            if instruction[31] == 0:
                pad = signal(intbv(0)[20:])
                im_gen.next[32:(31 - 20)] = pad

            else:
                temp = (2**20) - 1
                pad = signal(intbv(temp)[20:])
                im_gen.next[32:(31 - 20)] = pad

    return immgen


@block
def control(reset, opcode, brnch, mem_rd, mem_to_rgs, alu_op, mem_wr, alu_src, reg_wr):

    @always_comb
    def cont():
        if reset.next == INACTIVE_HIGH:
            if opcode == RTYPE:
                alu_src.next = False
                mem_to_rgs.next = False
                reg_wr.next = True
                mem_rd.next = False
                mem_wr.next = False
                brnch.next = False
                alu_op.next = 2

            elif opcode == ITYPE:
                alu_src.next = True
                mem_to_rgs.next = True
                reg_wr.next = True
                mem_rd.next = True
                mem_wr.next = False
                brnch.next = False
                alu_op.next = 0

            elif opcode == STYPE:
                alu_src.next = True
                mem_to_rgs.next = False
                reg_wr.next = False
                mem_rd.next = False
                mem_wr.next = True
                brnch.next = False
                alu_op.next = 0

            elif opcode == SBTYPE:
                alu_src.next = False
                mem_to_rgs.next = False
                reg_wr.next = False
                mem_rd.next = False
                mem_wr.next = False
                brnch.next = True
                alu_op.next = 7

    return cont


@block
def data_mem(reset, clk, result, mem_wr, mem_rd, rdb, read_data):

    ind = open('mc_data').read().splitlines()
    data_ram = [signal(intbv(int(ind[i], 2))[CPU_BITS:]) for i in range(128)]

    @always(clk.posedge)
    def dtcm():
        if reset.next == INACTIVE_HIGH:
            if mem_wr:
                data_ram[result].next = rdb
            elif mem_rd:
                read_data.next = data_ram[result]

    return dtcm


@block
def inst_mem(reset, read_addr, instruction, ra, rb, wa, opcode):

    inx = open('mc_code').read().splitlines()
    inst_ram = [signal(intbv(int(inx[i], 2))[CPU_BITS:]) for i in range(128)]

    @always_comb
    def itcm():
        if reset.next == INACTIVE_HIGH:
            instruction.next = inst_ram[read_addr]

            if inst_ram[read_addr][7:0] == RTYPE:
                ra.next = inst_ram[read_addr][20:15]
                rb.next = inst_ram[read_addr][25:20]
                opcode.next = inst_ram[read_addr][7:0]
                wa.next = inst_ram[read_addr][12:7]
            elif inst_ram[read_addr][7:0] == ITYPE:
                ra.next = inst_ram[read_addr][20:15]
                opcode.next = inst_ram[read_addr][7:0]
                wa.next = inst_ram[read_addr][12:7]
            elif inst_ram[read_addr][7:0] == STYPE:
                ra.next = inst_ram[read_addr][20:15]
                rb.next = inst_ram[read_addr][25:20]
                opcode.next = inst_ram[read_addr][7:0]
                wa.next = inst_ram[read_addr][25:20]
            elif inst_ram[read_addr][7:0] == SBTYPE:
                ra.next = inst_ram[read_addr][20:15]
                rb.next = inst_ram[read_addr][25:20]
                opcode.next = inst_ram[read_addr][7:0]

    return itcm


@block
def pc_adder(reset, step, pc, pc_addr):

    @always(step.posedge)
    def padder():
        if reset.next == INACTIVE_HIGH:
            pc_addr.next = (pc.next + 1)

    return padder


@block
def pc_assign(reset, read_addr, pc):

    @always_comb
    def assign():
        if reset.next == INACTIVE_HIGH:
            read_addr.next = pc

    return assign


@block
def jmp_adder(reset, read_addr, shl, jmp_addr):

    @always_comb
    def jadder():
        if reset.next == INACTIVE_HIGH:
            jmp_addr.next = read_addr + shl

    return jadder


@block
def cpu_top(clk, reset):

    ra, rb, wa = [signal(intbv(0, min=0, max=(CPU_REGS - 1))) for _ in range(3)]
    wda, rda, rdb, rdx = [signal(intbv(0)[CPU_BITS:]) for _ in range(4)]
    alu_op = signal(intbv(0)[CPU_ALUW:])
    brnch, mem_rd, mem_to_rgs, mem_wr, alu_src, reg_wr = [signal(intbv(0)[1:]) for _ in range(6)]
    opcode = signal(intbv(0)[7:])
    result, read_data, pc, shl = [signal(intbv(0)[CPU_BITS:]) for _ in range(4)]
    pc_sel = signal(intbv(0)[1:])
    im_gen = signal(intbv(0)[CPU_BITS:])
    alu_decode = signal(intbv(0)[4:])

    step = signal(intbv(0)[1:])

    read_addr, instruction, pc_addr, jmp_addr = [signal(intbv(0)[CPU_BITS:]) for _ in range(4)]

    cont = control(reset, opcode, brnch, mem_rd, mem_to_rgs, alu_op, mem_wr, alu_src, reg_wr)
    dmem = data_mem(reset, clk, result, mem_wr, mem_rd, rdb, read_data)
    imem = inst_mem(reset, read_addr, instruction, ra, rb, wa, opcode)
    alux = alu(reset, alu_decode, rda, rdx, result)
    regf = reg_file(reset, clk, ra, rb, wa, wda, reg_wr, rda, rdb)
    padr = pc_adder(reset, step, pc, pc_addr)
    jadr = jmp_adder(reset, read_addr, shl, jmp_addr)
    pcmx = pc_mux(reset, pc, pc_addr, jmp_addr, pc_sel)
    almx = alu_mux(reset, im_gen, rdb, rdx, alu_src)
    wdmx = wda_mux(reset, wda, mem_to_rgs, result, read_data)
    aluc = alu_control(reset, instruction, alu_op, alu_decode)
    imgn = imm_gen(reset, instruction, im_gen)
    nxpc = pc_assign(reset, read_addr, pc)
    tken = taken(result, brnch, pc_sel)

    cont.convert(hdl='Verilog')
    pcmx.convert(hdl='Verilog')
    almx.convert(hdl='Verilog')
    wdmx.convert(hdl='Verilog')
    nxpc.convert(hdl='Verilog')
    aluc.convert(hdl='Verilog')
    padr.convert(hdl='Verilog')
    jadr.convert(hdl='Verilog')
    tken.convert(hdl='Verilog')

    '''
    alux.convert(hdl='Verilog')
    imgn.convert(hdl='Verilog')
    regf.convert(hdl='Verilog')
    imem.convert(hdl='Verilog')
    dmem.convert(hdl='Verilog')
    '''

    @always(step.posedge)
    def cpu():
        if pc == 0:
            pc.next += 1

    @instance
    def event():
        idle = 7
        while True:
            for i in range(idle):
                yield clk.posedge
            if reset.next == INACTIVE_HIGH:
                step.next = not step
                idle = 3

    return instances()


@block
def top():

    clk = signal(intbv(0)[1:])
    reset = rsig(0, active=0, isasync=True)

    cl = clock(clk)
    cpu = cpu_top(clk, reset)

    @instance
    def stimulus():
        reset.next = ACTIVE_LOW
        yield clk.negedge
        reset.next = INACTIVE_HIGH

    return instances()

def main():

    tb = top()
    tb.config_sim(trace=True)
    tb.run_sim(1400)


if __name__ == '__main__':
    main()
