#-*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import logging
logging.basicConfig()

import time, datetime

# Scheduler interface
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler

class Scheduler(object):

    def __init__(self, bot):
        self.sched = BackgroundScheduler()
        self.sched.start()
        self.bot = bot
        self.job_id = []

    def __del__(self):
        self.shutdown()

    def shutdown(self):
        self.sched.shutdown()

    def kill_scheduler(self, job_id):
        try:
            self.sched.remove_job(job_id)
            if self.job_id.count != 0:
                self.job_id.remove(job_id)
        except JobLookupError as err:
            #print "fail to stop scheduler: %s" % err
            return

    def scheduler(self, type, job_id, myFunc, *args):
        # 스케줄러 중복 방지
        check=True
        for ch in self.job_id:
            if ch == job_id:
                check=False
            else:
                pass

        if check:
            #print "%s Scheduler Start" % type
            if type == 'interval':
                self.sched.add_job(myFunc, type, seconds=10, id=job_id, args=args)
            elif type == 'cron':
                self.sched.add_job(myFunc, type, day_of_week='mon-sat',
                                                    hour='7-20', minute='*/10',
                                                    id=job_id, args=args)
            self.job_id.append(job_id)
        else:
            pass




