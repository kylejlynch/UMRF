
# UMRF Ventures Agent Data and Statistics

This notebook demonstrates a current project of mine that logs weekly data from UMRF Ventures and performs statistics.
UMRF Ventures is a start-up that opened in August of 2017 and runs a Level 1 call center that troubleshoots IT issues for common services for FedEx employees worldwide.
Weekly, we receive performance data on each of our agents (e.g. Talk time, percentage of issues resolved, survey scores, etc.)

Data is received weekly in .csv format as shown below:

![](https://i.imgur.com/9CRnEML.png)

One of our agents would spend hours at a time compiling and performing statistics periodically. I knew that as UMRF Ventures grew this task would become increasingly arduous. I took it upon myself to come up with a more sophisticated approach. I wrote a program using Python and SQLite to extract raw data from the .csv files and construct
an SQL table for each agent which keeps track of each agents data. Below is my current code:

```python
import sqlite3

conn = sqlite3.connect('UMRF_SQL2.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE Employees (EmployeeNumber INTEGER PRIMARY
            KEY NOT NULL UNIQUE, Lastname TEXT, FirstName TEXT)''')

filelist = ['week1.csv', 'week2.csv', 'week3.csv', 'week4.csv', 'week5.csv']
for file in filelist :
    cruzname = list()
    fullname = list()
    fh = open(file, 'r')
    for line in fh :
        if line.startswith('LastName') :
            continue
        pieces = line.split(',')
        cur.execute('''SELECT EmployeeNumber FROM Employees WHERE
                    EmployeeNumber = ? ''', (pieces[2],))
        row = cur.fetchone()
        if row is None :
            cur.execute('''INSERT INTO Employees(
                    EmployeeNumber, LastName, FirstName)
                    VALUES (?, ?, ?)''', (pieces[2], pieces[0], pieces[1]))

    listname = cur.execute('''SELECT * FROM Employees''')

    for i in listname :
        cruzname.append(str(i[1])+'_'+str(i[2])+'_'+str(i[0]))

    #Cruz Loop
    for i in cruzname :
        if '-' in i :
            i = i.replace('-' , '_')
        fullname.append(i)
    
    for i in fullname :
        cur.execute('''CREATE TABLE IF NOT EXISTS %s (
                Lastname, Firstname, EmployeeNumber, 
                NumberOfSurveys, AvgSurveyScore100, 
                AvgSurveyScore5 INTEGER, IncidentsCreated INTEGER, 
                IncidentsCreatedAndResolved INTEGER, FCR_percent INTEGER, 
                IncidentsResolved INTEGER, LoggedOnTime_hrs INTEGER, 
                AvailTime_hrs INTEGER, NotReadyTime_hrs INTEGER, 
                NR_percent INTEGER, CallsAnswered INTEGER, 
                ACH_percent INTEGER, ASA_min INTEGER, CallsHandled INTEGER, 
                AHT_min INTEGER, AbandonRingCalls INTEGER, 
                AbandonHoldCalls INTEGER, AbandonHoldOutCalls INTEGER, 
                ShortCalls INTEGER)''' % i)

    for i in fullname :
        fh = open(file, 'r')
        for line in fh:
            if line.startswith('LastName') :
                continue
            pieces = line.split(',')
            if pieces[2] not in i :
                continue
            fcr = pieces[8].split('%')[0]
            logon_hrs = pieces[10].split(':')
            logon_hrs = (float(logon_hrs[0]) + 
                         (float(logon_hrs[1])/60) + 
                         (float(logon_hrs[2])/3600))
            avtime_hrs = pieces[11].split(':')
            avtime_hrs = (float(avtime_hrs[0]) + 
                          (float(avtime_hrs[1])/60) + 
                          (float(avtime_hrs[2])/3600))
            nrtime_hrs = pieces[12].split(':')
            nrtime_hrs = (float(nrtime_hrs[0]) + 
                          (float(nrtime_hrs[1])/60) + 
                          (float(nrtime_hrs[2])/3600))
            asa_min = pieces[16].split(':')
            asa_min = ((float(asa_min[0]*60)) + 
                       float(asa_min[1]) + 
                       (float(asa_min[2])/60))
            aht_min = pieces[18].split(':')
            aht_min = ((float(aht_min[0]*60)) + 
                       float(aht_min[1]) + 
                       (float(aht_min[2])/60))
            pieces[22] = pieces[22].rstrip()
            cur.execute('''INSERT INTO %s (
                        Lastname, Firstname, EmployeeNumber, NumberOfSurveys, 
                        AvgSurveyScore100,AvgSurveyScore5, IncidentsCreated, 
                        IncidentsCreatedAndResolved, FCR_percent, 
                        IncidentsResolved, LoggedOnTime_hrs, AvailTime_hrs, 
                        NotReadyTime_hrs, NR_percent, CallsAnswered, 
                        ACH_percent, ASA_min, CallsHandled,
                        AHT_min, AbandonRingCalls, 
                        AbandonHoldCalls, AbandonHoldOutCalls, ShortCalls)
                        VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?)''' %i, (pieces[0], pieces[1],
                        pieces[2], pieces[3], pieces[4], pieces[5], 
                        pieces[6], pieces[7], fcr, pieces[9], logon_hrs, 
                        avtime_hrs, nrtime_hrs, pieces[13], pieces[14], 
                        pieces[15], asa_min, pieces[17], aht_min, 
                        pieces[19], pieces[20], pieces[21], pieces[22]))
            break
        continue

cur.execute('''CREATE TABLE IF NOT EXISTS Summary (
            'Last Name', 
            'First Name', 
            'Employee Number', 
            'Number of Surveys', 
            'Incidents Created', 
            'Incidents Resolved', 
            'Incidents Created and Resolved',
            'FCR (%)',
            'Avg Survey Score (100)', 
            'AvgSurveyScore (5)', 
            'Avg Log On Time (hrs)', 
            'Avg Available Time (hrs)', 
            'Percent Not Ready (%)', 
            'Total Calls Answered', 
            'Total Calls Handled', 
            'Avg Handle Time (min)', 
            'Calls Per Hour Logged (ACH)'
            ) ''')

for i in fullname :
   cur.execute('''INSERT INTO Summary
                SELECT Lastname As 'Last Name',
                Firstname AS 'First Name',
                EmployeeNumber AS 'Employee Number', 
                sum(NumberOfSurveys) AS 'Number of Surveys', 
                sum(IncidentsCreated) AS 'Incidents Created', 
                sum(IncidentsResolved) AS 'Incidents Resolved', 
                sum(IncidentsCreatedAndResolved) AS 
                'Incidents Created and Resolved',
                (sum(CAST(IncidentsCreatedAndResolved AS 
                float))/sum(CAST(IncidentsCreated AS float)))*100 AS
                'FCR (%)',
                sum(NumberOfSurveys*AvgSurveyScore100)/sum(NumberOfSurveys) AS
                'Avg Survey Score (100)', 
                sum(NumberOfSurveys*AvgSurveyScore5)/sum(NumberOfSurveys) AS
                'AvgSurveyScore (5)', 
                avg(LoggedOnTime_hrs) AS 'Avg Log On Time (hrs)', 
                avg(AvailTime_hrs) AS 'Avg Available Time (hrs)', 
                (sum(CAST(NotReadyTime_hrs AS float))
                /sum(CAST(LoggedOnTime_hrs AS float)))*100 AS
                'Percent Not Ready (%)', 
                sum(CallsAnswered) AS 'Total Calls Answered', 
                sum(CallsHandled) AS 'Total Calls Handled', 
                sum(AHT_min*CallsHandled)/sum(CallsHandled) AS
                'Avg Handle Time (min)', 
                (sum(CallsAnswered)/sum(CAST(LoggedOnTime_hrs AS float))) AS
                'Calls Per Hour Logged (ACH)' 
                FROM {} ''' .format(i))

conn.commit()
cur.close()
```

The result is an SQL database that keeps track of agent data over all time with a summary table that provides statistics that changes as weekly data is appended.

![](https://i.imgur.com/jCZmM3Y.png)

This data is then used to provide feedback to the agents and decide whether agents get raises. Currently I am working with one of the agents to extract data from our time logging system. I am interested to see if there is any correlation between average shift worked (time of the day) and performance as different sets of caller issues occur primarily at different times of the day. Therefore, I wonder if comparing agents that can only work night shifts to those that can work mornings is a fair, unbiased assessment.
