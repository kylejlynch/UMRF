# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd
#import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def weeklytoplots() :
    conn = sqlite3.connect('UMRF_SQL_Weekly.sqlite')
    
    val = ['FCR %', 'Ticket %','NR%','AHT (min)']
    weight = ['IncidentsCreated','CallsHandled','LoggedOnTime (hrs)','CallsHandled']
    name = ['Resolution Rate (FCR %)', 'Percent Tickets Created (%)','Percent Time on Not Ready (%)','Call Handle Time (min)']
    axis = [(60,90), (80,110),(0,50),(6,18)]
    filename = ['avgFCR','avgTicket','avgNR','avgAHT']
    
    for i,j,k,l,m in zip(val,weight,name,axis,filename) :
        dfraw = pd.read_sql_query('''SELECT "WeekStart"
                                  AS "Date",
                                  sum("{0}"*"{1}")/sum("{1}")
                                  AS "{2}"
                                  FROM "AllData"
                                  GROUP BY "WeekStart"'''.format(i,j,k), conn)
        x = np.arange(0,len(dfraw['Date']))
        y = dfraw[k].astype(float).values
        ymask = np.isfinite(y)
        
        plt.figure()
        plt.plot(dfraw['Date'][ymask],dfraw[k][ymask],'-o', alpha=0.7)
        plt.xlabel('Week')
        plt.title('Average {}'.format(k))
        plt.plot(np.unique(x[ymask]), np.poly1d(np.polyfit(x[ymask], y[ymask], 1))(np.unique(x[ymask])))
        ax = plt.gca()
        x = plt.gca().xaxis
        y = plt.gca().yaxis
        #ax.autoscale(enable=True,axis='both',tight=False)
        plt.ylim(l)
        for item in x.get_ticklabels() :
            item.set_rotation(60)
            item.set_fontsize(8)
        for label in ax.xaxis.get_ticklabels()[-2::-2] :
            label.set_visible(False)
        plt.subplots_adjust(bottom=0.25)
        
        plt.savefig('{}.png'.format(m),bbox_inches='tight')
weeklytoplots()