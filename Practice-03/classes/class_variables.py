class Student:
    school = "Narxoz University"
    count = 0

    def __init__(self, name, grade):
        self.name = name
        self.grade = grade
        Student.count += 1

    def info(self):
        print(f"{self.name} | Grade: {self.grade} | School: {Student.school}")

s1 = Student("Esen", "A")
s2 = Student("Aibek", "B")
s3 = Student("Aruzhan", "A")

s1.info()
s2.info()
print(f"Total students: {Student.count}")
