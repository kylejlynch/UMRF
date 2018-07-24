# -*- coding: utf-8 -*-
import requests
import json
import sqlite3
import pandas as pd
import string
import numpy as np
from sensitive import wheniworktoken

'''
Obtains and stores employee info in an SQL database:
UMRF ID, FedEx ID, First Name, Last Name, Location, Position, Hourly Pay Rate,
Phone Number, Email
Generates Excel document
'''
pd.set_option('display.max_columns', 100)

headers = wheniworktoken()
r = requests.get('https://api.wheniwork.com/2/users', headers=headers)
j = r.json()
j = j["users"]

data = {k:[] for k,v in j[0].items()}
for i in j :
    for k,v in i.items():
        try :
            data[k].append(v)
        except : continue

df = pd.DataFrame(data)
print(df.head(20))
df = df.filter(['id','employee_code','first_name','last_name','locations','positions','role','hourly_rate','phone_number','email'])
df = df[~(df['locations'].str.len() > 1)].drop(columns = ['locations'])
df = df[(df['positions'].str.len() >= 1)]

df = df[~(df['positions'].str[0] == 5985624)].reset_index(drop=True)

df['position'] = df['positions'].str[1].replace({5806257 : 'Supervisor',
                                                  8412757 : 'Shift Lead',
                                                  8569433 : 'Supervisor',
                                                  8569434 : 'Shift Lead',
                                                  np.nan : 'Agent'})

df['location'] = df['positions'].str[0].replace({8457625 : 'Lambuth',
                                                  5806250 : 'Memphis',
                                                  5985624 : np.nan})
df = df.drop(columns = ['positions'])
#print(df.head(20))

letters = list(string.ascii_uppercase)
writer = pd.ExcelWriter('emplist.xlsx')
df.to_excel(writer,'Sheet1')
worksheet = writer.sheets['Sheet1']
for i,col in enumerate(list(df)) :    #autofit column-width
    worksheet.set_column('{}:{}'.format(letters[i+1],letters[i+1]), max(len(col)+2,df['{}'.format(col)].astype(str).map(len).max()+2))
writer.save()

conn = sqlite3.connect('emplist.sqlite')
df.to_sql('info', conn)

conn.commit()
conn.close()