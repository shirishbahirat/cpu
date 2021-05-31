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
def pc_adder(reset, clk, pc, pc_next):

    @always(clk.posedge)
    def padder():
        if reset.next == INACTIVE_HIGH:
            pc_next.next = (pc.next + 1)

    return padder


@block
def pc_mux(reset, pc, pc_next, jmp_addr, pc_sel):

    @always_comb
    def pmux():
        if reset.next == INACTIVE_HIGH:
            if pc_sel:
                pc.next = jmp_addr
            else:
                pc.next = pc_next

    return pmux


@block
def pc_assign(reset, read_addr, pc):

    @always_comb
    def assign():
        if reset.next == INACTIVE_HIGH:
            read_addr.next = pc

    return assign


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
def inst_mem(reset, read_addr, instruction):

    inx = open('mc_code').read().splitlines()
    inst_ram = [signal(intbv(int(inx[i], 2))[CPU_BITS:]) for i in range(128)]

    @always_comb
    def itcm():
        if reset.next == INACTIVE_HIGH:
            instruction.next = inst_ram[read_addr]

    return itcm


@block
def ifid_pipl(reset, ifid_reg, instruction, pc):

    @always_comb
    def if_id():
        if reset.next == INACTIVE_HIGH:
            ifid_reg.next[(CPU_BITS + CPU_BITS):CPU_BITS] = pc
            ifid_reg.next[CPU_BITS:] = instruction

    return if_id


@block
def decode(reset, ifid_reg, ra, rb, wa, opcode):

    @always_comb
    def dcode():

        if reset.next == INACTIVE_HIGH:

            if ifid_reg[7:0] == RTYPE:
                ra.next = ifid_reg[20:15]
                rb.next = ifid_reg[25:20]
                opcode.next = ifid_reg[7:0]
                wa.next = ifid_reg[12:7]

            elif ifid_reg[7:0] == ITYPE:
                ra.next = ifid_reg[20:15]
                opcode.next = ifid_reg[7:0]
                wa.next = ifid_reg[12:7]

            elif ifid_reg[7:0] == STYPE:
                ra.next = ifid_reg[20:15]
                rb.next = ifid_reg[25:20]
                opcode.next = ifid_reg[7:0]
                wa.next = ifid_reg[25:20]

            elif ifid_reg[7:0] == SBTYPE:
                ra.next = ifid_reg[20:15]
                rb.next = ifid_reg[25:20]
                opcode.next = ifid_reg[7:0]

    return dcode


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
            if reg_wr:
                if wa:
                    registers[wa].next = wda

    return read, write


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
def imm_gen(reset, ifid_reg, im_gen, padz, padx):

    @always_comb
    def immgen():
        if reset.next == INACTIVE_HIGH:

            if ifid_reg[7:0] == ITYPE:
                im_gen.next[12:] = ifid_reg[32:20]

            elif ifid_reg[7:0] == STYPE:
                im_gen.next[12:5] = ifid_reg[32:25]
                im_gen.next[5:] = ifid_reg[12:7]

            elif ifid_reg[7:0] == SBTYPE:
                im_gen.next[12] = ifid_reg[31]
                im_gen.next[11:5] = ifid_reg[31:25]
                im_gen.next[11] = ifid_reg[7]
                im_gen.next[5:1] = ifid_reg[12:8]
                im_gen.next[0] = 0

            if ifid_reg[31] == 0:
                im_gen.next[32:(31 - 20)] = padz
            else:
                im_gen.next[32:(31 - 20)] = padx

    return immgen


@block
def idex_pipl(reset, idex_reg, instruction, ra, rb, wa, im_gen, rda, rdb, alu_op, brnch, mem_rd, mem_to_rgs, mem_wr, alu_src, reg_wr):

    @always_comb
    def id_ex():
        if reset.next == INACTIVE_HIGH:
            idex_reg.next[CPU_BITS:] = instruction.next
            idex_reg.next[CPU_BITS + REG_WIDTH:CPU_BITS] = ra.next

            idex_reg.next[(2 * REG_WIDTH) + CPU_BITS:REG_WIDTH + CPU_BITS] = rb.next
            idex_reg.next[(3 * REG_WIDTH) + CPU_BITS: (2 * REG_WIDTH) + CPU_BITS] = wa.next

            idex_reg.next[(3 * REG_WIDTH) + (2 * CPU_BITS):(3 * REG_WIDTH) + CPU_BITS] = im_gen.next

            idex_reg.next[(3 * REG_WIDTH) + (3 * CPU_BITS):(3 * REG_WIDTH) + (2 * CPU_BITS)] = rda.next
            idex_reg.next[(3 * REG_WIDTH) + (4 * CPU_BITS):(3 * REG_WIDTH) + (3 * CPU_BITS)] = rdb.next
            idex_reg.next[(3 * REG_WIDTH) + (4 * CPU_BITS) + CPU_ALUW:(3 * REG_WIDTH) + (4 * CPU_BITS)] = alu_op.next

            idex_reg.next[1 + (3 * REG_WIDTH) + (4 * CPU_BITS) + CPU_ALUW:0 + (3 * REG_WIDTH) + (4 * CPU_BITS) + CPU_ALUW] = brnch.next
            idex_reg.next[2 + (3 * REG_WIDTH) + (4 * CPU_BITS) + CPU_ALUW:1 + (3 * REG_WIDTH) + (4 * CPU_BITS) + CPU_ALUW] = mem_rd.next
            idex_reg.next[3 + (3 * REG_WIDTH) + (4 * CPU_BITS) + CPU_ALUW:2 + (3 * REG_WIDTH) + (4 * CPU_BITS) + CPU_ALUW] = mem_to_rgs.next
            idex_reg.next[4 + (3 * REG_WIDTH) + (4 * CPU_BITS) + CPU_ALUW:3 + (3 * REG_WIDTH) + (4 * CPU_BITS) + CPU_ALUW] = mem_wr.next
            idex_reg.next[5 + (3 * REG_WIDTH) + (4 * CPU_BITS) + CPU_ALUW:4 + (3 * REG_WIDTH) + (4 * CPU_BITS) + CPU_ALUW] = alu_src.next
            idex_reg.next[6 + (3 * REG_WIDTH) + (4 * CPU_BITS) + CPU_ALUW:5 + (3 * REG_WIDTH) + (4 * CPU_BITS) + CPU_ALUW] = reg_wr.next

    return id_ex


@block
def alu(reset, alu_decode, idex_reg, rdx, result):

    @always_comb
    def operation():
        if reset.next == INACTIVE_HIGH:
            if alu_decode == AND:
                result.next = idex_reg[(3 * REG_WIDTH) + (3 * CPU_BITS):(3 * REG_WIDTH) + (2 * CPU_BITS)] & rdx
            elif alu_decode == OR:
                result.next = idex_reg[(3 * REG_WIDTH) + (3 * CPU_BITS):(3 * REG_WIDTH) + (2 * CPU_BITS)] | rdx
            elif alu_decode == ADD:
                result.next = idex_reg[(3 * REG_WIDTH) + (3 * CPU_BITS):(3 * REG_WIDTH) + (2 * CPU_BITS)] + rdx
            elif alu_decode == SUB:
                result.next = idex_reg[(3 * REG_WIDTH) + (3 * CPU_BITS):(3 * REG_WIDTH) + (2 * CPU_BITS)] - rdx
            elif alu_decode == XOR:
                result.next = idex_reg[(3 * REG_WIDTH) + (3 * CPU_BITS):(3 * REG_WIDTH) + (2 * CPU_BITS)] ^ rdx
            elif alu_decode == SLL:
                result.next = idex_reg[(3 * REG_WIDTH) + (3 * CPU_BITS):(3 * REG_WIDTH) + (2 * CPU_BITS)] << rdx
            elif alu_decode == SRL:
                result.next = idex_reg[(3 * REG_WIDTH) + (3 * CPU_BITS):(3 * REG_WIDTH) + (2 * CPU_BITS)].signed() >> rdx
            elif alu_decode == SLT:
                result.next = True if (idex_reg[(3 * REG_WIDTH) + (3 * CPU_BITS):(3 * REG_WIDTH) + (2 * CPU_BITS)].signed() < rdx.signed()) else False
            elif alu_decode == SLTU:
                result.next = True if (idex_reg[(3 * REG_WIDTH) + (3 * CPU_BITS):(3 * REG_WIDTH) + (2 * CPU_BITS)] < rdx) else False
            elif alu_decode == SRA:
                if idex_reg[(3 * REG_WIDTH) + (3 * CPU_BITS):(3 * REG_WIDTH) + (2 * CPU_BITS)][31] == 0:
                    result.next = idex_reg[(3 * REG_WIDTH) + (3 * CPU_BITS):(3 * REG_WIDTH) + (2 * CPU_BITS)].signed() >> rdx
                elif idex_reg[(3 * REG_WIDTH) + (3 * CPU_BITS):(3 * REG_WIDTH) + (2 * CPU_BITS)][31] == 1:
                    result.next = idex_reg[(3 * REG_WIDTH) + (3 * CPU_BITS):(3 * REG_WIDTH) + (2 * CPU_BITS)].signed() >> rdx
                    result.next[32:(31 - rdx)] = (2**rdx) - 1

    return operation


@block
def alu_control(reset, idex_reg, alu_decode):

    @always_comb
    def alucont():
        if reset.next == INACTIVE_HIGH:
            if idex_reg[(3 * REG_WIDTH) + (4 * CPU_BITS) + CPU_ALUW:(3 * REG_WIDTH) + (4 * CPU_BITS)] == 2:
                if idex_reg[32:25] == 0:
                    if idex_reg[15:12] == 0:
                        alu_decode.next = ADD
                    elif idex_reg[15:12] == 1:
                        alu_decode.next = SLL
                    elif idex_reg[15:12] == 2:
                        alu_decode.next = SLT
                    elif idex_reg[15:12] == 3:
                        alu_decode.next = SLTU
                    elif idex_reg[15:12] == 4:
                        alu_decode.next = XOR
                    elif idex_reg[15:12] == 5:
                        alu_decode.next = SRL
                    elif idex_reg[15:12] == 6:
                        alu_decode.next = OR
                    elif idex_reg[15:12] == 7:
                        alu_decode.next = AND
                elif idex_reg[32:25] == 32:
                    if idex_reg[15:12] == 0:
                        alu_decode.next = SUB
                    elif idex_reg[15:12] == 5:
                        alu_decode.next = SRA
            elif idex_reg[(3 * REG_WIDTH) + (4 * CPU_BITS) + CPU_ALUW:(3 * REG_WIDTH) + (4 * CPU_BITS)] == 0:
                alu_decode.next = ADD
            elif idex_reg[(3 * REG_WIDTH) + (4 * CPU_BITS) + CPU_ALUW:(3 * REG_WIDTH) + (4 * CPU_BITS)] == 7:
                if idex_reg[15:12] == 0:
                    alu_decode.next = XOR

    return alucont


@block
def cpu_top(clk, reset):

    pc, pc_next, jmp_addr, read_addr, instruction = [signal(intbv(0)[CPU_BITS:]) for _ in range(5)]
    ra, rb, wa = [signal(intbv(0, min=0, max=(CPU_REGS - 1))) for _ in range(3)]
    wda, rda, rdb, rdx = [signal(intbv(0)[CPU_BITS:]) for _ in range(4)]
    brnch, mem_rd, mem_to_rgs, mem_wr, alu_src, reg_wr = [signal(intbv(0)[1:]) for _ in range(6)]
    ifid_reg = signal(intbv(0)[(CPU_BITS + CPU_BITS):])
    alu_decode = signal(intbv(0)[CPU_ALUW:])

    pc_sel = signal(intbv(0)[1:])
    opcode = signal(intbv(0)[7:])
    alu_op = signal(intbv(0)[CPU_ALUW:])
    im_gen = signal(intbv(0)[CPU_BITS:])
    padz, padx = [signal(intbv(0)[20:]), signal(intbv(XPAD)[20:])]
    result, read_data, pc, shl = [signal(intbv(0)[CPU_BITS:]) for _ in range(4)]

    id_ex_len = len(ra) + len(rb) + len(wa) + len(im_gen) + \
        len(rda) + len(rdb) + len(brnch) + len(mem_rd) + \
        len(mem_to_rgs) + len(alu_op) + len(mem_wr) + \
        len(alu_src) + len(reg_wr) + len(instruction)

    idex_reg = signal(intbv(0)[id_ex_len:])

    padr = pc_adder(reset, clk, pc, pc_next)
    padr.convert(hdl='Verilog')

    pcmx = pc_mux(reset, pc, pc_next, jmp_addr, pc_sel)
    pcmx.convert(hdl='Verilog')

    pcmx = pc_mux(reset, pc, pc_next, jmp_addr, pc_sel)
    pcmx.convert(hdl='Verilog')

    nxpc = pc_assign(reset, read_addr, pc)
    nxpc.convert(hdl='Verilog')

    imem = inst_mem(reset, read_addr, instruction)
    imem.convert(hdl='Verilog')

    ifid = ifid_pipl(reset, ifid_reg, instruction, pc)
    ifid.convert(hdl='Verilog')

    dcde = decode(reset, ifid_reg, ra, rb, wa, opcode)
    dcde.convert(hdl='Verilog')

    regf = reg_file(reset, clk, ra, rb, wa, wda, reg_wr, rda, rdb)
    regf.convert(hdl='Verilog')

    cont = control(reset, opcode, brnch, mem_rd, mem_to_rgs, alu_op, mem_wr, alu_src, reg_wr)
    cont.convert(hdl='Verilog')

    imgn = imm_gen(reset, ifid_reg, im_gen, padz, padx)
    imgn.convert(hdl='Verilog')

    # tken = taken(result, brnch, pc_sel)
    # tken.convert(hdl='Verilog')

    idex = idex_pipl(reset, idex_reg, instruction, ra, rb, wa, im_gen, rda, rdb, alu_op, brnch, mem_rd, mem_to_rgs, mem_wr, alu_src, reg_wr)
    idex.convert(hdl='Verilog')

    aluc = alu_control(reset, idex_reg, alu_decode)
    aluc.convert(hdl='Verilog')

    alux = alu(reset, alu_decode, idex_reg, rdx, result)
    alux.convert(hdl='Verilog')

    '''
    to do
    fix taken seems like stalling
    include control output mux
    reg write control needs to be from forwared and not from contol out
    alu rdx needs be from alu_mux
    '''

    return instances()


@ block
def top():

    clk = signal(intbv(0)[1:])
    reset = rsig(0, active=0, isasync=True)

    cl = clock(clk)

    cpu = cpu_top(clk, reset)

    @ instance
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
