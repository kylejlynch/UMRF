# UMRF Ventures Web Application and Predictive Analytics
- [Web Application](#umrf-ventures-agent-data-and-statistics-web-application)
- [Predicitive Analytics/Machine Learning](#machine-learning-and-predictive-analytics)
- [Budgeting/Schedule](#budgeting-and-scheduling)
- [Upcoming/To do](#upcoming)

## UMRF Ventures Agent Data and Statistics Web Application

This notebook demonstrates a current project of mine that logs weekly data from UMRF Ventures and performs statistics.
UMRF Ventures is a start-up that opened in August of 2017 and runs a Level 1 call center that troubleshoots IT issues for common services for FedEx employees worldwide.
Weekly, we receive performance data on each of our agents (e.g. Talk time, percentage of issues resolved, survey scores, etc.)

When I first started this project, we had accumulated months of data located in different locations including eml files as well as email accounts. After creating a dedicated email address to receive new agent call data, I began writing several programs to obtain, clean, format, and store all the data into two separate databases (DB) based on the type of data (Daily and Weekly data). Once the DBs were initialized with several programs (labeled with blue arrows in the accompanying flow diagram below) and using the Daily DB to correct for some mistakes in the Weekly data that occurred on FedEx's end (indicated by the blue dashed arrow), I wrote programs the would update the daily and weekly DBs on a daily and weekly basis, respectively (indicated by yellow arrows below).

![](https://i.imgur.com/XHumHba.png)

#### Below are descriptions for each program as well as direct links to the code:

### Webapp
[myapp.py](https://github.com/kylejlynch/UMRF/blob/master/myapp.py) runs daily at 9am CST from PythonAnywhere, which runs the following programs:
* [agent_daily.py](https://github.com/kylejlynch/UMRF/blob/master/agent_daily.py) - Updates SQL daily database daily with statistics from the previous day gathered from data sent to an email address from FedEx.
* [agent_weekly.py](https://github.com/kylejlynch/UMRF/blob/master/agent_weekly.py) - Updates weekly SQL database every Monday with statistics from the previous week gathered from data sent to an email address from FedEx.
* [weekly_to_excel.py](https://github.com/kylejlynch/UMRF/blob/master/weekly_to_excel.py) - Updates an Excel workbook every Monday with data from the previous week highlighting poor performance and values that crossed a certain threshold. The workbook (pictured below) contains a summary page containing weighted averages for each stat, as well as a page containing the overall average stats for all agents for comparison. Additionally, the workbook contains a separate tab for each individual agent  grouping the performance data by week to monitor performance over time.
* [weekly_to_plots.py](https://github.com/kylejlynch/UMRF/blob/master/weekly_to_plots.py) - Updates various plots with along with a simple linear regression every Monday to give a quick glimpse at overall agent performance.
* [top_perform.py](https://github.com/kylejlynch/UMRF/blob/master/top_perform.py) - Adds the top 3 agents with the best stats in 4 different categories for the previous day (updates daily) and the previous week (updates weekly) to the PythonAnywhere webpage. Utilizes jQuery script.
* [agent_delete.py](https://github.com/kylejlynch/UMRF/blob/master/agent_delete.py) - Deletes supervisors and shift leads from the database to provide accurate averages for agents taking calls (not shown in flow diagram to avoid clutter).

### Database Initialization
* [daily_init_file.py](https://github.com/kylejlynch/UMRF/blob/master/agent_daily_init_file.py) - Obtains daily data from backlogged eml files stored locally. Checks to ensure only contains one entry per date.
* [daily_init_email.py](https://github.com/kylejlynch/UMRF/blob/master/agent_daily_init_email.py) - Obtains daily data from backlogged emails. Checks to ensure only contains one entry per date.
* [weekly_init_file.py](https://github.com/kylejlynch/UMRF/blob/master/agent_weekly_init_file.py) - Obtains weekly data from backlogged eml files stored locally. Checks to ensure only contains one entry per week.
* [weekly_init_email.py](https://github.com/kylejlynch/UMRF/blob/master/agent_weekly_init_email.py) - Obtains weekly data from backlogged emails. Checks to ensure only contains one entry per week.
* [weekly_correct.py](https://github.com/kylejlynch/UMRF/blob/master/agent_weekly_correct.py) - Calculates weekly data from daily data to corrects for missing weekly data (error on FedEx's end)
* [name_correct.py](https://github.com/kylejlynch/UMRF/blob/master/agent_name_correct.py) - Corrects for misspelled names (another error on FedEx's end) which caused problems with data tracking.

## Result
The result is a webapp hosted on PythonAnywhere at UMRFVentures.pythonanywhere.com (screenshot shown below) which runs daily to collect call data and statistics for the previous day. Every Monday a new Excel sheet is generated to incorporate the previous week and provide the most up-to-date statistics auto formatted so to highlight poor performance. Additionally, several plots are generated every Monday to provide a quick glimpse of the most recent trends in agent performance.

![](https://i.imgur.com/Q5nQoF0.png)
![](https://i.imgur.com/Vzzrlxq.png)

The Excel workbook is currently used by supervisors to ensure that agents are performing up to standard, and for helping supervisors conduct 90 day reviews for agents up for their 90 day raise. Auto-formatted cells are green or red if 1 standard deviation above of below the average (white = average, green = good, red = bad).

![Agent_Weekly.xlsx](https://i.imgur.com/kOOAhs2.png)
<br>
<br>
## Machine Learning and Predictive Analytics
Using call flow data and schedule data from our time clock's REST API I apply Scikit-Learn machine learning (ML) algorithms as well as SciPy curve_fit to predict how many agents will be need as we continue to increase call flow with FedEx. I noticed the data had a slight logarithmic look to it so I tried fitting it with y = a*ln(b*x + c*y + d) with good results. The ML algorithms seemed to do really well within the scope of the data. However, the equation obtained from the log fit does better at making predictions out of the scope of the data.
* [UMRF_ML.py](https://github.com/kylejlynch/UMRF/blob/master/UMRF_ML.py) - Somewhat of a scrap sheet of paper at the moment while I text various machine learning models in scikit-learn and and fits in scipy. Collects shift information from WhenIwork API and call flow data from Cisco. Predicts number of employees needed to take all calls per 30 min time block. This is important - as we continue to increase call volume as we grow we need to accurately predict scheduling throughout the day. My best fit so far is a logarithmic fit using scipy (see below for the plot with fit).

<br>
Example plot from UMRF_ML.py :

![](https://i.imgur.com/WpY1y51.png)
![](https://i.imgur.com/hOmcFg5.png)
<br>
The equations derived above are then used in conjunction with call flow data to predict optimal staffing for both agents and shift leads for each 30 min timeblock of the day.
![](https://i.imgur.com/WETiptc.png)
<br>

## Budgeting and Scheduling
* [UMRF_Call_Pattern_month.py](https://github.com/kylejlynch/UMRF/blob/master/UMRF_Call_Pattern_month.py) - Analyzes pervious month's incoming calls per 30 min time block, averages them per day of the week (along with standard deviation) and uses this to predict the optimal number of agents needed to minimize both missed calls labor costs based on previous month.
* [UMRF_Call_Pattern_day.py](https://github.com/kylejlynch/UMRF/blob/master/UMRF_Call_Pattern_day.py) - Retreives, cleans, and formats call data (number of calls) in 30 minute intervals to aid in scheduling and earnings/labor analysis. Used in UMRF_Earnings_Time_Block.py.
* [UMRF_Earnings_Time_Block.py](https://github.com/kylejlynch/UMRF/blob/master/UMRF_Earnings_Time_Block.py) - Analyzes previous day's labor hours and calls received in 30 min time intervals to visualize when UMRF gains/loses money throughout the day.
* [UMRF_Earnings_per_day.py](https://github.com/kylejlynch/UMRF/blob/master/UMRF_Earnings_per_day.py) - Calculates and generates Excel report of the net earnings per day for given time period.
* [UMRF_Employee_Info.py](https://github.com/kylejlynch/UMRF/blob/master/UMRF_Employee_Info.py) - Generates an SQL database and Excel document containing UMRF ID, FedEx ID, First Name, Last Name, Location, Position, Hourly Pay Rate. The SQL DB will be used to extract info for reports. Used in UMRF_Future_Earnings.py.
* [UMRF_Future_Earnings.py](https://github.com/kylejlynch/UMRF/blob/master/UMRF_Future_Earnings.py) - Predicts how many calls are needed per day to cover labor costs as well as labor + 20% for a given time period.
* [UMRF_Outflow.py](https://github.com/kylejlynch/UMRF/blob/master/UMRF_Outflow.py) - Calculates average missed calls for the previous month (or given time period) to aid in scheduling agents.
* [UMRF_Sched_Optimization.py](https://github.com/kylejlynch/UMRF/blob/master/UMRF_Sched_Optimization.py) - Predicts labor cost based on schedules. Breaks the schedules into 30 min time blocks. This will be used to compare scheduled vs actual hours. It will incorporate hourly pay from SQL database emplist.sqlite to yield predicted labor cost per 30 min time block. Finally, It will compare predicted number of agents to actual agents and compare with the number of overflow calls for schedule optimization.
* [custom_functions.py](https://github.com/kylejlynch/UMRF/blob/master/custom_functions.py) - Various custom functions used repeatedly such as weighted average, weighted standard deviation, converting time to various formats, and several functions used for obtaining data from email.
Example plots from UMRF_Earnings_Time_Block.py and UMRF_Overflow_Agent.py:

![](https://i.imgur.com/5IOqHFw.png)
![](https://i.imgur.com/bWDjPhI.png)
<br>

## Upcoming 
I will soon work on:
* Track tardies/absences with WhenIWork API
