#!/usr/bin/env python

import sys
from datetime import datetime
import os
from time import sleep
from apscheduler.schedulers.blocking import BlockingScheduler
import pollchat_twitterscrape_timed as pt
import app.graph_functions as gf







def main():
    sched = BlockingScheduler()

    job = sched.add_job(pt.run_twitterscrape, 'cron', hour=7, minute=45,\
    id='scrape_one', replace_existing=True)
    job_two = sched.add_job(pt.run_twitterscrape, 'cron', hour=21, minute=30, \
    id='scrape_two', replace_existing=True)
    job_three = sched.add_job(gf.fill_graphs, 'cron', hour=0, minute=1, \
    id='fill_graphs_timed', replace_existing=True)



    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == '__main__':
    main()
