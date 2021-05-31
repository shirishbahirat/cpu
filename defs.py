from math import log


CPU_BITS = 32
CPU_REGS = 32
CPU_ALUW = 4

ACTIVE_LOW, INACTIVE_HIGH = 0, 1

RTYPE = 51
ITYPE = 3
STYPE = 35
BTYPE = 32
UTYPE = 42
SBTYPE = 99


# R-format rd = rs1 op rs2
AND = 0
OR = 1
ADD = 2
SLL = 3
SLT = 4
SLTU = 5
SUB = 6
XOR = 7
SRL = 8
SRA = 9

# constants
XPAD = (2**20) - 1

# width of signals
REG_WIDTH = int(log(CPU_BITS, 2))
