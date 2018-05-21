import sqlite3
import pandas as pd
import numpy as np
import os
import re
from datetime import datetime,timedelta
import xlsxwriter
import string

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
    
    writer = pd.ExcelWriter('Agent_Weekly.xlsx', engine='xlsxwriter')
    
    summary.to_excel(writer,sheet_name='Summary',index=False) #Summary
    letters = list(string.ascii_uppercase)
    workbook = writer.book
    format1 = workbook.add_format({'bg_color': 'red'})
    worksheet = writer.sheets['Summary']
    
    worksheet.conditional_format('J2:J{}'.format(len(summary)+1), {'type' : 'cell',
                                        'criteria' : '<',
                                        'value' : 100,
                                        'format': format1})
    worksheet.conditional_format('I2:I{}'.format(len(summary)+1), {'type' : 'cell',
                                        'criteria' : '<',
                                        'value' : 70,
                                        'format': format1})
    worksheet.conditional_format('O2:O{}'.format(len(summary)+1), {'type' : 'cell',
                                        'criteria' : '>',
                                        'value' : 20,
                                        'format': format1})
    worksheet.conditional_format('T2:T{}'.format(len(summary)+1), {'type' : 'cell',
                                        'criteria' : '>',
                                        'value' : 15,
                                        'format': format1})
    worksheet.freeze_panes(1, 3)
    
    for i,col in enumerate(list(summary)) :    #autofit column-width
        worksheet.set_column('{}:{}'.format(letters[i],letters[i]), len(col)+2)
    
    summary2.to_excel(writer,sheet_name='CompareWith',index=False) #CompareWith
    worksheet = writer.sheets['CompareWith']
    for i,col in enumerate(list(summary2)) :    #autofit column-width
        worksheet.set_column('{}:{}'.format(letters[i],letters[i]), len(col)+2)
    
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
        
        worksheet.conditional_format('K2:K{}'.format(len(temp)+1), {'type' : 'cell',
                                            'criteria' : '<',
                                            'value' : 100,
                                            'format': format1})
        worksheet.conditional_format('J2:J{}'.format(len(temp)+1), {'type' : 'cell',
                                            'criteria' : '<',
                                            'value' : 70,
                                            'format': format1})
        worksheet.conditional_format('P2:P{}'.format(len(temp)+1), {'type' : 'cell',
                                            'criteria' : '>',
                                            'value' : 20,
                                            'format': format1})
        worksheet.conditional_format('U2:U{}'.format(len(temp)+1), {'type' : 'cell',
                                            'criteria' : '>',
                                            'value' : 15,
                                            'format': format1})
        worksheet.freeze_panes(1, 1)
    
    return writer.save()