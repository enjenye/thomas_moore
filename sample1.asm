#
# sample program
#
start:
    LOAD 0x52
    ADD  0x36

    LOAD    0       # clear A
loop:
    WRITE   -1
    ADD     1
    DUP     
    ADD     -10
    SKIP    4 
    JUMP    loop

# stop
exit:
    HALT


