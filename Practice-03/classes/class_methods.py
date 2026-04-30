class Circle:
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2

    def perimeter(self):
        return 2 * 3.14159 * self.radius

    def describe(self):
        print(f"Circle with radius {self.radius}")
        print(f"  Area: {self.area():.2f}")
        print(f"  Perimeter: {self.perimeter():.2f}")

c = Circle(7)
c.describe()
