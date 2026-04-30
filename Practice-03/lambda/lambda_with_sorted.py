numbers = [5, 2, 8, 1, 9, 3]
sorted_asc = sorted(numbers, key=lambda x: x)
sorted_desc = sorted(numbers, key=lambda x: -x)
print(sorted_asc)
print(sorted_desc)

people = [("Alice", 30), ("Bob", 25), ("Charlie", 35)]
by_age = sorted(people, key=lambda p: p[1])
print(by_age)

words = ["banana", "apple", "cherry", "fig"]
by_length = sorted(words, key=lambda w: len(w))
print(by_length)
