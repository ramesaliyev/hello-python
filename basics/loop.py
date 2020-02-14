a = 5
while a > 0:
  print(a)
  a-=1

print('---') # separator

words = ['cat', 'window', 'defenestrate']
for w in words:
  print(w, len(w))

print('---') # separator

for i in range(5):
  print(i)

print('---') # separator

for i in range(3,10):
  print(i)

print('---') # separator

for i in range(3,10, 3):
  print(i)

print('---') # separator

a = ['Mary', 'had', 'a', 'little', 'lamb']
for i in range(len(a)): # use enumarete instead
  print(i, a[i])

print('---') # separator

for i, v in enumerate(a):
  print(i, v)

print('---') # separator

print(sum(range(4)))

print('---') # separator

for n in range(2, 10):
  for x in range(2, n):
    if n % x == 0:
      print(n, 'equals', x, '*', n//x)
      break
  else: # a loop’s else clause runs when no break occurs.
    # loop fell through without finding a factor
    print(n, 'is a prime number')

print('---')

for num in range(2, 10):
  if num % 2 == 0:
    print("Found an even number", num)
    continue
  print("Found a number", num)