# -*- coding: utf-8 -*-
import pandas as pd

df = pd.DataFrame({'hey' : [1,2,3],'hi' : [1,pd.NaT,3]})

print(df['hi'].replace(pd.NaT,'time'))

print(pd.date_range(start='2018-01-01 07:00:00', end='2018-02-01 20:00:00', freq='30T').astype('str'))

print(np.sort(5 * np.random.rand(40, 1)))