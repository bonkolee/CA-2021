from process_file import InstructionParser
import pandas as pd

class Simulator(object):
    def __init__(self, memory, instr_set, NF, NW, NR, NB):
        self.NF = NF
        self.NW = NW
        self.NR = NR
        self.NB = NB
        self.memory = memory
        self.cycle = 0
        self.registers = dict([("R%s" % x, 0) for x in range(32)] + [("F%s" % x, 0) for x in range(32)] + [("$0", 0)])
        self.instr_set = instr_set
        self.bfr = 0
        index = ["INT1","INT2","INT3","INT4","LOAD1","LOAD2","STORE1","STORE2","FPadd1","FPadd2","FPadd3",
                 "FPmult1","FPmult2","FPmult3","FPmult4","FPdiv1","FPdiv2","BU"]
        self.reservation_columns = ["Busy", "Op", "Vj", "Vk", "Qj", "Qk", "Dest"]
        self.reservation = pd.DataFrame([[False] + [None]*6]*18, index=index, columns=self.reservation_columns)
        # index = ["ROB%s" % x for x in range(1, self.NR + 1)]
        self.ROB_columns = ["id","Busy", "Instruction", "State", "Dest", "value", "Unit"]
        self.ROB = []
        self.fetch_queue = []
        self.decode_queue = []
        self.cycles = {'add': 1, 'addi': 1, 'fld': 1, 'fsd': 1, 'fadd': 3, 'fsub': 3, 'fmul': 4, 'fdiv': 8, 'bne': 1}
        self.total_cycle = 0
        self.CDB = {}
        self.id = 0
        self.BTB = {}

    def run(self):

        while True:
            self.total_cycle += 1
            print('cycle:', self.total_cycle)

            # Simulation
            self.execute()
            self.issue()
            self.decode()
            self.fetch()

            print('fetch queue')
            for i in self.fetch_queue:
                print(i)
            print('decode queue')
            for i in self.decode_queue:
                print(i)
            print('reservation station')
            print(self.reservation_columns)
            for indexs in self.reservation.index:
                print(indexs, self.reservation.loc[indexs].values)
            print('ROB status')
            for i in self.ROB:
                print(i)
            if len(self.ROB) == 0 and len(self.fetch_queue) == 0 and len(self.decode_queue) == 0:
                break
            print('memory')
            print(self.memory)
            print('registers(value!=0)')
            for k, v in self.registers.items():
                if v != 0:
                    print((k, v), end=' ')
            print()
            print('CDB')
            print(self.CDB)
            print()

    def fetch(self):
        '''
        fetch the operations
        :return:
        '''
        for i in range(self.NF):
            if self.bfr == len(self.instr_set):
                return None
            self.fetch_queue.append(self.instr_set[self.bfr])
            if self.bfr in self.BTB:
                if self.BTB[self.bfr][1]:
                    self.bfr = self.BTB[self.bfr][0]
                else:
                    self.bfr += 1
            else:
                self.bfr += 1

    def decode(self):
        '''
        decode the operations
        :return:
        '''
        for i in range(len(self.fetch_queue)):
            temp = self.fetch_queue.pop(0)
            self.decode_queue.append(temp)
            if temp.op == 'bne' and temp.address not in self.BTB:
                self.BTB[temp.address] = [temp.target, False]

    def issue(self):
        '''
        put the operations in reservation station
        :return:
        '''
        unit = None
        for i in range(self.NW):
            if len(self.ROB) == self.NR:
                return None
            if len(self.decode_queue) == 0:
                return None
            temp = self.decode_queue[0]
            if temp.op == 'add' or temp.op == 'addi':
                if self.reservation.loc['INT1', 'Busy'] == False:
                    unit = 'INT1'
                elif self.reservation.loc['INT2', 'Busy'] == False:
                    unit = 'INT2'
                elif self.reservation.loc['INT3', 'Busy'] == False:
                    unit = 'INT3'
                elif self.reservation.loc['INT4', 'Busy'] == False:
                    unit = 'INT4'
                else:
                    return None
            elif temp.op == 'fld':
                if self.reservation.loc['LOAD1', 'Busy'] == False:
                    unit = 'LOAD1'
                elif self.reservation.loc['LOAD2', 'Busy'] == False:
                    unit = 'LOAD2'
                else:
                    return None
            elif temp.op == 'fsd':
                if self.reservation.loc['STORE1', 'Busy'] == False:
                    unit = 'STORE1'
                elif self.reservation.loc['STORE2', 'Busy'] == False:
                    unit = 'STORE2'
                else:
                    return None
            elif temp.op == 'fadd' or temp.op == 'fsub':
                if self.reservation.loc['FPadd1', 'Busy'] == False:
                    unit = 'FPadd1'
                elif self.reservation.loc['FPadd2', 'Busy'] == False:
                    unit = 'FPadd2'
                elif self.reservation.loc['FPadd3', 'Busy'] == False:
                    unit = 'FPadd3'
                else:
                    return None
            elif temp.op == 'fmul':
                if self.reservation.loc['FPmult1', 'Busy'] == False:
                    unit = 'FPmult1'
                elif self.reservation.loc['FPmult2', 'Busy'] == False:
                    unit = 'FPmult2'
                elif self.reservation.loc['FPmult3', 'Busy'] == False:
                    unit = 'FPmult3'
                elif self.reservation.loc['FPmult4', 'Busy'] == False:
                    unit = 'FPmult4'
                else:
                    return None
            elif temp.op == 'fdiv':
                if self.reservation.loc['FPdiv1', 'Busy'] == False:
                    unit = 'FPdiv1'
                elif self.reservation.loc['FPdiv2', 'Busy'] == False:
                    unit = 'FPdiv2'
                else:
                    return None
            elif temp.op == 'bne':
                if self.reservation.loc['BU', 'Busy'] == False:
                    unit = 'BU'
                else:
                    return None
            self.decode_queue.pop(0)
            self.reservation.loc[unit, 'Busy'] = True
            self.reservation.loc[unit, 'Op'] = temp.op
            # if len(self.ROB) == 0:
            #     self.reservation.loc[unit, 'Dest'] = 1
            # else:
            self.id += 1
            self.reservation.loc[unit, 'Dest'] = self.id
            if temp.rs1 is not None:
                for i in reversed(self.ROB):
                    if i['Dest'] == temp.rs1 and i['State'] != 'Commit' and i['State'] != 'Wrote result':
                        self.reservation.loc[unit, 'Qj'] = i['id']
                        break
                    if i['Dest'] == temp.rs1 and (i['State'] == 'Commit' or i['State'] == 'Wrote result'):
                        self.reservation.loc[unit, 'Vj'] = i['Dest'] + ',' + str(i['id'])
                        break
                else:
                    self.reservation.loc[unit, 'Vj'] = temp.rs1
            if temp.rs2 is not None:
                for i in reversed(self.ROB):
                    if i['Dest'] == temp.rs2 and i['State'] != 'Commit' and i['State'] != 'Wrote result':
                        self.reservation.loc[unit, 'Qk'] = i['id']
                        break
                    if i['Dest'] == temp.rs2 and (i['State'] == 'Commit' or i['State'] == 'Wrote result'):
                        self.reservation.loc[unit, 'Vk'] = i['Dest'] + ',' + str(i['id'])
                        break
                else:
                    self.reservation.loc[unit, 'Vk'] = temp.rs2
            self.ROB.append(dict([i for i in zip(self.ROB_columns, [self.reservation.loc[unit, 'Dest'], True, temp, 'Issue', temp.rd, None, unit])]))

    def execute(self):
        '''
        execute
        :return:
        '''
        count_WB = 0
        is_M = False
        for i in self.ROB:
            if i['State'] == 'Wrote result':
                # if i['Instruction'].op != 'fsd' or i['Instruction'].op != 'bne':
                i['State'] = 'Commit'
            elif i['State'] == 0 or i['State'] == 'M':
                if (i['Instruction'].op == 'fsd' or i['Instruction'].op == 'fld') and i['State'] == 0:
                    if not is_M:
                        is_M = True
                        i['State'] = 'M'
                        continue
                    else:
                        continue
                if count_WB == self.NB:
                    continue
                count_WB += 1
                i['State'] = 'Wrote result'
                if isinstance(i['value'], int) and not isinstance(i['value'], bool):
                    self.CDB[i['Dest'] +','+ str(i['id'])] = i['value']
                if isinstance(i['value'], bool):
                    if self.BTB[i['Instruction'].address][1] == i['value']:
                        pass
                    elif i['value']:
                        self.BTB[i['Instruction'].address][1] = i['value']
                        self.bfr = self.BTB[i['Instruction'].address][0]
                    elif not i['value']:
                        self.BTB[i['Instruction'].address][1] = i['value']
                        self.bfr = i['Instruction'].address + 1
                        self.fetch_queue.clear()
                        self.decode_queue.clear()
                        for index, value in enumerate(self.ROB):
                            if value['id'] > i['id']:
                                flush_ROB = self.ROB[index:]
                                for flush_i in flush_ROB:
                                    self.reservation.loc[flush_i['Unit']] = [False] + [None]*6
                                self.ROB = self.ROB[0:index]
                                break


                for indexs in self.reservation.index:
                    if self.reservation.loc[indexs, 'Qj'] == i['id']:
                        self.reservation.loc[indexs, 'Vj'] = i['Dest'] + ',' + str(self.reservation.loc[indexs, 'Qj'])
                        self.reservation.loc[indexs, 'Qj'] = None
                    if self.reservation.loc[indexs, 'Qk'] == i['id']:
                        self.reservation.loc[indexs, 'Vk'] = i['Dest'] + ',' + str(self.reservation.loc[indexs, 'Qk'])
                        self.reservation.loc[indexs, 'Qk'] = None
            elif i['State'] == 'Issue':
                if (self.reservation.loc[i['Unit'], 'Qj'] is None and self.reservation.loc[i['Unit'], 'Qk'] is None):
                    i['State'] = self.cycles[i['Instruction'].op] - 1
                    i['value'] = self.get_value(i)

            elif i['State'] == 'Commit':
                pass
            else :
                # print(i['State'])
                i['State'] -= 1

        if len(self.ROB) != 0:
            if self.ROB[0]['State'] == 'Commit':
                temp = self.ROB.pop(0)
                self.reservation.loc[temp['Unit']] = [False] + [None]*6
                if temp['Instruction'].op == 'fsd':
                    self.memory[temp['value'][1]] = temp['value'][0]
                elif temp['Instruction'].op == 'bne':
                    pass
                #     if temp['value']:
                #         self.bfr = temp['Instruction'].target
                else:
                    self.registers[temp['Dest']] = temp['value']
                    # if
                    # self.registers[temp['Dest']] = self.CDB.pop(temp['Dest'])

    def get_value(self, item):
        temp_Vj = None
        temp_Vk = None
        instr = item['Instruction']

        if self.reservation.loc[item['Unit'], 'Vj'] in self.CDB:
            temp_Vj = self.CDB[self.reservation.loc[item['Unit'], 'Vj']]
        if self.reservation.loc[item['Unit'], 'Vk'] in self.CDB:
            temp_Vk = self.CDB[self.reservation.loc[item['Unit'], 'Vk']]

        if temp_Vj is None:
            temp_Vj = self.registers[instr.rs1]
        if temp_Vk is None:
            if instr.rs2 is not None:
                temp_Vk = self.registers[instr.rs2]

        if instr.op == 'addi':
            return temp_Vj + instr.imm
        elif instr.op == 'add' or instr.op == 'fadd':
            return temp_Vj + temp_Vk
        elif instr.op == 'fsub':
            return temp_Vj - temp_Vk
        elif instr.op == 'fmul':
            return temp_Vj * temp_Vk
        elif instr.op == 'fdiv':
            return temp_Vj * 1.0 / temp_Vk
        elif instr.op == 'fld':
            return self.memory[temp_Vj + instr.imm]
        elif instr.op == 'fsd':
            return temp_Vj, temp_Vk + instr.imm
        elif instr.op == 'bne':
            return temp_Vj != temp_Vk

def read_memory(filepath):
    result = {}
    with open(filepath, 'r') as f:
        data = filter((lambda x: x != '\n'), f.readlines())
        for i in data:
            a, b = i.replace(',', '').split()
            result[int(a)] = int(b)
        return result

