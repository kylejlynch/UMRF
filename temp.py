# -*- coding: utf-8 -*-
import pandas as pd

df = pd.DataFrame({'hey' : [1,2,3],'hi' : [1,pd.NaT,3]})

print(df['hi'].replace(pd.NaT,'time'))
