import re

def task1(text):
    pattern = r'ab*'
    return bool(re.search(pattern, text))

def task2(text):
    pattern = r'ab{2,3}'
    return bool(re.search(pattern, text))

def task3(text):
    pattern = r'[a-z]+_[a-z]+'
    return re.findall(pattern, text)

def task4(text):
    pattern = r'[A-Z][a-z]+'
    return re.findall(pattern, text)

def task5(text):
    pattern = r'a.*b$'
    return bool(re.search(pattern, text))

def task6(text):
    pattern = r'[ ,.]'
    return re.sub(pattern, ':', text)

def task7(text):
    words = text.split('_')
    return words[0] + ''.join(word.capitalize() for word in words[1:])

def task8(text):
    pattern = r'[A-Z][^A-Z]*'
    return re.findall(pattern, text)

def task9(text):
    pattern = r'([A-Z][a-z]+)'
    return re.sub(pattern, r' \1', text).strip()

def task10(text):
    pattern = r'([a-z])([A-Z])'
    return re.sub(pattern, r'\1_\2', text).lower()

print("Task 1:", task1("ab"))
print("Task 1:", task1("ac"))
print("Task 2:", task2("abb"))
print("Task 2:", task2("abbb"))
print("Task 3:", task3("hello_world test_case"))
print("Task 4:", task4("Hello World Test"))
print("Task 5:", task5("aanythingb"))
print("Task 5:", task5("aanythingc"))
print("Task 6:", task6("Hello, world. Test"))
print("Task 7:", task7("snake_case_string"))
print("Task 8:", task8("CamelCaseString"))
print("Task 9:", task9("CamelCaseString"))
print("Task 10:", task10("CamelCaseString"))
