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


def auipc(rd, immediate):
    register[rd] = pc + (immediate << 12)

countlw = 0

def lw(rd, rs1, offset):
    global countlw
    register[rd] = getInstruction(register[rs1] + offset)
    countlw += 1


def sw(rs1, rs2, offset):
    global countlw
    if countlw == 4:
        countlw += 0
    memory[register[rs1] + offset] = bitsToNumber(register[rs2], 24, 31)
    memory[register[rs1] + offset + 1] = bitsToNumber(register[rs2], 16, 23)
    memory[register[rs1] + offset + 2] = bitsToNumber(register[rs2], 8, 15)
    memory[register[rs1] + offset + 3] = bitsToNumber(register[rs2], 0, 7)

def loadTestSrs(file):
    k = 0
    global passedAdress
    with open(file, 'r') as f:
        for line in f.readlines():
            if (line[0] == '8') and (not '<' in line):
                adresa, instructiune = line.split(':')
                instructiune = int(instructiune.strip(), 16)
                adresa = int(adresa.strip(), 16) - const
                if adresa >= 12288 and adresa < 12300:
                    memory[adresa] = bitsToNumber(instructiune, 8, 15)
                    memory[adresa + 1] = bitsToNumber(instructiune, 0, 7)
                else:
                    memory[adresa] = bitsToNumber(instructiune, 24, 31)
                    memory[adresa + 1] = bitsToNumber(instructiune, 16, 23)
                    memory[adresa + 2] = bitsToNumber(instructiune, 8, 15)
                    memory[adresa + 3] = bitsToNumber(instructiune, 0, 7)
            elif '<' in line and 'pass' in line:
                adresa, eticheta = line.split('<')
                passedAdress = int(adresa.strip(), 16) - const



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

def sgnext2(offset):
    if offset & (1 << 11):
        offset -= (1 << 12)
    return offset


def getInstruction(pc):
    return (memory[pc] << 24) + (memory[pc + 1] << 16) + (memory[pc + 2] << 8) + memory[pc + 3]


loadTestSrs('rv32um-v-rem.mc')
while True:
    register[0] = 0

    if pc == 10720:
        pc += 0

    # IF - instruction fetch
    instruction = getInstruction(pc)

    # ID - instruction decode
    opcode = bitsToNumber(instruction, 0, 6)

    if opcode == 0:
        pc += 4

    elif opcode == 3:
        rd = bitsToNumber(instruction, 7, 11)
        funct3 = bitsToNumber(instruction, 12, 14)
        rs1 = bitsToNumber(instruction, 15, 19)
        offset = signedBitsToNumber(instruction, 20, 31)

        if funct3 == 2:
            lw(rd, rs1, offset)

        pc += 4

    elif opcode == 19:
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

    elif opcode == 23:
        rd = bitsToNumber(instruction, 7, 11)
        immediate = bitsToNumber(instruction, 12, 31)

        auipc(rd, immediate)

        pc += 4

    elif opcode == 35:
        offset = bitsToNumber(instruction, 7, 11) + (bitsToNumber(instruction, 25, 31) << 5)
        funct3 = bitsToNumber(instruction, 12, 14)
        rs1 = bitsToNumber(instruction, 15, 19)
        rs2 = bitsToNumber(instruction, 20, 24)

        offset = sgnext2(offset)

        if funct3 == 2:
            sw(rs1, rs2, offset)

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




