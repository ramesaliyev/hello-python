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

# keywords & arguments
def magics(a, *arguments, **keywords):
    print(a)
    for arg in arguments:
        print('arg', arg)
    print("-" * 40)
    for kw in keywords:
        print('kw', kw, ":", keywords[kw])

magics('1', '2', '3', _4='4', _5='5')

# def f(pos1, pos2, /, pos_or_kwd, *, kwd1, kwd2):
def standard_arg(arg):
  print(arg)

def pos_only_arg(arg, /):
  print(arg)

def kwd_only_arg(*, arg):
  print(arg)

def combined_example(pos_only, /, standard, *, kwd_only):
  print(pos_only, standard, kwd_only)