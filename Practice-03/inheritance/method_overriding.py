class Shape:
    def area(self):
        return 0

    def describe(self):
        print(f"Area: {self.area()}")

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2

r = Rectangle(4, 6)
c = Circle(5)
r.describe()
c.describe()
