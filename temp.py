#stuff = dict()
#print(stuff.get('candy',-1))
import numpy as np
from sensitive import wheniworktoken
import pandas as pd
from datetime import date

r = np.arange(36).reshape((6, 6))
print(r)
print(r.reshape(36)[::7])

print(str(['Hey'][0]))

list = np.random.binomial(20,0.5,10000)
print(len(list))
print(sum((i/i) for i in list if i >= 15)/len(list))

t = np.random.binomial(1000,0.01)
print(t)
v = np.random.binomial(1,0.01,1000)
print(sum(v))

print(''.join(['h','e','y']))

import requests

headers = wheniworktoken()

r = requests.get('https://api.wheniwork.com/2/positions', headers=headers)
j = r.json()
j = j["positions"]

data = {k:[] for k,v in j[0].items()}
for i in j :
    for k,v in i.items():
        try :
            data[k].append(v)
        except : continue

df = pd.DataFrame(data)

print(df)

'''
if not (date.today().weekday() == 5 or date.today().weekday() == 6)  :
    print('hi')
'''
'''
def timeConversion(s):
    h,m,s = s.split(':')
    h = float(h.strip('0'))
    if (h == 12) & (s[2:4] == 'AM') :
        h = 00
    elif (h == 12) & (s[2:4] == 'PM') :
        h = 12
    elif s[2:4] == 'AM' :
        h = h
    elif s[2:4] == 'PM' :
        h += 12
    h= int(h)
    s = s[0:2]
    return '{0:02}:{1}:{2}'.format(h,m,s)
a = timeConversion('12:05:45AM')
print(a)
'''
'''
def factorial(n) :
    fact = 1
    for i in range(1,n+1):
        fact = fact * i
    return(fact)

def compute_numerator_of_probability(num_polys, num_sides, num_colors):
    """Computes the numerator of probability of two colored polygons having the same coloring (up to 2D rotation).
    Args:
        num_polys (int): The number of polygons in the bag.
        num_sides (int): The number of sides per polygon.
        num_colors (int): The number of possible colors.
        
    Returns:
        int: The probability multiplied by num_colors ** (2 * num_sides).
    """
    #possible = num_sides * num_colors
    possible = num_sides * int(factorial(num_colors)/factorial(num_colors - 1))
    print(possible)
    #prob = factorial(possible)/(factorial(possible - num_polys))
    prob = (1/possible)*(1/possible) + (1/possible)*(1/possible) + 0.6*(1/possible)*(1/possible)
    print(prob)
    ans = int(prob * (num_colors ** (2*num_sides)))
    return ans
a = compute_numerator_of_probability(5,6,3)
print(a)
'''