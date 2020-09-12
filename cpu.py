"""CPU functionality."""
import sys


# OP CODES
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
RET = 0b00010001
ADD = 0b10100000
MUL = 0b10100010
AND = 0b10101000
OR = 0b10101010
XOR = 0b10101011

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 # 256 Bytes of memory 
        self.reg = [0] * 8 # 8 Generatl purpose registers
        self.pc = 0 # Program Counter (Internal Register), address of the currently executing instruction
        self.sp = 244 # Stack pointer, set to F4 on initialization
        self.reg[7] = self.sp
        self.running = True # For when the cpu is running
        self.flag = [0] * 8 # Set the flag to hold 8 bits
        self.bt = { # Branch Table
            HLT: self.op_hlt,
            LDI: self.op_ldi,
            PRN: self.op_prn,
            PUSH: self.op_push,
            POP: self.op_pop,
            CALL: self.op_call,
            RET : self.op_ret,
            CMP: self.op_cmp,
            JEQ: self.op_jeq,
            JNE: self.op_jne,
            AND: self.op_and,
            OR: self.op_or,
            XOR: self.op_xor
        }
        ###...
    
    # Get file name from command line arguments
    if len(sys.argv) != 2:
        print("Usage: cpu.py filename")
        sys.exit(1)


    def load(self):
        """Load a program into memory."""

        address = 0

        # Get file name from command line arguments
        filename = sys.argv[1]

        # Open the file with the given filename
        with open(filename)as f:
            # Go through each lines of the file
            for line in f:
                # Split the lines and their comments
                line = line.split("#")
                # Remove the white space and the n/ character
                opcode = line[0].strip()
                # Make sure that the value before the # symbol is not empty
                if opcode == "":
                    continue
                # Convert binary to string
                # and load it in to the memory
                num = int(opcode, 2)
                self.ram_write(num, address)
                address += 1
            
    # It accepts the address to read and return the value stored there
    def ram_read(self, MAR):
        # return MAR (address) MDR (value)
        return self.ram[MAR]

    # It accepts a value to write, and the address to write it to.
    def ram_write(self, MDR, MAR):
        # write MDR (value) to MAR (address
        self.ram[MAR] = MDR

    # MAR = Memory Address Register
    # MDR = Memory Data Register
    ###...

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        # Sprint MVP
        elif op == CMP:
            # If registerA is greater than registerB, set the Greater-than G flag to 1, otherwise set it to 0.
            if self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000100
            # If registerA is less than registerB, set the Less-than L flag to 1, otherwise set it to 0.
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000010
            # If they are equal, set the Equal E flag to 1, otherwise set it to 0.
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 0b00000001
        # Sprint Stretch
        elif op == AND:
            # Compare both values in the register if they exist in both registers
            self.reg[reg_a] &= self.reg[reg_b]
         # Sprint Stretch
        elif op == OR:
            # Compare both values in the register if it exists in either
            self.reg[reg_a] |= self.reg[reg_b]
         # Sprint Stretch
        elif op == XOR:
            # Compare both values in the register if it exists in one not both
            self.reg[reg_a] ^= self.reg[reg_b]
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
    
    def op_hlt(self, operand_a, operand_b):
        # Exit the loop (no matter what comes next)
        self.running = False
    def op_ldi(self, operand_a, operand_b):
        # Load "immediate", store a value in a register, or "set this register to this value"
        # Register location is byte at pc + 1 (operand_a)
        # Value is byte at pc + 2 (operand_b)
        self.reg[operand_a] = operand_b
    def op_prn(self, operand_a, operand_b):
        # Prints the numeric value stored in a register
        # Register location is byte at pc + 1 (operand_a)
        print(self.reg[operand_a])
    def op_push(self, operand_a, operand_b):
        # Decrement the stack pointer by 1
        self.sp -= 1
        # Write the value from the given register and that the stack pointer is set to the memory
        self.ram_write(self.reg[operand_a], self.sp)
    def op_pop(self, operand_a, operand_b):
        # Get the stack pointer in the memory and create a new var called 'value'
        value = self.ram_read(self.sp)
        # Set the value from the given register to the new var 'value'
        self.reg[operand_a] = value
        # Increment the stack pointer by 1
        self.sp += 1
    def op_call(self, operand_a, operand_b):
        # Push the address of the instruction directly after CALL (pc + 2)
        # Decrement the stack pointer by 1
        self.sp -= 1
        # Write the return address to memory at the SP location
        self.ram_write(self.pc + 2, self.sp)
        # Set PC to the address stored in the given register
        self.pc = self.reg[operand_a]
    # Sprint MVP
    def op_jmp(self, operand_a, operand_b):
        # Set PC to the address stored in the given register
        self.pc = self.reg[operand_a]
    def op_ret(self, operand_a, operand_b):
        # Pop the value from the top of the stack and store it in the PC
        self.pc = self.ram_read(self.sp)
        # Increment the stack pointer
        self.sp += 1
    # Sprint MVP
    def op_cmp(self, operand_a, operand_b):
        # Get the CMP method from alu and pass in both operands
        self.alu(CMP, operand_a, operand_b)
        # Increment the program counter by 3
        self.pc += 3
    # Sprint MVP
    def op_jeq(self, operand_a, operand_b):
        # If the flag is set to (true)
        if self.flag == True:
            # Jump to the address stored in the given register
            self.pc = self.reg[operand_a]
        # otherwise increment the program counter by 2
        else:
            self.pc += 2
    # Sprint MVP
    def op_jne(self, operand_a, operand_b):
        # # If the flag is not equal to 1 or (false, 0)
        if self.flag != 1:
            # Jump to the address stored in the given register
            self.pc = self.reg[operand_a]
        # otherwise increment the program counter by 2
        else:
            self.pc += 2
    # Sprint Stretch
    def op_and(self, operand_a, operand_b):
        self.alu(AND, operand_a, operand_b)
        self.pc += 3
    # Sprint Stretch
    def op_or(self, operand_a, operand_b):
        self.alu(OR, operand_a, operand_b)
        self.pc += 3
    # Sprint Stretch
    def op_xor(self, operand_a, operand_b):
        self.alu(XOR, operand_a, operand_b)
        self.pc += 3
        

    def run(self):
        """Run the CPU."""
        # While CPU is running
        while self.running:
            # Read the memory address stored in register PC, and
            # store in IR (instruction register - local variable)
            IR = self.ram_read(self.pc)

            # Some instructions requires up to the next two bytes of data after the PC in memory to perform operations on
            # Read bytes at pc + 1 and pc + 2 and store into operand_a and operand_b
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # Determine if IR is an ALU operation
            isALU = (IR >> 5) & 0b00000001

            # Dispatch ALU operations to alu function
            if isALU == 1:
                self.alu(IR, operand_a, operand_b)
            # Perform actions needed based on given opcode (branch table)
            else:
                if IR in self.bt:
                    self.bt[IR](operand_a, operand_b)
            
            # Update pc to point to next instruction (if the instruction doesn't set the PC)
            setsPc = (IR >> 4) & 0b00000001

            if setsPc == 0:
                # Determine number of operands
                num_operands = IR >> 6
                # Update pc to point to next instruction
                self.pc += num_operands + 1

   