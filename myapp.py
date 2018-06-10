from datetime import date
from weekly_to_excel import weeklytoexcel
from weekly_to_plots import weeklytoplots
from agent_weekly import agentweekly
from agent_daily import agentdaily
from top_perform import top_perform
from agent_delete import agentdelete
import os

os.chdir('/home/UMRFVentures/mysite/')

agentdaily()
agentdelete()

if date.today().weekday() == 0 :
    agentweekly()
    agentdelete()
    weeklytoexcel()
    weeklytoplots()

top_perform()

print('myapp.py executed successfully!')