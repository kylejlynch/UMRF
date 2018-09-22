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
pd.set_option('display.max_rows', 400)

def agentweekly() :
    user, password, imap_url = emailcredentials()
    mail = imaplib.IMAP4_SSL(imap_url)
    mail.login(user,password)
    mail.select('"Agent Weekly"')
    
    eml = search('Subject','UMRF Agent Stats for the week', mail)[0].split()
    for i in eml[-1:] :
        result, data = mail.fetch(i,'(RFC822)')
        emlhtml = get_body(email.message_from_bytes(data[0][1]))
        soup = BeautifulSoup(emlhtml, 'lxml')
        dt = re.findall('from ([0-9-]+)', soup.text)[0]
        
        #prep/clean data   
        dfraw = pd.read_html(emlhtml,header=0)[0]
        #dfraw.insert(8, 'Ticket %',((dfraw['IncidentsCreated']/dfraw['CallsHandled'])*100).replace([np.inf,-np.inf], np.nan).round(2))
        dfraw['WeekStart'] = dt
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
        dfraw['IncidentsCreated'] = dfraw['IncidentsCreated'].mask((dfraw['IncidentsCreated'] == 0) & (dfraw['CallsHandled'] > 0))
    dfweeklyeml = dfraw
    return dfweeklyeml, dt

def agentweeklycsv() :
    dfraw2, lstwk = agentweekly()
    conn = sqlite3.connect('UMRF_Incidents_SQL.sqlite')
    conn2 = sqlite3.connect('UMRF_SQL_Weekly.sqlite')
    conn3 = sqlite3.connect('emplistmanual.sqlite')
    #today = datetime.strftime(datetime.today(), '%Y-%m-%d')
    #yesterday = (datetime.now() - timedelta(14)).strftime('%Y-%m-%d')
    yesterday = (datetime.strptime(lstwk, '%Y-%m-%d') + timedelta(6)).strftime('%Y-%m-%d')
    #lstwk = datetime.strftime(datetime.now() - timedelta(20), '%Y-%m-%d')
    print(yesterday)
    print(lstwk)
    dfraw = pd.read_sql_query('''SELECT * FROM AllData WHERE Date BETWEEN "{0}" AND "{1}"'''.format(lstwk,yesterday), conn)
    df_inc = dfraw.filter(['sys_created_by','opened_by','resolved_by'])
    s_open = df_inc['opened_by'].value_counts()
    s_res = df_inc['resolved_by'].value_counts()
    
    dfemp = pd.read_sql_query('''SELECT * FROM info''', conn3)
    df_relate = dfemp.filter(['fedex_id','first_name','last_name'])
    df_relate['opened_by'] = df_relate['first_name'] + ' ' + df_relate['last_name']
    df_relate = df_relate.drop(columns=['first_name','last_name']).set_index('opened_by')
    #df_relate = df_inc.filter(['sys_created_by','opened_by']).drop_duplicates().set_index('opened_by')
    
    df = pd.concat([df_relate,s_open,s_res],axis=1,sort=True)
    df['opened_by'] = df['opened_by'].fillna(0)
    df['resolved_by'] = df['resolved_by'].fillna(0)

    df = df.dropna().astype(int)
    df['FCR %'] = (df['resolved_by']/df['opened_by']).round(4) * 100
    df = df.rename(columns={'fedex_id':'Employee Number','opened_by':'IncidentsCreated','resolved_by':'IncidentsCreatedAndResolved'}).reset_index().set_index('Employee Number')
    
    df_call = dfraw2.drop(columns=['IncidentsCreated','IncidentsCreatedAndResolved','FCR %'])
    df_call = df_call.set_index('Employee Number')
    
    df_week = pd.concat([df,df_call],axis=1,sort=True).dropna().reset_index(drop=False)
    df_week['FirstName'] = df_week['index'].str.split().str[0]
    df_week['LastName'] = df_week['index'].str.split().str[-1]
    #df_week['FirstName'] = df_week['index'].str.extract('([a-zA-Z-]+)\s[\sa-zA-Z-]+')
    #df_week['LastName'] = df_week['index'].str.extract('[a-zA-Z-]+\s([\sa-zA-Z-]+)')
    df_week = df_week.drop(columns=['index'])
    df_week['Ticket %'] = ((df_week['IncidentsCreated']/df_week['CallsHandled'])*100).replace([np.inf,-np.inf], np.nan).round(2)
    df_week = df_week.filter(['Employee Number', 'LastName','FirstName','Number of Surveys', 'Avg. Survey Score (100)','Avg. Survey Score (5)','IncidentsCreated','IncidentsCreatedAndResolved','FCR %','Ticket %','IncidentsResolved','LoggedOnTime (hrs)','AvailTime (hrs)', 'NotReadyTime (hrs)', 'NR%','CallsAnswered','ACH%','ASA (min)','CallsHandled','AHT (min)','AbandonRingCalls','AbandonHoldCalls','AbandonHoldOutCalls','ShortCalls','WeekStart'])
    df_week = df_week.sort_values(by=['LastName']).reset_index(drop=True)

    dfemp = dfemp.filter(['fedex_id','position'])
    dfemp = dfemp[dfemp['position'] == 'Agent']
    dfweekly = pd.merge(df_week,dfemp,left_on='Employee Number',right_on='fedex_id').drop(columns=['fedex_id','position'])
    dfweekly['FCR %'] = dfweekly['FCR %'].mask((dfweekly['FCR %'] == 0) & ~(dfweekly['IncidentsCreated'] > 0))
    dfweekly.to_sql('AllData', conn2, if_exists='append',index=False)
agentweeklycsv()
