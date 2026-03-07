names = ["Ann", "Bob", "Cate"]
ages = [20, 30, 25]

print("enumerate:")
for i, name in enumerate(names):
    print(i, name)

print("zip:")
for name, age in zip(names, ages):
    print(name, age)

pairs = list(zip(names, ages))
sorted_by_age = sorted(pairs, key=lambda t: t[1])

print("pairs:", pairs)
print("sorted_by_age:", sorted_by_age)

s = "123"
n = int(s)
f = float("3.5")
text = str(99)
tup = tuple([1, 2, 3])
lst = list(tup)
st = set([1, 1, 2])
dct = dict([("a", 1), ("b", 2)])

print("type(n):", type(n))
print("type(f):", type(f))
print("type(dct):", type(dct))
print("isinstance(n, int):", isinstance(n, int))
print("conversions:", n, f, text, tup, lst, st, dct)
