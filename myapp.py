from datetime import date
from weekly_to_excel import weeklytoexcel
from weekly_to_plots import weeklytoplots
from agent_weekly import agentweekly
from agent_daily import agentdaily
import os

os.chdir('/home/UMRFVentures/mysite/')

agentdaily()

if date.today().weekday() == 0 :
    agentweekly()
    weeklytoexcel()
    weeklytoplots()

top_perform()

print('myapp.py executed successfully!')
