"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110


class CPU:
    """Main CPU class."""

    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0  # Program Counter
        self.sp = 7
        self.reg[self.sp] = 0xF4
        # setup branch table
        self.branch_table = {}
        self.branch_table[LDI] = self.handle_LDI
        self.branch_table[PRN] = self.handle_PRN
        self.branch_table[HLT] = self.handle_HLT
        self.branch_table[MUL] = self.handle_MUL
        self.branch_table[PUSH] = self.handle_PUSH
        self.branch_table[POP] = self.handle_POP
        self.running = False

    def load(self):
        """Load a program into memory."""
        address = 0

        if len(sys.argv) != 2:
            print("usage: ls8.py <filename>")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    # deal with comments
                    # split before and after any comment symbol '#'
                    comment_split = line.split("#")

                    # convert the pre-comment portion (to the left) from binary to a value
                    # extract the first part of the split to a number variable
                    # and trim whitespace
                    num = comment_split[0].strip()

                    # ignore blank lines / comment only lines
                    if len(num) == 0:
                        continue

                    # set the number to an integer of base 2
                    instruction = int(num, 2)
                    self.ram[address] = instruction
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        self.running = True
        while self.running:
            IR = self.ram[self.pc]

            operands = {
                "a": self.ram_read(self.pc + 1),
                "b": self.ram_read(self.pc + 2)
            }

            instruction_size = ((IR >> 6) & 0b11) + 1
            self.branch_table[IR](operands)
            self.pc += instruction_size

    def ram_read(self, MAR):
        return self.ram[MAR]

    def raw_write(self, MAR, MDR):
        self.reg[MAR] = MDR

    def handle_LDI(self, operands):
        # Set the value of a register to an integer.
        self.raw_write(operands["a"], operands["b"])

    def handle_PRN(self, operands):
        print(self.reg[operands["a"]])

    def handle_MUL(self, operands):
        self.alu("MUL", operands["a"], operands["b"])

    def handle_PUSH(self, operands):
        # decrement self.sp
        self.reg[self.sp] -= 1
        # value at given register
        value = self.reg[operands["a"]]
        # address the stack pointer is pointing to
        address = self.reg[self.sp]
        self.ram[address] = value

    def handle_POP(self, operands):
        self.reg[operands["a"]] = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1

    def handle_HLT(self, operands):
        self.running = False
