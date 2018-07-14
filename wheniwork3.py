# -*- coding: utf-8 -*-
import requests
import json
import urllib.request, urllib.parse, urllib.error
import pandas as pd
import string
import numpy as np
from sensitive import wheniworktoken

### List payrolls

pd.set_option('display.max_columns', 100)

headers = wheniworktoken()
r = requests.get('https://api.wheniwork.com/2/payrolls', headers=headers)
j = r.json()
j = j['payrolls']
data = {k:[] for k,v in j[0].items()}
for i in j :
    for k,v in i.items():
        try :
            data[k].append(v)
        except : continue
df = pd.DataFrame(data)
print(df)