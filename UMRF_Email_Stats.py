# -*- coding: utf-8 -*-
"""
Obtains performance data from previous week, syncs to employee info
used to send performance data separately to all employees
"""
import pandas as pd
import sqlite3
from datetime import datetime,timedelta
from UMRF_send_report import send_mail
from sensitive import emailcredentials
from io import StringIO

pd.set_option('display.max_columns', 100)
user, password, imap_url = emailcredentials()
def agentprevweekemail() :
    conn1 = sqlite3.connect('UMRF_SQL_Weekly.sqlite')
    conn2 = sqlite3.connect('emplistmanual.sqlite')
    dfweek = pd.read_sql('''SELECT * FROM AllData''', conn1)
    dfweek = dfweek[dfweek['WeekStart'] == dfweek['WeekStart'].max()]
    start = dfweek['WeekStart'].iloc[0]
    end = datetime.strftime(datetime.strptime(start,'%Y-%m-%d') + timedelta(6), '%Y-%m-%d')
    dfweek['DateRange'] = '{0} to {1}'.format(start,end)
    dfweek = dfweek.filter(['DateRange','Employee Number','FirstName','LastName','FCR %','CallsHandled','AHT (min)','Ticket %','IncidentsCreated','IncidentsCreatedAndResolved','Number of Surveys','Avg. Survey Score (100)'])
    dfweek = dfweek.rename(columns={'FCR %' : 'Call Resolution %','AHT (min)' : 'Avg Handle Time (min)'})
    dfemp = pd.read_sql('''SELECT * FROM info''', conn2)
    dfemp = dfemp.filter(['fedex_id','email2']).rename(columns={'first_name':'FirstName','last_name':'LastName','email2':'EmailOSV'})
    df = pd.merge(dfweek,dfemp,left_on='Employee Number',right_on='fedex_id').drop(columns=['fedex_id'])
    
    text = '''This is an automated email. If you have any questions, concerns, or feedback please email Kyle Lynch at kylejlynch@gmail.com'''

    for i,row in df.iloc[:].iterrows() :
        dfagent = pd.DataFrame(row).rename(columns={i:'Agent Stats'})
        email = dfagent.loc['EmailOSV'].values.tolist()
        print(email)
        html = StringIO()
        dfagent.to_html(buf=html,border='border')
        dfhtml = pd.read_html(html,index_col=0)[0]
        print(dfhtml)
        html = dfhtml.to_html(border='border')
        #send_mail(user, email,'Weekly Agent Statistics', text=text, html=html)

agentprevweekemail()