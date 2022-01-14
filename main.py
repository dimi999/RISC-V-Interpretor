from constante import *
import math
from time import sleep

const = 0x80000000                          # scadem aceasta constanta din adresele de memorie pentru a porni de la adresa 0

pc = 0                                      # program counter
passAddress = 0                             # adresa etichetei pass

memory = [0 for i in range(1024 * 1024)]    # 1MB RAM

register = {0: 0,                           # 32 de registrii
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


# extrage numarul format din bitii de pe pozitiile [i...j] din x
def bitSeqToNumber(x, i, j):
    return (x & ((1 << (j + 1)) - (1 << i))) >> i


# extrage numarul(intreg) format din bitii de pe pozitiile [i...j] din x
def signedBitSeqToNumber(x, i, j):
    if x & (1 << j):
        return ((x & ((1 << (j + 1)) - (1 << i))) - (1 << (j + 1))) >> i
    else:
        return (x & ((1 << (j + 1)) - (1 << i))) >> i


# transforma un numar natural reprezentat pe msb biti in complementul sau fata de doi
def complTwo(x, msb):
    if x & (1 << msb):
        x -= (1 << (msb + 1))
    return x


# concateneaza 4 octeti incepand de la adresa din parametru
def getInstruction(adresa):
    return (memory[adresa] << 24) + (memory[adresa + 1] << 16) + (memory[adresa + 2] << 8) + memory[adresa + 3]


# addi rd, rs1, imm   <=>   reg[rd] = reg[rs1] + imm
# instructiunile li, mv, nop sunt implementate cu addi
def addi(rd, rs1, immediate):
    # EXECUTE
    result = register[rs1] + immediate
    # MEMORY
    register[rd] = result


# ori rd, rs1, imm   <=>   reg[rd] = reg[rs1] | imm
def ori(rd, rs1, immediate):
    # EXECUTE
    result = register[rs1] | immediate
    # MEMORY
    register[rd] = result


# slli rd, rs1, imm   <=>   reg[rd] = reg[rs1] << imm
def slli(rd, rs1, immediate):
    # EXECUTE
    result = register[rs1] << immediate
    # MEMORY
    register[rd] = result


# srl rd, rs1, rs2   <=>   reg[rd] = reg[rs1] >> lw5(reg[rs2])
# srl face shiftare logica, nu aritmetica (implicit, >> in Python este shiftare aritmetica)
# in EXECUTE am implementat shiftarea logica
def srl(rd, rs1, rs2):
    # EXECUTE
    if register[rs1] >= 0 or (register[rs2] & 31) == 0:
        result = register[rs1] >> (register[rs2] & 31)
    else:
        s = 0
        for i in range(0, 32):
            if register[rs1] & (1 << i):
                s += (1 << i)
        result = s >> (register[rs2] & 31)

    # MEMORY
    register[rd] = result


# xor rd, rs1, rs2   <=>   reg[rd] = reg[rs1] ^ reg[rs2]
def xor(rd, rs1, rs2):
    # EXECUTE
    result = register[rs1] ^ register[rs2]
    # MEMORY
    register[rd] = result


# rem rd, rs1, rs2   <=>   reg[rd] = reg[rs1] % reg[rs2]
# in Python, operatorul % se comporta diferit fata de instructiunea din RISC-V
# functia fmod din modulul math are comportamentul dorit
# daca reg[rs2] == 0 (impartitorul este 0), atunci d = i * c + r <=> d = 0 * c + r <=> d = r <=> reg[rd] = reg[rs1]
def rem(rd, rs1, rs2):
    # EXECUTE
    if register[rs2] != 0:
        result = math.fmod(register[rs1], register[rs2])
    else:
        result = register[rs1]

    # MEMORY
    register[rd] = result


# lui rd, imm   <=>   reg[rd] = imm << 12
def lui(rd, immediate):
    # EXECUTE
    result = immediate << 12
    # MEMORY
    register[rd] = result


# instructiunea j se implementeaza cu jal
def jal(rd):
    # MEMORY
    register[rd] = pc + 4


# brench not equal   <=>   reg[rs1] != reg[rs2] then jump(by offset) else continue
def bne(rs1, rs2, offset):
    # EXECUTE
    global pc
    if register[rs1] != register[rs2]:
        pc += offset
    else:
        pc += 4


# brench equal   <=>   reg[rs1] == reg[rs2] then jump(by offset) else continue
# instructiunea beqz se implementeaza cu beq
def beq(rs1, rs2, offset):
    # EXECUTE
    global pc
    if register[rs1] == register[rs2]:
        pc += offset
    else:
        pc += 4


# auipc rd, imm   <=>   reg[rd] = pc + (imm << 12)
def auipc(rd, immediate):
    # EXECUTE
    result = pc + (immediate << 12)
    # MEMORY
    register[rd] = result


# lw rd, rs1, offset   <=>   reg[rd] = memory(reg[rs1] + offset)
def lw(rd, rs1, offset):
    # MEMORY
    register[rd] = getInstruction(register[rs1] + offset)


# sw rs1, rs2, offset   <=>   memory(reg[rs1] + offset) = reg[rs2]
def sw(rs1, rs2, offset):
    # WRITE BACK
    memory[register[rs1] + offset] = bitSeqToNumber(register[rs2], 24, 31)
    memory[register[rs1] + offset + 1] = bitSeqToNumber(register[rs2], 16, 23)
    memory[register[rs1] + offset + 2] = bitSeqToNumber(register[rs2], 8, 15)
    memory[register[rs1] + offset + 3] = bitSeqToNumber(register[rs2], 0, 7)


# incarca in RAM programul din file
def loadTest(file):
    # golim memoria inainte de rularea unui nou test
    for i in range(len(memory)):
        memory[i] = 0

    global passAddress
    with open(file, 'r') as f:
        for line in f.readlines():
            if (line[0] == '8') and ('<' not in line):
                # linia contine o instructiune valida
                adresa, instructiune = line.split(':')
                lungime_instructiune = len(instructiune.strip())
                instructiune = int(instructiune.strip(), 16)
                adresa = int(adresa.strip(), 16) - const

                if lungime_instructiune == 4:
                    # incarcam cei 2 octeti ai instructiunii la adresa de memorie precizata
                    memory[adresa] = bitSeqToNumber(instructiune, 8, 15)
                    memory[adresa + 1] = bitSeqToNumber(instructiune, 0, 7)
                else:
                    # incarcam cei 4 octeti ai instructiunii la adresa de memorie precizata
                    memory[adresa] = bitSeqToNumber(instructiune, 24, 31)
                    memory[adresa + 1] = bitSeqToNumber(instructiune, 16, 23)
                    memory[adresa + 2] = bitSeqToNumber(instructiune, 8, 15)
                    memory[adresa + 3] = bitSeqToNumber(instructiune, 0, 7)

            elif 'pass' in line:
                # retinem adresa etichetei pass
                adresa, eticheta = line.split('<')
                passAddress = int(adresa.strip(), 16) - const


def runTest(fisier):
    sleep(1)
    print(fisier, end=" ")

    loadTest(fisier)

    global pc
    pc = 0
    while True:
        # print(f'Memory Address {int(str(pc), 16)}')

        # registrul 0 este hard-wired zero; il resetam la fiecare instructiune
        register[0] = 0

        # INSTRUCTION FETCH
        instruction = getInstruction(pc)

        # INSTRUCTION DECODE
        opcode = bitSeqToNumber(instruction, 0, 6)

        if opcode == OP_LOAD:   # LW
            rd = bitSeqToNumber(instruction, 7, 11)
            rs1 = bitSeqToNumber(instruction, 15, 19)
            funct3 = bitSeqToNumber(instruction, 12, 14)
            offset = signedBitSeqToNumber(instruction, 20, 31)

            if funct3 == FUNCT3_LW:
                lw(rd, rs1, offset)
            else:
                print("Instructiune neimplementata")
                break

            pc += 4

        elif opcode == OP_IMM:   # ADDI(+ LI, MV, NOP), SLLI, ORI
            rd = bitSeqToNumber(instruction, 7, 11)
            rs1 = bitSeqToNumber(instruction, 15, 19)
            funct3 = bitSeqToNumber(instruction, 12, 14)
            immediate = signedBitSeqToNumber(instruction, 20, 31)

            if funct3 == FUNCT3_ADDI:
                addi(rd, rs1, immediate)
            elif funct3 == FUNCT3_SLLI:
                slli(rd, rs1, immediate)
            elif funct3 == FUNCT3_ORI:
                ori(rd, rs1, immediate)
            else:
                print("Instructiune neimplementata")
                break

            pc += 4

        elif opcode == OP_AUIPC:   # AUIPC
            rd = bitSeqToNumber(instruction, 7, 11)
            immediate = bitSeqToNumber(instruction, 12, 31)

            auipc(rd, immediate)

            pc += 4

        elif opcode == OP_STORE:   # SW
            rs1 = bitSeqToNumber(instruction, 15, 19)
            rs2 = bitSeqToNumber(instruction, 20, 24)
            offset = complTwo(bitSeqToNumber(instruction, 7, 11) + (bitSeqToNumber(instruction, 25, 31) << 5), 11)
            funct3 = bitSeqToNumber(instruction, 12, 14)

            if funct3 == FUNCT3_SW:
                sw(rs1, rs2, offset)
            else:
                print("Instructiune neimplementata")
                break

            pc += 4

        elif opcode == OP_OP:   # XOR, SRL, REM
            rd = bitSeqToNumber(instruction, 7, 11)
            rs1 = bitSeqToNumber(instruction, 15, 19)
            rs2 = bitSeqToNumber(instruction, 20, 24)
            funct3 = bitSeqToNumber(instruction, 12, 14)

            if funct3 == FUNCT3_XOR:
                xor(rd, rs1, rs2)
            elif funct3 == FUNCT3_SRL:
                srl(rd, rs1, rs2)
            elif funct3 == FUNCT3_REM:
                rem(rd, rs1, rs2)
            else:
                print("Instructiune neimplementata")
                break

            pc += 4

        elif opcode == OP_LUI:   # LUI
            rd = bitSeqToNumber(instruction, 7, 11)
            immediate = bitSeqToNumber(instruction, 12, 31)

            lui(rd, immediate)

            pc += 4

        elif opcode == OP_BRANCH:   # BNE, BEQ(+ BEQZ)
            rs1 = bitSeqToNumber(instruction, 15, 19)
            rs2 = bitSeqToNumber(instruction, 20, 24)
            funct3 = bitSeqToNumber(instruction, 12, 14)

            offset = (bitSeqToNumber(instruction, 7, 7) << 11) + \
                     (bitSeqToNumber(instruction, 8, 11) << 1) + \
                     (bitSeqToNumber(instruction, 25, 30) << 5) + \
                     (bitSeqToNumber(instruction, 31, 31) << 12)
            offset = complTwo(offset, 12)

            if funct3 == FUNCT3_BEQ:
                beq(rs1, rs2, offset)
            elif funct3 == FUNCT3_BNE:
                bne(rs1, rs2, offset)
            else:
                print("Instructiune neimplementata")
                break

        elif opcode == OP_JAL:   # JAL(+ J)
            rd = bitSeqToNumber(instruction, 7, 11)
            offset = (bitSeqToNumber(instruction, 31, 31) << 20) + \
                     (bitSeqToNumber(instruction, 21, 30) << 1) + \
                     (bitSeqToNumber(instruction, 20, 20) << 11) + \
                     (bitSeqToNumber(instruction, 12, 19) << 12)

            jal(rd)

            pc += offset

        elif opcode == OP_EXIT:   # ECALL(exit call)
            if pc >= passAddress:
                print('PASS')
            else:
                print('FAIL')
            break

        elif opcode == OP_EMPTY:
            pc += 4

        else:
            print("Opcode invalid")
            break


teste = ["rv32ui-v-addi.mc", "rv32ui-v-beq.mc", "rv32ui-v-srl.mc", "rv32ui-v-xor.mc", "rv32um-v-rem.mc",
         "rv32ui-v-lw.mc", "rv32ui-v-sw.mc"]

for test in teste:
    runTest(test)
