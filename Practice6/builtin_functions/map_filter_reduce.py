from functools import reduce


nums = [1, 2, 3, 4, 5]

squares = list(map(lambda x: x * x, nums))
evens = list(filter(lambda x: x % 2 == 0, nums))
total_reduce = reduce(lambda a, b: a + b, nums, 0)

print("nums:", nums)
print("len:", len(nums))
print("sum:", sum(nums))
print("min:", min(nums))
print("max:", max(nums))
print("map (squares):", squares)
print("filter (evens):", evens)
print("reduce (sum):", total_reduce)
print("sorted desc:", sorted(nums, reverse=True))
