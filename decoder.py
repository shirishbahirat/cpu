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
    imm = intbv(0)[32:]

    op_type = ''

    if opcode == RTYPE:
        alu_op = 2
        op_type = 'RTYPE'
    elif opcode == ITYPE:
        alu_op = 0
        op_type = 'ITYPE'
    elif opcode == STYPE:
        alu_op = 0
        op_type = 'STYPE'
    elif opcode == SBTYPE:
        alu_op = 7
        op_type = 'SBTYPE'

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

    if opcode == ITYPE:
        rda = registers[instruction[20:15]]
        rdx = instruction[32:20]

    if opcode == STYPE:
        imm[5:] = instruction[12:7]
        imm[12:5] = instruction[32:25]

        rda = registers[instruction[25:20]]
        rdx = imm

    if opcode == SBTYPE:
        imm[12] = instruction[31]
        imm[11:5] = instruction[31:25]
        imm[11] = instruction[7]
        imm[5:1] = instruction[12:8]
        imm[0] = 0

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
        result = True if (rda.signed() < rdx.signed()) else False
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

    if opcode == ITYPE:
        registers[instruction[12:7]] = data_ram[result]

    if opcode == STYPE:
        data_ram[result] = registers[instruction[25:20]]

    if opcode == SBTYPE:
        if result == 0:
            pc = pc + int(imm)
            i = pc

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
        print(format(i, '02x'), format(int(instruction), '08x'), 'op', op_type, format(int(instruction[7:0]), '02x'),
              'rs1', format(int(instruction[20:15]), '02x'), 'rs2', format(int(instruction[25:20]), '02x'), 'rd',
              format(int(instruction[12:7]), '02x'), '\n',
              'alu-op', aluop, 'rs1-data', format(int(rda), '08x'), 'rs2-data', format(int(rdx), '08x'), 'rd-data', format(int(result), '08x'))

    if instruction[7:0] == ITYPE:
        print(format(i, '02x'), format(int(instruction), '08x'), 'op', op_type, format(int(instruction[7:0]), '02x'),
              'base', format(int(instruction[20:15]), '02x'), 'rd', format(int(instruction[12:7]), '02x'),
              'width', format(int(instruction[15:12]), '01x'), 'offset', format(int(instruction[32:20]), '02x'), '\n',
              'alu-op', aluop, 'base-data', format(int(rda), '08x'), 'rd-data-offset', format(int(result), '08x'), 'rd-data', format(int(registers[instruction[12:7]]), '02x'))

    if instruction[7:0] == STYPE:
        print(format(i, '02x'), format(int(instruction), '08x'), 'op', op_type, format(int(instruction[7:0]), '02x'),
              'base', format(int(instruction[20:15]), '02x'), 'rs2', format(int(instruction[25:20]), '02x'),
              'width', format(int(instruction[15:12]), '01x'), 'offset', format(int(imm), '08x'), '\n',
              'alu-op', aluop, 'base-data', format(int(rda), '08x'), 'stored-address base-data+offset', format(int(result), '08x'), '\n',
              'rs2-data stored-data', format(int(registers[instruction[25:20]]), '08x'), 'data-ram', format(int(data_ram[result]), '08x'))

    if instruction[7:0] == SBTYPE:
        print(format(i, '02x'), format(int(instruction), '08x'), 'op', op_type, format(int(instruction[7:0]), '02x'),
              'rs1', format(int(instruction[20:15]), '02x'), 'rs2', format(int(instruction[25:20]), '02x'), 'offset',
              format(int(imm), '08x'), '\n', 'alu-op', aluop, 'result', result, 'pc', i)
