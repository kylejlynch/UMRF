#stuff = dict()
#print(stuff.get('candy',-1))
import numpy as np
from sensitive import wheniworktoken
import pandas as pd

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