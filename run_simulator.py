from Simulator import *

if __name__ == '__main__':
    # configuration
    f = open('config', 'r')
    config = {}
    temp = f.readline()
    while temp:
        temp = temp.split()
        config[temp[0]] = int(temp[1])
        temp = f.readline()
    print(config)
    # memory
    memory_content = read_memory('memory')
    # read operations file
    parser = InstructionParser()
    set = parser.parseFile('benchmark')
    # create a Simulator
    a = Simulator(memory_content, set, NF=config['NF'], NW=config['NW'], NR=config['NR'], NB=config['NB'])
    a.run()