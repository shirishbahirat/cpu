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
def pc_mux(pc, pc_addr, jmp_addr, pc_sel):

    @always_comb
    def pmux():
        if pc_sel:
            pc.next = jmp_addr
        else:
            pc.next = pc_addr

    return pmux


@block
def wda_mux(wda, mem_to_rgs, result, read_data):

    @always_comb
    def wmux():
        if mem_to_rgs:
            wda.next = read_data
        else:
            wda.next = result

    return wmux


@block
def alu_mux(im_gen, rdb, rdx, alu_src):

    @always_comb
    def amux():
        if alu_src:
            rdx.next = im_gen
        else:
            rdx.next = rdb

    return amux


@block
def reg_file(clk, ra, rb, wa, wda, reg_wr, rda, rdb):

    registers = [signal(intbv(10 + i)[CPU_BITS:]) for i in range(32)]

    @always_comb
    def read():
        if ra:
            rda.next = registers[ra]

        if rb:
            rdb.next = registers[rb]

    @always(clk.posedge)
    def write():
        if reg_wr and (wa > 0):
            registers[wa].next = wda

    return read, write


@block
def alu(alu_op, rda, rdx, result):

    @always_comb
    def operation():

        if alu_op == AND:
            result.next = rda & rdx
        elif alu_op == OR:
            result.next = rda | rdx
        elif alu_op == ADD:
            result.next = rda + rdx
        elif alu_op == SUB:
            result.next = rda - rdx

    return operation


@block
def alu_control(instruction, alu_op, oprtin):

    @always_comb
    def alucont():

        if (alu_op[0] == 0) and (alu_op[1] == 0):
            oprtin.next = int('0010', 2)
        elif (alu_op[0] == 1):
            oprtin.next = int('0110', 2)
        elif (alu_op[1] == 1) and (instruction[31:25] == 0) and (instruction[14:12] == 0):
            oprtin.next = int('0010', 2)
        elif (alu_op[1] == 1) and (instruction[31:25] == int('0100000', 2)) and (instruction[14:12] == 0):
            oprtin.next = int('0110', 2)
        elif (alu_op[1] == 1) and (instruction[31:25] == 0) and (instruction[14:12] == int('111', 2)):
            oprtin.next = int('0000', 2)
        elif (alu_op[1] == 1) and (instruction[31:25] == 0) and (instruction[14:12] == int('110', 2)):
            oprtin.next = int('0001', 2)

    return alucont


@block
def imm_gen(instruction, im_gen):

    @always_comb
    def immgen():
        im_gen.next = instruction

    return immgen


@block
def control(opcode, brnch, mem_rd, mem_to_rgs, alu_op, mem_wr, alu_src, reg_wr):

    @always_comb
    def cont():
        if opcode == RTYPE:
            alu_src.next = False
            mem_to_rgs.next = False
            reg_wr.next = True
            mem_rd.next = False
            mem_wr.next = False
            brnch.next = False
            alu_op.next = 2

        elif opcode == 2:
            alu_src.next = True
            mem_to_rgs.next = True
            reg_wr.next = True
            mem_rd.next = True
            mem_wr.next = False
            brnch.next = False
            alu_op.next = 0

        elif opcode == 35:
            alu_src.next = True
            mem_to_rgs.next = False
            reg_wr.next = False
            mem_rd.next = False
            mem_wr.next = True
            brnch.next = False
            alu_op.next = 0

        elif opcode == 99:
            alu_src.next = False
            mem_to_rgs.next = False
            reg_wr.next = False
            mem_rd.next = False
            mem_wr.next = False
            brnch.next = True
            alu_op.next = 1

    return cont


@block
def data_mem(clk, result, mem_wr, mem_rd, rdb, read_data):

    ind = open('mc_data').read().splitlines()
    data_ram = [signal(intbv(int(ind[i], 2))[CPU_BITS:]) for i in range(128)]

    @always(clk.posedge)
    def dtcm():
        if mem_wr:
            data_ram[result].next = rdb
        elif mem_rd:
            read_data.next = data_ram[result]

    return dtcm


@block
def inst_mem(read_addr, instruction, ra, rb, wa, opcode):

    inx = open('mc_code').read().splitlines()
    inst_ram = [signal(intbv(int(inx[i], 2))[CPU_BITS:]) for i in range(128)]

    @always_comb
    def itcm():
        instruction.next = inst_ram[read_addr]

        if inst_ram[read_addr][6:0] == RTYPE:
            ra.next = inst_ram[read_addr][19:15]
            rb.next = inst_ram[read_addr][24:20]
            opcode.next = inst_ram[read_addr][6:0]
            wa.next = inst_ram[read_addr][11:7]

    return itcm


@block
def pc_adder(pc, read_addr):

    @always_comb
    def padder():
        read_addr.next = pc + 1

    return padder


@block
def jmp_adder(pc, shl, jmp_addr):

    @always_comb
    def jadder():
        jmp_addr.next = pc + shl

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
    oprtin = signal(intbv(0)[4:])

    step = signal(intbv(0)[1:])

    read_addr, instruction, pc_addr, jmp_addr = [signal(intbv(0)[CPU_BITS:]) for _ in range(4)]

    cont = control(opcode, brnch, mem_rd, mem_to_rgs, alu_op, mem_wr, alu_src, reg_wr)
    dmem = data_mem(clk, result, mem_wr, mem_rd, rdb, read_data)
    imem = inst_mem(read_addr, instruction, ra, rb, wa, opcode)
    alux = alu(alu_op, rda, rdx, result)
    regf = reg_file(clk, ra, rb, wa, wda, reg_wr, rda, rdb)
    padr = pc_adder(pc, read_addr)
    jadr = jmp_adder(pc, shl, read_addr)
    pcmx = pc_mux(pc, pc_addr, jmp_addr, pc_sel)
    almx = alu_mux(im_gen, rdb, rdx, alu_src)
    wdmx = wda_mux(wda, mem_to_rgs, result, read_data)
    aluc = alu_control(instruction, alu_op, oprtin)
    imgn = imm_gen(instruction, im_gen)

    @always(step.posedge)
    def cpu():
        if pc == 0:
            pc.next += 1

    @instance
    def event():

        while True:
            for i in range(2):
                yield clk.posedge
            if reset.next == INACTIVE_HIGH:
                step.next = not step

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
    tb.run_sim(200)


if __name__ == '__main__':
    main()
