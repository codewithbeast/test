rows = input("rows")

try:
    rows = int(rows)

except:
    print("Invalid Input")

for i in range(rows,0,-1):
    for j in range(i):
        print("*",end="")

    print("\n")
