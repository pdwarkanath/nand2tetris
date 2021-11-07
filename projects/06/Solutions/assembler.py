import json
import re
import os
from argparse import ArgumentParser

ap = ArgumentParser()

ap.add_argument("-f", "--filename", required=True, help="Name of the symbolic machine instructions (.asm) file . eg. Max.asm")
args = vars(ap.parse_args())
asm_file = args['filename']

with open('symbol_table.json') as f:
    symbol_table = json.load(f)
with open('c_instructions.json') as f:
    c_instructions = json.load(f)
with open('d_table.json') as f:
    d_table = json.load(f)
with open('j_table.json') as f:
    j_table = json.load(f)


def first_pass(f):
    line_number = 0
    for line in f:
        line = re.sub('\s+', '', line) # remove whitespace
        line = re.sub('\/\/.*', '', line) # remove comments
        if len(line) > 0:
            if line[0] == '(':
                if line[1:-1] not in symbol_table:
                    symbol_table[line[1:-1]] = line_number
            else:
                line_number += 1

with open(asm_file) as f:
    first_pass(f)

curr_addr = 16

def read_a_instruction(line):
    addr = line[1:]
    try:
        a = int(addr)
    except ValueError:
        if addr not in symbol_table:
            global curr_addr
            symbol_table[addr] = curr_addr
            curr_addr += 1
        a = symbol_table[addr]
    return f'{int(bin(a)[2:]):016d}\n'

def read_c_instruction(line):
    c_instr = line.split(';')
    if len(c_instr) > 1:
        j = c_instr[1]
    else:
        j = '0'
    
    c_instr = c_instr[0].split('=')
    if len(c_instr) > 1:
        d = ''.join(sorted(c_instr[0]))
        c = c_instr[1]
    else:
        d = '0'
        c = c_instr[0]
    
    return '111' + c_instructions[c]['a'] + c_instructions[c]['c'] + d_table[d] + j_table[j] + '\n'

def second_pass(f):
    hack_file = asm_file[:-4] + '.hack'
    if os.path.exists(hack_file):
        os.remove(hack_file)
    line_number = 0
    instr = ''
    for line in f:
        line = re.sub('\s+', '', line) # remove whitespace
        line = re.sub('\/\/.*', '', line) # remove comments
        if len(line) > 0:
            if line[0] == '(':
                continue
            elif line[0] == '@':
                instr += read_a_instruction(line)
                line_number += 1
            else:
                instr += read_c_instruction(line)
                line_number += 1
            if line_number == 10:
                line_number = 0
                with open(hack_file, 'a+') as h:
                    h.write(instr)
                instr = ''
    with open(hack_file, 'a+') as h:
        h.write(instr)

with open(asm_file) as f:
    second_pass(f)