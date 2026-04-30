class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        print(f"{self.name} makes a sound")

class Dog(Animal):
    pass

class Cat(Animal):
    pass

d = Dog("Rex")
c = Cat("Whiskers")
d.speak()
c.speak()
