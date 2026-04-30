class Flyable:
    def fly(self):
        print(f"{self.name} is flying")

class Swimmable:
    def swim(self):
        print(f"{self.name} is swimming")

class Duck(Flyable, Swimmable):
    def __init__(self, name):
        self.name = name

    def quack(self):
        print(f"{self.name} says: Quack!")

donald = Duck("Donald")
donald.fly()
donald.swim()
donald.quack()

print(Duck.__mro__)
