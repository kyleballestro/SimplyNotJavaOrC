DEF PROC partition(NUMBER arr, NUMBER low, NUMBER high)
BEGIN
        NUMBER pivot
	NUMBER i
	NUMBER j
	NUMBER temp
	pivot := arr[high]
	i := low - 1
	j := low
        WHILE j < high
        	BEGIN
            	IF arr[j] <= pivot
            		BEGIN
                	i := i + 1
 			temp := arr[i]
                	arr[i] := arr[j]
                	arr[j] := temp
            		END
		j := j + 1
        	END
 
        temp := arr[i+1]
        arr[i+1] := arr[high]
        arr[high] := temp
 	i := i + 1
        RETURN i
END
 
DEF PROC sort(NUMBER arr, NUMBER low, NUMBER high)
BEGIN
	NUMBER pi
	IF low < high
        BEGIN
        	pi := partition(arr, low, high)
                sort(arr, low, pi-1)
                sort(arr, pi+1, high)
        END
END
 
BEGIN
        NUMBER arr[5]
        NUMBER n
	n := 4
	READ arr
        sort(arr, 0, n)
 	PRINT arr
END