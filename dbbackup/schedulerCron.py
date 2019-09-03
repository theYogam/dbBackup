import getpass
import crontab
import datetime
import os
import sys
from crontab import CronTab


user = getpass.getuser()
my_cron = CronTab(user=user)
# current_working_directory = os.getcwd()
file_path = os.path.realpath(__file__)
command = 'python ' + file_path.replace('dbbackup/schedulerCron.py', 'cron.py ') + sys.argv[2]
job = my_cron.new(command=command)
run_every = int(sys.argv[1])
job.hours.every(run_every)
my_cron.write()

