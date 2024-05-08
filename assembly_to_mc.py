file_name = "handle_packets.s"
f = open(file_name, "r")
f_out = open("bubble_sort.coe", "w") # Output file


inject_4_nops_per_instruction = False # Injects 4 addi r0 r0 0 between every instruction 
sw_lw_debug = False # Prints data when executing lw and sw functions
coe_file_syntax = False # Format output file for memory instantiation in ISE
if coe_file_syntax:
    f_out.write("MEMORY_INITIALIZATION_RADIX=2;\nMEMORY_INITIALIZATION_VECTOR=\n")





delims = (" ", ",")
curr_addr = 0
subroutine_addresses = {"main": 0}

reg_dict = {
    "zero" : 0, # zero constant
    "r" : 1,  # Return address
    "ra" : 1, # Return address
    "sp" : 2, # Stack pointer
    "gp" : 3, # Global pointer
    "tp" : 4, # Thread pointer
    "t0" : 5, # Temp regs
    "t1" : 6, # Temp regs
    "t2" : 7, # Temp regs
    "fp" : 8, # Frame pointer, shared with s0
    "s0" : 8, # Saved reg, shared with fp
    "s1" : 9, # Saved register
    "a0" : 10, # Function arguments and return values
    "a1" : 11, # Function arguments and return values
    "a2" : 12, # Function arguments
    "a3" : 13, # Function arguments
    "a4" : 14, # Function arguments
    "a5" : 15, # Function arguments
    "a6" : 16, # Function arguments
    "a7" : 17, # Function arguments
    "FIFO_ADDR" : int("0xFFF", 16),
    "FIFO_READY" : int("0x7FF", 16),
    "FFT_ADDR" : int("0xFFE", 16),
    "IP_BUFFER" : int("0xFFF", 16)
    
    # Expand to s2-s11 and t3-t6 if necessary
}

def reg_decode(reg):
    return "{0:b}".format(reg_dict[reg]).zfill(5) # Return 5 bit register index

# Converts a decimal number to a signed binary number string of length bitlen
def get_offset_str(decimal, bitlen):
    if int(decimal) < 0: # Check if negative
        bits = int("1"*bitlen, 2) + int(decimal) + 1 # Get two's complement of decimal value in binary
        return "{0:b}".format(bits).zfill(bitlen)
    
    return "{0:b}".format(int(decimal)).zfill(bitlen) # Return for positive values

def parse_line(data, addr):
    data = data.replace(',', " ")  # Replace commas with whitespace
    data = data.replace('(', " ") # Seperate offset from reg
    data = data.replace(')', "") # Remove end ) from reg field
    data = data.replace(':', "") # Remove colon from subroutine declarations
    data = data.split() # Split line into elements
    
    op = data[0]
    
    if op in subroutine_addresses: # Do not generate instruction for subroutine declarations
        return -1
    
    match op:
        case "addi":
            return addi(data)
        case "sw":
            return sw(data)
        case "j":
            return j(data, addr)
        case "lw":
            return lw(data)
        case "slli":
            return slli(data)
        case "add":
            return add(data)
        case "ble":
            return ble(data, addr)
        case "li":
            return li(data)
        case "jr":
            return jr(data)
        case "nop":
            return nop()
        case _:
            return nop()
    return

def addi(data):
    # data = [opcode dst src imm]
    imm = get_offset_str(data[3], 12) # [31:20] - 12b
    rs1 =  reg_decode(data[2])  # [19:15] - 5b
    funct3 = "000"              # [14:12] - 3b
    rd =  reg_decode(data[1])   # [11:7] - 5b
    opcode = "0010011"          # [6:0] - 7b 
    
    return imm + rs1 + funct3 + rd + opcode

def sw(data):
    # data = [opcode src offset dst]
    imm = get_offset_str(reg_decode(data[3]), 12)
    
    imm2 = imm[0:7]             # [31:25] - 7b
    rs2 =  reg_decode(data[1])  # [24:20] - 5b
    rs1 =  reg_decode("zero")  # [19:15] - 5b
    funct3 = "010"              # [14:12] - 3b
    imm1 =  imm[7:12]           # [11:7] - 5b
    opcode = "0100011"          # [6:0] - 7b 
    
    if sw_lw_debug:
        print(data)
        print("store word: " + imm2 + " " + rs2 + " " +rs1 + " " +funct3 + " " +imm1 + " " +opcode)
    
    return imm2 + rs2 + rs1 + funct3 + imm1 + opcode

def j(data, addr): # Jump and link
    #jump straight to address, or jump with offset from curr address????
    offset = str(int(subroutine_addresses[data[1]]) - addr) # Get subroutine address offset
    offset = get_offset_str(addr, 20) # Format as 20 bit string
   #offset = get_offset_str(data[1], 20) # 20b
    rd = "00000" #rd=x0  5b
    opcode = "1100000" # 7b
    
    return offset + rd + opcode

# Needs no special implementation, just relies on same opcode and format as j.
# Uses a nonzero register and sets offset = 0
def jr(data):
    # data = [opcode register]
    addr = "00000000000000000000"
    addr_upper = "000000000000" # imm[19:8]
    addr_lower = "0000000" # imm[7:0]
    rd = reg_decode(data[1]) #  5b
    opcode = "0010001" # 7b
    
    return addr_upper + rd + addr_lower + opcode

def lw(data):
    # data = [opcode src offset dst]
    imm = get_offset_str(reg_decode(data[3]), 12) # [31:20] - 12b
    rs1 = reg_decode("zero")   # [19:15] - 5b
    funct3 = "010"              # [14:12] - 3b
    rd =  reg_decode(data[1])  # [11:7] - 5b
    opcode = "0000011"          # [6:0] - 7b 
    
    if sw_lw_debug:
        print(data)
        print("Load word:  " + imm + " " +rs1 + " " +funct3 + " " +rd + " " +opcode)
    
    return imm + rs1 + funct3 + rd + opcode

def slli(data):
    # data = [opcode dst src amt]
    imm = get_offset_str(data[3], 12) # [31:20] - 5b
    rs1 = reg_decode(data[2])   # [19:15] - 5b
    funct3 = "001"              # [14:12] - 3b
    rd =  reg_decode(data[1])  # [11:7] - 5b
    opcode = "0010011"          # [6:0] - 7b 
    
    return imm + rs1 + funct3 + rd + opcode
    
def add(data):
    # data = [opcode rd rs1 rs2]
    
    funct7 = "0000000"
    rs2 = reg_decode(data[3])
    rs1 = reg_decode(data[2])
    funct3 = "000"
    rd = reg_decode(data[1])
    opcode = "0110011"
    
    return funct7 + rs2 + rs1 + funct3 + rd + opcode


def bge(data, addr):
    # The implementation for b type instructions is really weird. Let me know how it looks in the hardware
    # and if it differs from the spec in the Risc V manual I can change this function no problem
    # branch rs1 < rs2: jump_location
    
    
    # data = [opcode rs1 rs2 offset]
    # branch rs1 > rs2: jump_location
    offset = get_offset_str(subroutine_addresses[data[3]] - addr, 12) # [31:20] - 5b
    
    imm2 = offset[0] + offset[2:9] #imm[12] + imm[10:5] trust me the math is right (dont trust me)
    rs2 = reg_decode(data[2])
    rs1 = reg_decode(data[1])
    funct3 = "101"
    imm1 = offset[9:12] + offset[1]
    opcode = "1100011"
    
    return imm2 + rs2 + rs1 + funct3 + imm1 + opcode

# Pseudo instruction. Implement bge and flip operands
def ble(data, addr=0):
    old = 0
    if old: # old way 
        # The implementation for b type instructions is really weird. Let me know how it looks in the hardware
        # and if it differs from the spec in the Risc V manual I can change this function no problem
        # branch rs1 < rs2: jump_location
        reorder = [data[0], data[2], data[1], data[3]]
        instr = bge(reorder)
        return instr
    else: # new way
        offset = get_offset_str(subroutine_addresses[data[3]] - addr, 12) # [31:20] - 5b
    
        # offset == "11 10 9 8 7 6 5 4 3 2 1  0 " -12b
        # indices:    0  1 2 3 4 5 6 7 8 9 10 11
        # ble     a4,a5,.L3 - B type
        # imm[11](1b)_imm[9:4](6b)_rs2(5b)_rs1(5b)_101(3b)_imm[3:0](4b)_imm[10](1b)_110_00
    
        imm2 = offset[0] + offset[2:8] #imm[11] + imm[9:4] trust me the math is right (dont trust me)
        rs2 = reg_decode(data[2])
        rs1 = reg_decode(data[1])
        funct3 = "101"
        imm1 = offset[8:12] + offset[1]
        opcode = "1100011"

        return imm2 + rs2 + rs1 + funct3 + imm1 + opcode

# Compressed instruction, that's why you couldn't find it initially. It is in the RISC-V Reference manual though
# Implemented by calling addi rather than using a unique hardware implementation
def li(data):
    reorder = ["addi", data[1], "zero", data[2]]
    return addi(reorder)



def nop():
    return addi(["addi", "zero", "zero", "0"]) #addi r0 = r0 + 0


# Loop over file to define subroutine address indices
for line in f:
    if line[0] == '.':
        line = line.replace(':', "")
        line = line.split()
        subroutine_addresses[line[0]] = curr_addr
        continue # Do not increment address on hit
    curr_addr = curr_addr + 1


f.close()
f = open(file_name, "r")

# Loop over to translate instructions to binary
curr_addr = 0
for line in f:
    #f_out.write(parse_line(line))
    cmd = parse_line(line, curr_addr)
    if cmd == -1: continue # Skip subroutine declarations
    
    f_out.write(cmd) # Write binary 32 bit instruction to file
    if coe_file_syntax: f_out.write(',')
    f_out.write('\n')
    
    if inject_4_nops_per_instruction:
        for i in range(4):
            f_out.write(nop())
            f_out.write('\n')
    curr_addr = curr_addr + 1
    

f.close()
f_out.close()
