#1
x = "great language code"

def myfunc1():
  print("Python is " + x)

myfunc1()

#2
x = "great language code"

def myfunc():
  x = "awesome"
  print("Python is " + x)

myfunc()

print("Python is " + x)

#3

def myfunc():
  global x
  x = "great language code"

myfunc()

print("Python is " + x)

#4

x = "great language code"

def myfunc():
  global x
  x = "awesome"

myfunc()

print("Python is " + x)