import math

pc = 0
passedAdress = 0
const = 0x80000000
memory = [0 for i in range(100000)]
register = {0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0,
            8: 0,
            9: 0,
            10: 0,
            11: 0,
            12: 0,
            13: 0,
            14: 0,
            15: 0,
            16: 0,
            17: 0,
            18: 0,
            19: 0,
            20: 0,
            21: 0,
            22: 0,
            23: 0,
            24: 0,
            25: 0,
            26: 0,
            27: 0,
            28: 0,
            29: 0,
            30: 0,
            31: 0}

funct3Dict = {
    0: 'addi',
    1: 'slli',
    2: 'slti',
    3: 'sltiu',
    4: 'xori',
    5: 'srli',
    6: 'ori',
    7: 'andi'
}

#EXECUTE

def addi(rd, rs1, immediate):
    #MEM
    register[rd] = register[rs1] + immediate
    # if register[rd] > const:
    #     register[rd] = -const + register[rd] % const


def ori(rd, rs1, immediate):
    #MEM
    register[rd] = register[rs1] | immediate


def slli(rd, rs1, immediate):
    #MEM
    register[rd] = register[rs1] << immediate


def rshift(val, n):
    s = val & 0x80000000
    for i in range(0,n):
        val >>= 1
        val |= s
    return val


def srl(rs2, rs1, rd):
    if register[rs1] >= 0 or (register[rs2] & 31) == 0:
        register[rd] = register[rs1] >> (register[rs2] & 31)
    else:
        s = 0
        for i in range(0, 32):
            if register[rs1] & (1 << i):
                s += (1 << i)
        register[rd] = s >> (register[rs2] & 31)


def xor(rs2, rs1, rd):
    register[rd] = register[rs2] ^ register[rs1]


def rem(rs2, rs1, rd):
    if register[rs2] != 0:
        register[rd] = math.fmod(register[rs1], register[rs2])
    else:
        register[rd] = register[rs1]


def lui(rd, immediate):
    #MEM
    register[rd] = immediate << 12


def jal(rd):
    #MEM
    register[rd] = pc + 4


def bne(rs1, rs2, offset):
    global pc
    if register[rs1] != register[rs2]:
        pc += offset
    else:
        pc += 4


def beq(rs1, rs2, offset):
    global pc
    if register[rs1] == register[rs2]:
        pc += offset
    else:
        pc += 4


def loadTestSrs(file):
    k = 0
    global passedAdress
    with open(file, 'r') as f:
        for line in f.readlines():
            if (line[0] == '8') and (not '<' in line):
                inutil, util = line.split(':')
                util = int(util.strip(), 16)
                memory[k] = bitsToNumber(util, 24, 31)
                k += 1
                memory[k] = bitsToNumber(util, 16, 23)
                k += 1
                memory[k] = bitsToNumber(util, 8, 15)
                k += 1
                memory[k] = bitsToNumber(util, 0, 7)
                k += 1
            elif '<' in line and 'pass' in line:
                adresa, eticheta = line.split('<')
                passedAdress = k



def bitsToNumber(x, i, j):
    return (x & ((1 << (j + 1)) - (1 << i))) >> i


def signedBitsToNumber(x, i, j):
    if x & (1 << j):
        return ((x & ((1 << (j + 1)) - (1 << i))) - (1 << (j + 1))) >> i
    else:
        return (x & ((1 << (j + 1)) - (1 << i))) >> i


def sgnext(offset):
    if offset & (1 << 12):
        offset -= (1 << 13)
    return offset


def getInstruction(pc):
    return (memory[pc] << 24) + (memory[pc + 1] << 16) + (memory[pc + 2] << 8) + memory[pc + 3]


loadTestSrs('rv32ui-v-addi.mc')

while True:
    register[0] = 0
    if pc >= 500:
        pc += 0

    # IF - instruction fetch
    instruction = getInstruction(pc)

    # print(bitsToNumberJmek(instruction, 20, 31))

    # ID - instruction decode
    opcode = bitsToNumber(instruction, 0, 6)
    if opcode == 19:
        rd = bitsToNumber(instruction, 7, 11)
        funct3 = bitsToNumber(instruction, 12, 14)
        rs1 = bitsToNumber(instruction, 15, 19)
        immediate = signedBitsToNumber(instruction, 20, 31)

        if funct3 == 0:
            addi(rd, rs1, immediate)
        elif funct3 == 6:
            ori(rd, rs1, immediate)
        elif funct3 == 1:
            slli(rd, rs1, immediate)

        pc += 4

    elif opcode == 55:
        rd = bitsToNumber(instruction, 7, 11)
        immediate = bitsToNumber(instruction, 12, 31)

        lui(rd, immediate)

        pc += 4

    elif opcode == 51:
        rs2 = bitsToNumber(instruction, 20, 24)
        rs1 = bitsToNumber(instruction, 15, 19)
        rd = bitsToNumber(instruction, 7, 11)
        funct3 = bitsToNumber(instruction, 12, 14)

        if funct3 == 5:
            srl(rs2, rs1, rd)
        elif funct3 == 4:
            xor(rs2, rs1, rd)
        elif funct3 == 6:
            rem(rs2, rs1, rd)

        pc += 4

    elif opcode == 111:
        rd = bitsToNumber(instruction, 7, 11)
        offset = (bitsToNumber(instruction, 31, 31) << 20) + \
                 (bitsToNumber(instruction, 21, 30) << 1) + \
                 (bitsToNumber(instruction, 20, 20) << 11) + \
                 (bitsToNumber(instruction, 12, 19) << 12)

        jal(rd)

        pc += offset

    elif opcode == 99:
        rs1 = bitsToNumber(instruction, 15, 19)
        rs2 = bitsToNumber(instruction, 20, 24)
        funct3 = bitsToNumber(instruction, 12, 14)
        offset = (bitsToNumber(instruction, 7, 7) << 11) + \
                 (bitsToNumber(instruction, 8, 11) << 1) + \
                 (bitsToNumber(instruction, 25, 30) << 5) + \
                 (bitsToNumber(instruction, 31, 31) << 12)

        offset = sgnext(offset)

        if funct3 == 1:
            bne(rs1, rs2, offset)
        elif funct3 == 0:
            beq(rs1, rs2, offset)

    elif opcode == 115:
        if pc >= passedAdress:
            print('pass')
        else:
            print('fail', pc)
        break




