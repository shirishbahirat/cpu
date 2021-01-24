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
def pc_adder(reset, clk, pc, pc_addr):

    @always(clk.posedge)
    def padder():
        if reset.next == INACTIVE_HIGH:
            pc_addr.next = (pc.next + 1)

    return padder


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
def pc_assign(reset, read_addr, pc):

    @always_comb
    def assign():
        if reset.next == INACTIVE_HIGH:
            read_addr.next = pc

    return assign


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
def cpu_top(clk, reset):
    pc, pc_addr, jmp_addr, read_addr, instruction = [signal(intbv(0)[CPU_BITS:]) for _ in range(5)]
    pc_sel = signal(intbv(0)[1:])

    padr = pc_adder(reset, clk, pc, pc_addr)
    padr.convert(hdl='Verilog')

    pcmx = pc_mux(reset, pc, pc_addr, jmp_addr, pc_sel)
    pcmx.convert(hdl='Verilog')

    pcmx = pc_mux(reset, pc, pc_addr, jmp_addr, pc_sel)
    pcmx.convert(hdl='Verilog')

    nxpc = pc_assign(reset, read_addr, pc)
    nxpc.convert(hdl='Verilog')

    imem = inst_mem(reset, read_addr, instruction)
    imem.convert(hdl='Verilog')

    return instances()


@block
def top():

    clk = signal(intbv(0)[1:])
    reset = rsig(0, active=0, isasync=True)

    cl = clock(clk)
    cl.convert(hdl='Verilog')

    cpu = cpu_top(clk, reset)
    cpu.convert(hdl='Verilog')

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
