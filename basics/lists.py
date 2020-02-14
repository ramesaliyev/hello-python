squares = [1, 4, 9, 16, 25]

print(squares)
print(squares[-1])
print(squares[:2]) # slicing
print(squares[:]) # shallow copy -- deepCopy() for deep copies

extrasquares = squares + [36, 49, 64, 81, 100]

print(extrasquares)

cubes = [1, 8, 27, 65, 125]
cubes[3] = 64
cubes.append(216)

print(cubes)

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
letters[2:5] = ['C', 'D', 'E']
letters[5:] = []

print(letters)
print(len(letters))

nested = [['a', 'b', 'c'], [1, 2, 3]]
print(nested)

print ('m' in letters)
print ('a' in letters)