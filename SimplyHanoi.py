DEF PROC TowerOfHanoi(NUMBER n, CHARACTER from_rod, CHARACTER to_rod, CHARACTER aux_rod)
BEGIN
IF n = 0
BEGIN
RETURN 0
END
TowerOfHanoi(n-1, from_rod, aux_rod, to_rod)
PRINT "Move disk", n, "from rod", from_rod, "to rod", to_rod
TowerOfHanoi(n-1, aux_rod, to_rod, from_rod)
END
BEGIN

TowerOfHanoi(3, 'A', 'C', 'B')
END

