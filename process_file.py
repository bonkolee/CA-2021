"""
Instructions to support:

R-Type Instructions [add, fadd, fsub, fmul, fdiv]
funct7(7) rs2(5) rs1(5) funct3(3) rd(5) opcode(7)
funct5(5) fmt(2) rs2(5) rs1(5) funct3(3) rd(5) opcode(7)
I-Type Instructions [addi, fld, fsd]
imm(12) rs1(5) funct3(3) rd(5) opcode(7)
imm(12) rs1(5) funct3(3) rd(5) opcode(7)
imm(7) rs2(5) rs1(5) width(3) imm(5) opcode(7)
B-Type Instructions [bne]
imm[12](1) imm[10:5](6) rs2(5) rs1(5) funct3(3) imm[4:1](4) imm[11](1) opcode(7)

instr - type of instruction
op - operation
rs - source register
rt - transition register
rd - destination register
sa (shamt) - shift amount
target - target address
func - function
"""

class Instruction(object):
    def __init__(self, **input):
        self.values = {
            'op': None,
            'rd': None,
            'rs1': None,
            'rs2': None,
            'imm': None,
            'target': None,
            'address': None
        }

        for key in input:
            if key in self.values.keys():
                self.values[key] = input[key]

    @property
    def op(self):
        """ Get this Instruction's name """
        return self.values['op']

    @property
    def rd(self):
        """ Get this Instruction's destination register """
        return self.values['rd']

    @property
    def rs1(self):
        """ Get this Instruction's first source register """
        return self.values['rs1']

    @property
    def rs2(self):
        """ Get this Instruction's second source register """
        return self.values['rs2']

    @property
    def imm(self):
        """ Get this Instruction's immediate value """
        return self.values['imm']

    @property
    def target(self):
        """ Get this Instruction's target value """
        return self.values['target']

    @property
    def address(self):
        """ Get this Instruction's target value """
        return self.values['address']



    def __str__(self):
        if self.op in ['addi']:
            return '%#x %s\t%s %s %s' % (self.address*4, self.op, self.rd, self.rs1, self.imm)
        if self.op in ['fld']:
            return '%#x %s \t%s %s %s' % (self.address*4, self.op, self.rd, self.rs1, self.imm)
        if self.op in ['fsd']:
            return '%#x %s \t%s %s %s' % (self.address*4, self.op, self.rs1, self.rs2, self.imm)
        if self.op in ['add', 'fadd', 'fsub', 'fmul', 'fdiv']:
            return '%#x %s \t%s %s %s' % (self.address*4, self.op, self.rd, self.rs1, self.rs2)
        if self.op in ['bne']:
            return '%#x %s \t%s %s %#x' % (self.address*4, self.op, self.rs1, self.rs2, self.target*4)

    def __repr__(self):
        return repr(self.values)

class InstructionParser(object):
    def __init__(self):
        self.instructionSet = {
            'rtype': ['add', 'fadd', 'fsub', 'fmul', 'fdiv'],
            'itype': ['addi', 'fld', 'fsd'],
            'btype': ['bne']
        }
        self.mark = {}
        self.count = -1

    def parseFile(self, filename):
        with open(filename) as f:
            data = filter((lambda x: x != '\n'), f.readlines())

            instructions = [self.parse(a[1].replace(',', ' '), a[0]) for a in enumerate(data)]
            return instructions

    def parse(self, s, no):
        s = s.split()
        if ':' in s[0]:
            self.mark[s.pop(0).replace(':', '')] = no
        instr = s[0]
        self.count += 1
        if instr in self.instructionSet['rtype']:
            return self.createRTypeInstruction(s)
        elif instr in self.instructionSet['itype']:
            return self.createITypeInstruction(s)
        elif instr in self.instructionSet['btype']:
            return self.createBTypeInstruction(s)
        else:
            raise ParseError("Invalid parse instruction")

    def createRTypeInstruction(self, s):
        return Instruction(op=s[0], rd=s[1], rs1=s[2], rs2=s[3], address=self.count)

    def createITypeInstruction(self, s):
        if s[0] == "addi":
            return Instruction(op=s[0], rd=s[1], rs1=s[2], imm=int(s[3]), address=self.count)
        temp = s[2].replace(')', '').split('(')
        if s[0] == "fld":
            return Instruction(op=s[0], rd=s[1], rs1=temp[1], imm=int(temp[0]), address=self.count)
        else:
            return Instruction(op=s[0], rs1=s[1], rs2=temp[1], imm=int(temp[0]), address=self.count)

    def createBTypeInstruction(self, s):
        return Instruction(op=s[0], rs1=s[1], rs2=s[2], target=self.mark[s[3]], address=self.count)


class ParseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

if __name__ == '__main__':
    a = InstructionParser()
    set = a.parseFile('benchmark')
    for i in set:
        print(i)

    # print(set)