BEGIN
	NUMBER temp
	NUMBER array[5]
	NUMBER i
	NUMBER j
	i := 0
	j := 0
	READ array
	WHILE i < 4
		BEGIN
        	WHILE j < 4 - i
			BEGIN
            		IF array[j] > array[j + 1]
				BEGIN
					temp := array[j]
					array[j] := array[j + 1]
					array[j + 1] := temp
				END
			j := j + 1
			END
		j := 0
		i := i + 1
		END
	PRINT array
END

