
import logging
from django_cron import CronJobBase , Schedule

from web.cron import *

logger = logging.getLogger(__name__)

def my_sheduled_job():
    print("the job sheduler stared")


def my_sheduled_30minjob():
    print("the  30 min job sheduler stared")

def my_sheduled_60minjob():
    print("the  60 min job sheduler stared")    