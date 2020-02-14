def initlog(*args):
  pass   # pass does nothing

def helloworld(name = 'kamil'):
  print('hello world', name)

helloworld()
helloworld('fadime')

globalvar = 5
def wontmutate(num):
  globalvar = num
  print('local globalvar of wontmutate', globalvar)
def willmutate(num):
  global globalvar
  globalvar = num
  print('local globalvar of willmutate', globalvar)

willmutate(10)
wontmutate(3)

print('da globalvar', globalvar)

# The default value is evaluated only once.
def f(a, L=[]):
  L.append(a)
  return L

def f2(a, L=None):
  if L is None:
    L = []
  L.append(a)
  return L

print(f(1))
print(f(2))
print(f(3))

print(f2(1))
print(f2(2))
print(f2(3))

# keyword argument
def kword(a='a', b='b', c='c'):
  print(a, b, c)

kword()
kword('x', 'y', 'z')
kword(c='3', a='1', b='2')