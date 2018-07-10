#!/usr/bin/env python

import sys
from datetime import datetime
import os
from time import sleep
from apscheduler.schedulers.blocking import BlockingScheduler
import pollchat_twitterscrape_timed as pt







def main():
    sched = BlockingScheduler()

    job = sched.add_job(pt.run_twitterscrape, 'cron', hour=7, minute=10)
    job_two = sched.add_job(pt.run_twitterscrape, 'cron', hour=20, minute=30)



    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == '__main__':
    main()
