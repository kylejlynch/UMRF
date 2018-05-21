import pandas as pd
import numpy as np
import os
import re
from bs4 import BeautifulSoup
import email
from datetime import date
import calendar

def convtime(t) :
    h,m,s = re.split(':',t)
    _hrs = int(h) + int(m)/60 + int(s)/3600
    _min = int(h)*60 + int(m) + int(s)/60
    return '{:.3f}'.format(_hrs),'{:.3f}'.format(_min)

df = pd.DataFrame()
datelist = []

path = 'Call Patterns/'
listing = os.listdir(path)
for file in listing :
    fh = open(os.path.join(path,file), 'rb')
    handle = email.message_from_string(fh.read().decode())
    if handle.is_multipart() :
        for part in handle.walk() :
            if part.get_content_type() == 'text/html' :
               emlhtml = part.get_payload(decode=True).decode()
    else :
        emlhtml = handle.get_payload()
               
    #extract data
    soup = BeautifulSoup(emlhtml, 'lxml')
    dates = soup.find_all('b')[-1]
    dt = dates.text[49:59]
    year, day, month = dt.split('-')
    day = calendar.day_name[calendar.weekday(int(year), int(day), int(month))]
    if not dt in datelist :
        datelist.append(dt)
    else : continue
    #prep/clean data
    correcthtml = re.findall(r'<p class="MsoNormal"><span style="mso-bookmark:_MailOriginal">'r'[0-9]+'r'<o:p></o:p></span></p>'r'[\s]+'r'(<p class="MsoNormal"><span style="mso-bookmark:_MailOriginal">'r'[0-9]+'r'<o:p></o:p></span></p>'r'[\s]+)',emlhtml)
    for i,string in enumerate(correcthtml) :
        emlhtml = re.sub(r'(<p class="MsoNormal"><span style="mso-bookmark:_MailOriginal">'r'[0-9]+'r'<o:p></o:p></span></p>'r'[\s]+)'r'(<p class="MsoNormal"><span style="mso-bookmark:_MailOriginal">'r'[0-9]+'r'<o:p></o:p></span></p>'r'[\s]+)',r'\1' + r'</td>\r\n<span style="mso-bookmark:_MailOriginal"></span>\r\n<td style="padding:.75pt .75pt .75pt .75pt">\r\n' + correcthtml[i], emlhtml)
        emlhtml = re.sub(r'<td style="border:none;padding:.75pt .75pt .75pt .75pt"><span style="mso-bookmark:_MailOriginal"></span></td>\r\n<span style="mso-bookmark:_MailOriginal"></span>'r'[\s]+',r'',emlhtml)
    dfraw = pd.read_html(emlhtml,header=0)[0]
    dfraw = dfraw.iloc[14:40]
    dfraw.replace({'! ':'','!':'','< /td>':'','<tr>':'','< td>':'','< tr>':''}, regex=True,inplace=True)
    if dfraw.isnull().values.any() :
        continue
    if not 'Overflow Calls' in dfraw :
        dfraw['Overflow Calls'] = dfraw['Calls Offered'].astype('float') - dfraw['ACD Calls'].astype('float')
    dfraw = dfraw[['Time Interval','Overflow Calls']].set_index('Time Interval')
    dfclean = dfraw['Overflow Calls'].astype('str').replace({'[^0-9.]*':''}, regex=True).reset_index()
    dfclean['Day'] = day
    df = df.append(dfclean)

df = df.apply(pd.to_numeric, errors='ignore')
dfavg = df.groupby(['Day','Time Interval'],sort=False)['Overflow Calls'].mean().round(2)

writer = pd.ExcelWriter('Avg_Overflow.xlsx')
dfavg.to_excel(writer,'Sheet1')
writer.save()