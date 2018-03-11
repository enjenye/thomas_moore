#
# sample program
#
start:
    LOAD 0x52
    ADD  0x36

    LOAD    0       # clear A
    WRITE   0

loop:
    READ    0
    DUP
    WRITE   -1
    ADD     1
    WRITE   0

    LOAD    0
inner:
    ADD     1
    DUP
    SKIP    4
    JUMP   inner
   
    DROP
    JUMP    loop

# stop
exit:
    HALT


