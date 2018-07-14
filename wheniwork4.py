# -*- coding: utf-8 -*-
import requests
import json
import urllib.request, urllib.parse, urllib.error
import pandas as pd
import string
import numpy as np
from sensitive import wheniworktoken

'''
0   5577672     1950209    20512956  Sat, 09 Jun 2018 00:00:00 -0500   
1   5577667     1950209    20512956  Sat, 26 May 2018 00:00:00 -0500 
'''
### Specific payroll

pd.set_option('display.max_columns', 100)

headers = wheniworktoken()
r = requests.get('https://api.wheniwork.com/2/payrolls/5577667', headers=headers)
j = r.json()
j = j['payrollhours']
data = {k:[] for k,v in j[0].items()}
for i in j :
    for k,v in i.items():
        try :
            data[k].append(v)
        except : continue
df = pd.DataFrame(data)
print(df)