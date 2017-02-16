import cs50
while True:
    print("Height: ", end = '')
    n=cs50.get_int()
    if (n >= 0):
        break
n +=1    
for i in range(1,n):
    print(" " * (n-i-1) + "#" * i + "  " + "#" * i)
        