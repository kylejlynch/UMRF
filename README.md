
# UMRF Ventures Agent Data and Statistics

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
* [top_perform.py](https://github.com/kylejlynch/UMRF/blob/master/top_perform.py) - Adds the top 3 agents with the best stats in 4 different categories for the previous day (updates daily) and the previous week (updates weekly) as html objects to the PythonAnywhere webpage.

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

The Excel workbook is currently used by supervisors to ensure that agents are performing up to standard, and for helping supervisors conduct 90 day reviews for agents up for their 90 day raise.

![Agent_Weekly.xlsx](https://i.imgur.com/u3o82Ow.png)

I am still adding to the website.

**My to do list:**
* Add Outflow calls for previous week (code already written)
* Add previous day's top performers
* Add previous week's top performers
