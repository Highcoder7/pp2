class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.area = width * height

p1 = Person("Esen", 21)
p2 = Person("Aibek", 25)
print(p1.name, p1.age)
print(p2.name, p2.age)

rect = Rectangle(5, 3)
print(f"Area: {rect.area}")
