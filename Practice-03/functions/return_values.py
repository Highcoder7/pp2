def add(a, b):
    return a + b

def square(x):
    return x * x

def min_max(numbers):
    return min(numbers), max(numbers)

print(add(3, 5))
print(square(7))

lo, hi = min_max([4, 1, 9, 2, 7])
print(f"Min: {lo}, Max: {hi}")
