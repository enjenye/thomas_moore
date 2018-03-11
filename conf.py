opc_bits = 5
reg_bits = 12
rom_bits = 6

reg_size = 2**(reg_bits-1)
mem_size = 2**(reg_bits  )
rom_size = 2**(rom_bits)

mnem = {    # ID    arg
    'NOT'   : ( 0, 'none'),
    'NEG'   : ( 1, 'none'),
    'SHL'   : ( 2, 'none'),
    'SHR'   : ( 3, 'none'),
    'DROP'  : ( 4, 'none'),
    'DUP'   : ( 5, 'none'),
    'OVER'  : ( 6, 'none'),
    'XOR'   : ( 7, 'data'),
    'AND'   : ( 8, 'data'),
    'ADD'   : ( 9, 'data'),
    'READ'  : (10, 'addr'),
    'WRITE' : (11, 'addr'),
    'CALL'  : (12, 'addr'),
    'JUMP'  : (13, 'rela'),
    'SKIP'  : (14, 'data'),
    'HALT'  : (15, 'none'),

    'LOAD'  : ( 5, 'data')
}
