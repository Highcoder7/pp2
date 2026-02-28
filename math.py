import math

print("1:")
degree = float(input("degree: "))
radian = math.radians(degree)
print(f"radian: {radian:.6f}")

print("2:")
height = float(input("Height: "))
base1 = float(input("Base1: "))
base2 = float(input("Base2: "))
area = (base1 + base2) * height / 2
print(f"Output: {area}")

print("3:")
sides = int(input("number of sides: "))
length = float(input("length of a side: "))
area = (sides * length * length) / (4 * math.tan(math.pi / sides))
print(f"Area: {int(area)}")

print("4:")
base = float(input("Length of base: "))
height = float(input("Height of parallelogram: "))
area = base * height
print(f"Output: {area}")
