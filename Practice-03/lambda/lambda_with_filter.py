numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)

words = ["apple", "banana", "avocado", "cherry", "apricot"]
a_words = list(filter(lambda w: w.startswith("a"), words))
print(a_words)
