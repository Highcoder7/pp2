numbers = [1, 2, 3, 4, 5]

squares = list(map(lambda x: x ** 2, numbers))
print(squares)

words = ["hello", "world", "python"]
upper = list(map(lambda w: w.upper(), words))
print(upper)
