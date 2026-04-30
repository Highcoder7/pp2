class Vehicle:
    def __init__(self, brand, speed):
        self.brand = brand
        self.speed = speed

    def describe(self):
        print(f"{self.brand} | Speed: {self.speed} km/h")

class Car(Vehicle):
    def __init__(self, brand, speed, doors):
        super().__init__(brand, speed)
        self.doors = doors

    def describe(self):
        super().describe()
        print(f"  Doors: {self.doors}")

car = Car("Toyota", 180, 4)
car.describe()
