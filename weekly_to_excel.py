import sqlite3
import pandas as pd
import numpy as np
import os
import re
from datetime import datetime,timedelta
import xlsxwriter
import string

def w_avg(values,weights=None) :
    numer = 0
    if weights is None :
        weights = np.ones(len(values))
    for v,w in zip(values,weights):
        numer += w*v
        denom = sum(weights)
    return float(numer/denom)

def w_stdev(values,weights,avg) :
    numer = 0
    m = sum([int(bool(i)) for i in weights])
    for v,w in zip(values,weights):
        numer += w*(np.square(v - avg))
        denom = ((m - 1)/m)*sum(weights)
    return(np.sqrt(numer/denom))

def weeklytoexcel() :
    lstwk = datetime.strftime(datetime.now() - timedelta(7), '%Y-%m-%d')
    os.rename('Agent_Weekly.xlsx', 'Agent_Weekly_{}.xlsx'.format(lstwk))
    
    conn = sqlite3.connect('UMRF_SQL_Weekly.sqlite')
    cur = conn.cursor()
    
    emplist = pd.read_sql_query('''SELECT DISTINCT
                                    "Employee Number",
                                    "FirstName",
                                    "LastName"
                                    FROM "AllData"''', conn)
    emplist = emplist.sort_values(by=['LastName','FirstName'])
    emplist.set_index('Employee Number', inplace=True)
    
    summary = pd.read_sql_query('''SELECT
                "Employee Number","LastName","FirstName",
                sum("Number of Surveys") AS "Number of Surveys",
                round(sum("Avg. Survey Score (100)"*"Number of Surveys")/sum("Number of Surveys"),2) AS "Avg. Survey Score (100)",
                round(sum("Avg. Survey Score (5)"*"Number of Surveys")/sum("Number of Surveys"),2) AS "Avg. Survey Score (5)",
                sum(IncidentsCreated) AS "IncidentsCreated",
                sum(IncidentsCreatedAndResolved) AS "IncidentsCreatedAndResolved",
                round(sum("FCR %"*"IncidentsCreated")/sum("Incidentscreated"),2) AS "FCR %",
                round(sum("Ticket %"*"CallsHandled")/sum("CallsHandled"),2) AS "Ticket %",
                sum(IncidentsResolved) AS "IncidentsResolved",
                sum("LoggedOnTime (hrs)") AS "LoggedOnTime (hrs)",
                sum("AvailTime (hrs)") AS "AvailTime (hrs)",
                sum("NotReadyTime (hrs)") AS "NotReadyTime (hrs)",
                round(sum("NotReadyTime (hrs)")/sum("LoggedOnTime (hrs)")*100,2) AS "NR%",
                sum("CallsAnswered") AS "CallsAnswered",
                round(sum("ACH%"*"LoggedOnTime (hrs)")/sum("LoggedOnTime (hrs)"),2) AS "ACH%",
                round(sum("ASA (min)"*"CallsHandled")/sum("CallsHandled"),2) AS "ASA (min)",
                sum("CallsHandled") AS "CallsHandled",
                round(sum("AHT (min)"*"CallsHandled")/sum("CallsHandled"),2) AS "AHT (min)",
                sum("AbandonRingCalls") AS "AbandonRingCalls",
                sum("AbandonHoldCalls") AS "AbandonHoldCalls",
                sum("AbandonHoldOutCalls") AS "AbandonHoldOutCalls",
                sum("ShortCalls") AS "ShortCalls"
                FROM "AllData"
                GROUP BY "Employee Number"''',conn)
    summary = summary.sort_values(by=['LastName','FirstName'])
    
    summary2 = pd.read_sql_query('''SELECT
                round(sum("Avg. Survey Score (100)"*"Number of Surveys")/sum("Number of Surveys"),2) AS "Avg. Survey Score (100)",
                round(sum("Avg. Survey Score (5)"*"Number of Surveys")/sum("Number of Surveys"),2) AS "Avg. Survey Score (5)",
                round(sum("FCR %"*"IncidentsCreated")/sum("Incidentscreated"),2) AS "FCR %",
                round(sum("Ticket %"*"CallsHandled")/sum("CallsHandled"),2) AS "Ticket %",
                round(sum("NotReadyTime (hrs)")/sum("LoggedOnTime (hrs)")*100,2) AS "NR%",
                round(sum("AHT (min)"*"CallsHandled")/sum("CallsHandled"),2) AS "AHT (min)"
                FROM "AllData"
                ''',conn)
    
    stats = pd.read_sql_query('''SELECT * FROM "AllData"''',conn)
    stats = stats.fillna(0)
    x_fcr = w_avg(stats['FCR %'].tolist(),stats['IncidentsCreated'].tolist())
    x_aht = w_avg(stats['AHT (min)'].tolist(),stats['CallsHandled'].tolist())
    x_ticket = w_avg(stats['Ticket %'].tolist(),stats['CallsHandled'].tolist())
    x_nr = w_avg(stats['NR%'].tolist(),stats['LoggedOnTime (hrs)'].tolist())
    std_fcr = w_stdev(stats['FCR %'].tolist(),stats['IncidentsCreated'].tolist(),x_fcr)
    std_aht = w_stdev(stats['AHT (min)'].tolist(),stats['CallsHandled'].tolist(),x_aht)
    std_ticket = w_stdev(stats['Ticket %'].tolist(),stats['CallsHandled'].tolist(),x_ticket)
    std_nr = w_stdev(stats['NR%'].tolist(),stats['LoggedOnTime (hrs)'].tolist(),x_nr)
    
    writer = pd.ExcelWriter('Agent_Weekly.xlsx', engine='xlsxwriter')
    
    summary.to_excel(writer,sheet_name='Summary',index=False) #Summary
    letters = list(string.ascii_uppercase)
    workbook = writer.book
    worksheet = writer.sheets['Summary']

    average = [x_ticket,x_fcr,x_nr,x_aht]
    stdev = [0.5*std_ticket,std_fcr,std_nr,std_aht]
    
    cols = ['J','I','O','T']
    for col,val1,val2 in zip(cols[0:2],average[0:2],stdev[0:2]) :
        worksheet.conditional_format('{0}2:{0}{1}'.format(col,len(summary)+1), {'type' : '3_color_scale',
                                    'min_value' : val1-val2,
                                    'min_type' : 'num',
                                    'mid_value' : (val1),
                                    'mid_type' : 'num',
                                    'max_value' : val1+val2,
                                    'max_type' : 'num',
                                    'min_color' : 'red',
                                    'mid_color' : 'white',
                                    'max_color' : 'green'})
    for col,val1,val2 in zip(cols[2:4],average[2:4],stdev[2:4]) :
        worksheet.conditional_format('{0}2:{0}{1}'.format(col,len(summary)+1), {'type' : '3_color_scale',
                                    'min_value' : (val1-val2),
                                    'min_type' : 'num',
                                    'mid_value' : (val1),
                                    'mid_type' : 'num',
                                    'max_value' : (val1+val2),
                                    'max_type' : 'num',
                                    'min_color' : 'green',
                                    'mid_color' : 'white',
                                    'max_color' : 'red'})
    
    worksheet.freeze_panes(1, 3)
    
    for i,col in enumerate(list(summary)) :    #autofit column-width
        worksheet.set_column('{}:{}'.format(letters[i],letters[i]), len(col)+2)
    
    summary2.to_excel(writer,sheet_name='CompareWith',index=False) #CompareWith
    worksheet = writer.sheets['CompareWith']
    for i,col in enumerate(list(summary2)) :    #autofit column-width
        worksheet.set_column('{}:{}'.format(letters[i],letters[i]), len(col)+2)
    
    cols2 = ['K','J','P','U']
    for empnum in emplist.index :
        temp = pd.read_sql_query(
                '''SELECT *
                    FROM "AllData"
                    WHERE "Employee Number" IS "{}"'''.format(empnum),conn)
        temp = temp.sort_values(by=['WeekStart'])
        temp = temp.set_index(['WeekStart']).reset_index(['WeekStart'])
        temp.to_excel(writer,sheet_name='{} {}'.format(emplist.at[empnum,'FirstName'],emplist.at[empnum,'LastName']),index=False)
        worksheet = writer.sheets['{} {}'.format(emplist.at[empnum,'FirstName'],emplist.at[empnum,'LastName'])]
        
        for i,col in enumerate(list(temp)) :    #autofit column-width
            worksheet.set_column('{}:{}'.format(letters[i],letters[i]), len(col)+2)
        
        for col,val1,val2 in zip(cols2[0:2],average[0:2],stdev[0:2]) :
            worksheet.conditional_format('{0}2:{0}{1}'.format(col,len(temp)+1), {'type' : '3_color_scale',
                                        'min_value' : val1-val2,
                                        'min_type' : 'num',
                                        'mid_value' : (val1),
                                        'mid_type' : 'num',
                                        'max_value' : val1+val2,
                                        'max_type' : 'num',
                                        'min_color' : 'red',
                                        'mid_color' : 'white',
                                        'max_color' : 'green'})
        for col,val1,val2 in zip(cols2[2:4],average[2:4],stdev[2:4]) :
            worksheet.conditional_format('{0}2:{0}{1}'.format(col,len(temp)+1), {'type' : '3_color_scale',
                                        'min_value' : (val1-val2),
                                        'min_type' : 'num',
                                        'mid_value' : (val1),
                                        'mid_type' : 'num',
                                        'max_value' : (val1+val2),
                                        'max_type' : 'num',
                                        'min_color' : 'green',
                                        'mid_color' : 'white',
                                        'max_color' : 'red'})
        
        worksheet.freeze_panes(1, 1)
    
    return writer.save()
weeklytoexcel()