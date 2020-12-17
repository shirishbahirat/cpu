import myhdl
from myhdl import Signal as signal
from myhdl import intbv
from defs import *


ind = open('mc_data').read().splitlines()
data_ram = [signal(intbv(int(ind[i], 2))[CPU_BITS:]) for i in range(128)]
inx = open('mc_code').read().splitlines()
inst_ram = [signal(intbv(int(inx[i], 2))[CPU_BITS:]) for i in range(128)]
registers = [signal(intbv(10 + i)[CPU_BITS:]) for i in range(32)]

result, rda, rdx = [signal(intbv(0)[CPU_BITS:]) for _ in range(3)]

for i in range(12):

    instruction = inst_ram[i]

    opcode = instruction[7:0]

    if opcode == RTYPE:
        alu_op = 2
    elif opcode == ITYPE:
        alu_op = 0
    elif opcode == STYPE:
        alu_op = 0
    elif opcode == JTYPE:
        alu_op = 7

    if alu_op == 2:
        if instruction[32:25] == 0:
            if instruction[15:12] == 0:
                alu_decode = ADD
            elif instruction[15:12] == 1:
                alu_decode = SLL
            elif instruction[15:12] == 2:
                alu_decode = SLT
            elif instruction[15:12] == 3:
                alu_decode = SLTU
            elif instruction[15:12] == 4:
                alu_decode = XOR
            elif instruction[15:12] == 5:
                alu_decode = SRL
            elif instruction[15:12] == 6:
                alu_decode = OR
            elif instruction[15:12] == 7:
                alu_decode = AND
        elif instruction[32:25] == 32:
            if instruction[15:12] == 0:
                alu_decode = SUB
            elif instruction[15:12] == 5:
                alu_decode = SRA
    elif alu_op == 0:
        alu_decode = ADD
    elif alu_op == 7:
        if instruction[15:12] == 0:
            alu_decode = XOR

    if opcode == RTYPE:
        rda = registers[instruction[20:15]]
        rdx = registers[instruction[25:20]]

    if alu_decode == AND:
        result = rda & rdx
    elif alu_decode == OR:
        result = rda | rdx
    elif alu_decode == ADD:
        result = rda + rdx
    elif alu_decode == SUB:
        result = rda - rdx
    elif alu_decode == XOR:
        result = rda ^ rdx
    elif alu_decode == SLL:
        result = rda << rdx
    elif alu_decode == SRL:
        result = rda.signed() >> rdx
    elif alu_decode == SLT:
        resultt = True if (rda.signed() < rdx.signed()) else False
    elif alu_decode == SLTU:
        result = True if (rda.unsigned() < rdx.unsigned()) else False
    elif alu_decode == SRA:
        if rda[31] == 0:
            result = rda.signed() >> rdx
        elif rda[31] == 1:
            temp = (2**rdx) - 1
            pad = signal(intbv(temp)[rdx:])
            result = rda.signed() >> rdx
            result[32:(31 - rdx)] = pad

    if opcode == RTYPE:
        registers[instruction[12:7]] = result

    '''
    imm = intbv(0)[13:]
    imm[12] = ins[31]
    imm[11:5] = ins[31:25]
    imm[11] = ins[7]
    imm[5:1] = ins[12:8]
    '''
    aluop = ''
    if alu_decode == AND:
        aluop = ' AND'
    elif alu_decode == OR:
        aluop = '  OR'
    elif alu_decode == ADD:
        aluop = ' ADD'
    elif alu_decode == SLL:
        aluop = ' SLL'
    elif alu_decode == SLT:
        aluop = ' SLT'
    elif alu_decode == SLTU:
        aluop = 'SLTU'
    elif alu_decode == SUB:
        aluop = ' SUB'
    elif alu_decode == XOR:
        aluop = ' XOR'
    elif alu_decode == SRL:
        aluop = ' SRL'
    elif alu_decode == SRA:
        aluop = ' SRA'

    if instruction[7:0] == RTYPE:
        print(format(i, '03'), format(int(instruction), '08x'), 'op', format(int(instruction[7:0]), '02x'),
              'rs1', format(int(instruction[20:15]), '02x'), 'rs2', format(int(instruction[25:20]), '02x'), 'rd',
              format(int(instruction[12:7]), '02x'), '\n',
              'alu-op', aluop, 'rs1-data', format(int(rda), '08x'), 'rs2-data', format(int(rdx), '08x'), 'rd-data', format(int(result), '08x'))

    #format(int(rda), '08x')

    '''
    print('rd', format(int(ins[12:7]), '05b'))
    print('func3', format(int(ins[15:12]), '03b'))
    print('rs1', format(int(ins[20:15]), '05b'))
    print('rs2', format(int(ins[25:20]), '05b'))
    print('func7', format(int(ins[32:25]), '07b'))

    print('imm', format(int(ins[32:20]), '012b'))

    print('imm', format(int(ins[32:25]), '012b'))

    print('jmp', format(int(imm), '012b'))
    '''
