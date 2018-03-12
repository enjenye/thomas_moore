#!/usr/local/bin/python
#
# tiny assembler
#
# jan@uwinloc.com   
#
#
import sys
import json

import conf

def cnv_oper(operand, short=True):      # convert operand to instructions {{{
    # always insert lowest nybble
    v = operand & 0x0F; operand >>= 4
    out = [v]
    for i in range((conf.reg_bits/4)-1):
        # get next nybble
        n = operand & 0x0F; operand >>= 4
        # check for negative fillers
        if   short and (operand == -1) and (n == 0xF) and     (v & 0x8): break
        elif short and (operand ==  0) and (n == 0x0) and not (v & 0x8): break
        # this nybble means something : prepend and continue
        out.insert(0, n)
        v = n
    # return
    return out
# }}}

# read file
with open(sys.argv[1]) as f:
    src = f.readlines()


# parse lines
lines = [line.strip().split() for line in src]

labels = {}
variab = {}
progmem = [0]*conf.rom_size
progptr = 0
datamem = [0]*conf.mem_size
dataptr = 0

# start assembling
for lnr, line in enumerate(lines):

    # remove empty lines
    if not line: continue

    word = line[0]

    # remove comments
    if word == '#': continue

    # get labels : ends on ':'
    if word[-1] == ':':
        label = word[:-1]
        labels[label] = {'ptr':progptr, "lnr":lnr}
        continue

    # get variables : ends on '@'
    if word[-1] == '@':
        var = word[:-1]
        variab[var] = {'ptr':dataptr, "lnr":lnr}
        dataptr += 1
        continue

    # must be instruction now
    if not word in conf.mnem:
        print("error : bad instruction %s at line %d" % (word, lnr))
        continue

    # get instruction and operand mode
    inst = conf.mnem[word][0]
    mode = conf.mnem[word][1]

    # check for argument
    if len(line) > 1:
        arg = line[1]

        # parse operands (and labels)
        if arg in labels:
            operand = labels[arg]['ptr']
        elif arg in variab:
            operand = variab[arg]['ptr']
        else:
            operand = int(arg, 0)

        # check for 'ORG'
        if inst == -1:  
            progptr = operand
            continue

        # check for relative arguments
        if mode == 'rela': 
            operand -= progptr + 3
            cnv_op = cnv_oper(operand, short=False)
        else:
            cnv_op = cnv_oper(operand)

        # output operand
        for v in cnv_op:
            progmem[progptr] = 0x10 | v
            progptr += 1

    # output instruction
    progmem[progptr] = inst
    progptr += 1


print "LABELS", labels
print "VARIABLES", variab
print "PROG"
print [hex(i) for i in progmem]

# save
with open(sys.argv[2], 'w') as f:
    json.dump((labels, progmem), f)




