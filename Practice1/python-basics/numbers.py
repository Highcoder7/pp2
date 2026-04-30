x = 1    
y = 25.9  
z = 8j   


print(type(x))
print(type(y))
print(type(z))

#int

x = 1
y = 35656258
z = -325

print(type(x))
print(type(y))
print(type(z))

#float

x = 6.25
y = 897.5
z = -23698.59

print(type(x))
print(type(y))
print(type(z))

x = 38e3
y = 12E5
z = -87.7e1000

print(type(x))
print(type(y))
print(type(z))

#complex

x = 3-9j
y = 8j
z = -2j

print(type(x))
print(type(y))
print(type(z))

#type conversion

x = 8   
y = 2.896  
z = -81j   


a = float(x)


b = int(y)


c = complex(x)

print(a)
print(b)
print(c)

print(type(a))
print(type(b))
print(type(c))


#random

import random

print(random.randrange(1, 256))