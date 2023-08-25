BEGIN
NUMBER rowA
NUMBER colA
NUMBER a[20, 20]
NUMBER rowB
NUMBER colB
NUMBER b[20, 20]
NUMBER i
NUMBER j
NUMBER res[20, 20]
NUMBER x
NUMBER y
NUMBER z
NUMBER fillx
NUMBER filly
NUMBER val
NUMBER comp
i := 0
j := 0
x := 0
y := 0
z := 0
fillx := 0
filly := 0
comp := 0

WHILE fillx < 5
    BEGIN
    WHILE filly < 5
        BEGIN
        res[fillx, filly] := 0
        filly := filly + 1
        END
    filly := 0
    fillx := fillx + 1
    END
PRINT " "
PRINT "Matrix A"
PRINT "========"
PRINT "Rows:"
READ rowA
PRINT " "
PRINT "Cols:"
READ colA
PRINT " "
PRINT "Values:"
WHILE i < rowA
    BEGIN
    WHILE j < colA
        BEGIN
        READ a[i, j]
        j := j + 1
        END
    j := 0
    i := i + 1
    END
PRINT " "
PRINT "Matrix B"
PRINT "========"
PRINT "Rows:"
READ rowB
PRINT " "
PRINT "Cols:"
READ colB
PRINT " "
PRINT "Values:"
i := 0
j := 0
WHILE i < rowB
    BEGIN
    WHILE j < colB
        BEGIN
            READ b[i, j]
            j := j + 1
        END
        j := 0
        i := i + 1
    END

PRINT " "
IF colA ~= rowB
BEGIN
    PRINT "Incompatible Dimensions"
    comp := 1
END
ELSE
BEGIN
    WHILE x < rowA
    BEGIN
        WHILE y < colB
        BEGIN
            WHILE z < rowB
            BEGIN
                val := a[x, z] * b[z, y]
                val := val + res[x, y]
                res[x, y] := val
                z := z + 1
            END
            z := 0
            y := y + 1
        END
        y := 0
        x := x + 1
    END
END

IF comp = 0
    BEGIN
    PRINT "A x B = "

    i := 0
    j := 0
    WHILE i < rowA
    BEGIN
        PRINT "Row ", i + 1
        WHILE j < colB
        BEGIN
            PRINT res[i, j]
            j := j + 1
        END
        PRINT "--------"
        j := 0
        i := i + 1
    END
END
END