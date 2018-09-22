# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 00:56:59 2018

@author: Labuser
"""

import imaplib, email
import sqlite3
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os
import re
from datetime import date,datetime,timedelta
import calendar
from sensitive import emailcredentials
from custom_functions import get_body,search,get_emails,convtime
from io import StringIO

pd.set_option('display.max_columns', 100)
#pd.set_option('display.max_rows', 400)

def agentdailycsv() :
    conn = sqlite3.connect('UMRF_Incidents_SQL.sqlite')
    conn2 = sqlite3.connect('UMRF_SQL_Daily.sqlite')
    conn3 = sqlite3.connect('emplistmanual.sqlite')
    
    user, password, imap_url = emailcredentials()
    mail = imaplib.IMAP4_SSL(imap_url)
    mail.login(user,password)
    mail.select('"Agent Daily"')
    
    dfemp = pd.DataFrame(columns = ['FirstName','LastName'])
    dfdaily = pd.DataFrame()
    datelist = pd.read_sql_query('''SELECT DISTINCT "Date" FROM "AllData"''', conn2)['Date'].tolist()
    
    eml = search('Subject','FW: UMRF Agent Stats', mail)[0].split()
    for i in eml[-5:] :
        result, data = mail.fetch(i,'(RFC822)')
        emlhtml = get_body(email.message_from_bytes(data[0][1]))
        soup = BeautifulSoup(emlhtml, 'lxml')
        dt = re.findall('from ([0-9-]+)', soup.text)[0]
        if not dt in datelist :
            print(dt,'not in')
            datelist.append(dt)
            
            #prep/clean data   
            dfraw = pd.read_html(emlhtml,header=0)[0].set_index(['Employee Number'])
            dfraw['IncidentsCreated'] = dfraw['IncidentsCreated'].mask((dfraw['IncidentsCreated'] == 0) & (dfraw['CallsHandled'] > 0))
            dfraw['Date'] = dt
            dfraw['FCR %'] = dfraw['FCR %'].replace({'%' : ''}, regex=True).astype('float')
            dfraw['LoggedOnTime'] = dfraw['LoggedOnTime'].apply(lambda x : float(convtime(x)[0]))
            dfraw['AvailTime'] = dfraw['AvailTime'].apply(lambda x : float(convtime(x)[0]))
            dfraw['NotReadyTime'] = dfraw['NotReadyTime'].apply(lambda x : float(convtime(x)[0]))
            dfraw['ASA'] = dfraw['ASA'].apply(lambda x : float(convtime(x)[1]))
            dfraw['AHT'] = dfraw['AHT'].apply(lambda x : float(convtime(x)[1]))
            dfraw.rename(columns = {
                                    'LoggedOnTime':'LoggedOnTime (hrs)',
                                    'AvailTime' : 'AvailTime (hrs)',
                                    'NotReadyTime' : 'NotReadyTime (hrs)',
                                    'ASA' : 'ASA (min)',
                                    'AHT' : 'AHT (min)',
                                    }
                        ,inplace=True)
            dftemp = dfraw.filter(items = ['FirstName','LastName'])
            dfemp = dfemp.append(dftemp)
            dfemp.drop_duplicates(inplace=True)
            dfemp.index.rename('Employee Number',inplace=True)
            
            yesterday = (datetime.strptime(dt, '%Y-%m-%d')).strftime('%Y-%m-%d')

            dfraw2 = pd.read_sql_query('''SELECT * FROM AllData WHERE Date IS "{0}"'''.format(yesterday), conn)
            df_inc = dfraw2.filter(['sys_created_by','opened_by','resolved_by'])
            s_open = df_inc['opened_by'].value_counts()
            s_res = df_inc['resolved_by'].value_counts()
            
            dfemp = pd.read_sql_query('''SELECT * FROM info''', conn3)
            df_relate = dfemp.filter(['fedex_id','first_name','last_name'])
            df_relate['opened_by'] = df_relate['first_name'] + ' ' + df_relate['last_name']
            df_relate = df_relate.drop(columns=['first_name','last_name']).set_index('opened_by')
            
            df = pd.concat([df_relate,s_open,s_res],axis=1,sort=True)
            df['opened_by'] = df['opened_by'].fillna(0)
            df['resolved_by'] = df['resolved_by'].fillna(0)
        
            df = df.dropna().astype(int)
            df['FCR %'] = (df['resolved_by']/df['opened_by']).round(4) * 100
            df = df.rename(columns={'fedex_id':'Employee Number','opened_by':'IncidentsCreated','resolved_by':'IncidentsCreatedAndResolved'}).reset_index().set_index('Employee Number')
            
            df_call = dfraw.drop(columns=['IncidentsCreated','IncidentsCreatedAndResolved','FCR %'])

            df_day = pd.concat([df,df_call],axis=1,sort=True).dropna().reset_index(drop=False)
            df_day['FirstName'] = df_day['index'].str.split().str[0]
            df_day['LastName'] = df_day['index'].str.split().str[-1]
            #df_week['FirstName'] = df_week['index'].str.extract('([a-zA-Z-]+)\s[\sa-zA-Z-]+')
            #df_week['LastName'] = df_week['index'].str.extract('[a-zA-Z-]+\s([\sa-zA-Z-]+)')
            df_day = df_day.drop(columns=['index'])
            df_day['Ticket %'] = ((df_day['IncidentsCreated']/df_day['CallsHandled'])*100).replace([np.inf,-np.inf], np.nan).round(2)
            df_day = df_day.filter(['Employee Number', 'LastName','FirstName','Number of Surveys', 'Avg. Survey Score (100)','Avg. Survey Score (5)','IncidentsCreated','IncidentsCreatedAndResolved','FCR %','Ticket %','IncidentsResolved','LoggedOnTime (hrs)','AvailTime (hrs)', 'NotReadyTime (hrs)', 'NR%','CallsAnswered','ACH%','ASA (min)','CallsHandled','AHT (min)','AbandonRingCalls','AbandonHoldCalls','AbandonHoldOutCalls','ShortCalls','Date'])
            df_day = df_day.sort_values(by=['LastName']).reset_index(drop=True)
        
            dfemp = dfemp.filter(['fedex_id','position'])
            dfemp = dfemp[dfemp['position'] == 'Agent']
            df_daily = pd.merge(df_day,dfemp,left_on='Employee Number',right_on='fedex_id',sort=False).drop(columns=['fedex_id','position'])
            df_daily['FCR %'] = df_daily['FCR %'].mask((df_daily['FCR %'] == 0) & ~(df_daily['IncidentsCreated'] > 0))
            dfdaily = dfdaily.append(df_daily)
            #print(dfdaily)
        else :
            print(dt,'already in')
            continue
    dfdaily.to_sql('AllData', conn2, if_exists='append',index=False)
    print('UMRF_Agent_Daily Completed Successfully!')
agentdailycsv()