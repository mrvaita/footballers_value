import datetime
import schedule
import time
from collect_season import main

day_to_run = 1  # run this starting on the 1st
month_to_run = 1  # run this in January (the 1st month)

def job():
    # the task to be executed
    main()

while 1:
    date = datetime.datetime.now()
    if date.day == day_to_run and date.month == month_to_run:
        break  # this breaks out of the while loop if it's the right day.
    else:
        time.sleep(60)  # wait 60 seconds

schedule.every(1).day.do(job)

while True:
	schedule.run_pending()
	time.sleep(1)
