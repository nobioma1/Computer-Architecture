"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0  # Program Counter
        self.sp = 7
        self.reg[self.sp] = 0xF4
        self.op_pc = False

    def load(self):
        """Load a program into memory."""

        # address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

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
        LDI = 0b10000010
        PRN = 0b01000111
        HLT = 0b00000001
        MUL = 0b10100010
        PUSH = 0b01000101
        POP = 0b01000110
        ADD = 0b10100000
        CALL = 0b01010000
        RET = 0b00010001
        instruction_size = 0

        running = True


        while running:
            IR = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if IR == HLT:
                running = False

            elif IR == LDI:
                # Set the value of a register to an integer.
                self.raw_write(operand_a, operand_b)
                # Update PC (Program Counter)
                instruction_size = 3
                self.op_pc = False

            elif IR == PRN:
                print(self.reg[operand_a])
                instruction_size = 2
                self.op_pc = False

            elif IR == MUL:
                self.alu("MUL", operand_a, operand_b)
                instruction_size = 3
                self.op_pc = False

            elif IR == ADD:
                self.alu("ADD", operand_a, operand_b)
                instruction_size = 3
                self.op_pc = False

            elif IR == PUSH:
                # decrement self.sp
                self.reg[self.sp] -= 1
                # value at given register
                value = self.reg[operand_a]
                # address Stack pointer is pointing to
                address = self.reg[self.sp]
                self.ram[address] = value
                instruction_size = 2
                self.op_pc = False

            elif IR == POP:
                # get value
                self.reg[operand_a] = self.ram_read(self.reg[self.sp])
                self.reg[self.sp] += 1
                instruction_size = 2
                self.op_pc = False

            elif IR == CALL:
                self.reg[self.sp] -= 1  # Decrement Stack Pointer
                # Push return location to stack
                self.ram[self.reg[self.sp]] = self.pc + 2
                # set pc to subroutine
                self.pc = self.reg[operand_a]
                self.op_pc = True
                instruction_size = 2

            elif IR == RET:
                self.pc = self.ram_read(self.reg[self.sp])
                self.reg[self.sp] += 1
                self.op_pc = True

            else:
                print(f"Unknown Instruction {IR:08b}")
                sys.exit(1)

            # update instruction size
            if not self.op_pc:
                self.pc += instruction_size

    def ram_read(self, MAR):
        return self.ram[MAR]

    def raw_write(self, MAR, MDR):
        self.reg[MAR] = MDR
