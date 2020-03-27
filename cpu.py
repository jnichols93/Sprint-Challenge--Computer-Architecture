"""CPU functionality."""

import sys

#create instructions for LDI, PRN, HLT, and MUL programs
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
ADD = 0b10100000
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JEQ = 0b01010101
JNE = 0b01010110
JMP = 0b01010100
SP = 7


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # setup ram, register, and pc
        self.ram = [0] * 256
        self.register = [0] * 8
        self.pc = 0
        self.fl = 0
        self.branchtable = {
        HLT: self.handle_hlt,
        LDI: self.handle_ldi,
        PRN: self.handle_prn,
        ADD: self.handle_add,
        MUL: self.handle_mul,
        PUSH: self.handle_push,
        POP: self.handle_pop,
        CALL: self.handle_call,
        RET: self.handle_ret
        }
        
        self.halted = False
        #register 7 is reserved as the stack pointer, which is 0xf4 per specs
        self.register[SP] = 0xf4

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print("format: ls8.py [filename]")
            sys.exit(1)

        program = sys.argv[1]
        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        #open file
        with open(program) as file:
            #read the lines
            for line in file:
                #parse out comments
                line = line.strip().split("#")[0]
                #cast numbers from strings to ints
                val = line.strip()
                #ignore blank lines
                if line == "":
                    continue

                value = int(val, 2)
                self.ram[address] = value
                address +=1
        


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        elif op == "MUL":
            self.register[reg_a] *= self.register[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()


    #ram_read should accept an address to read and return the value
    def ram_read(self, mar):
        return self.ram[mar]

    #ram_write should accept a value to write, and the address to write it to
    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

    
    def handle_ldi(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        
        self.register[operand_a] = operand_b

    def handle_prn(self):
        operand_a = self.ram_read(self.pc + 1)
        print(self.register[operand_a])

    def handle_hlt(self):
        self.halted = True
    #method to handle adding
    def handle_add(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("ADD", operand_a, operand_b)

    def handle_mul(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("MUL", operand_a, operand_b)

    #method to handle push on the stack
    def handle_push(self):
        #decrement the SP register
        self.register[SP] -= 1
        #set operand_a
        operand_a = self.ram_read(self.pc + 1)
        # copy the value in the given register to the address pointed to by SP
        operand_b = self.register[operand_a]
        self.ram[self.register[SP]] = operand_b


    #method to handle popping from the stack to the register
    def handle_pop(self):
        operand_a = self.ram_read(self.pc + 1)
        # copy the value from the address pointed to by SP to the given register
        operand_b = self.ram[self.register[SP]]
        self.register[operand_a] = operand_b
        #increment the SP
        self.register[SP] += 1

    #method to handle subroutine calls
    def handle_call(self):
        #push address after call to top of stack
        self.register[SP] -= 1
        self.ram[self.register[SP]] = self.pc + 2
        # set the pc to the given register
        operand_a = self.ram_read(self.pc + 1)
        self.pc = self.register[operand_a]

    #method to handle the return after a call
    def handle_ret(self):
        #return from subroutine
        self.pc = self.ram[self.register[SP]]
        #pop the value from the stack and store in pc                                                                              
        self.register[SP] += 1

    def run(self):
        while self.halted != True:
            IR = self.ram[self.pc]
            val = IR
            op_count = val >> 6
            IR_length = op_count + 1
            self.branchtable[IR]()

            if IR == 0 or None:
                print(f"Unknown instructions and index {self.pc}")
                sys.exit(1)
            if IR != 80 and IR != 17:
                self.pc += IR_length