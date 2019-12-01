
import logging
from django_cron import CronJobBase , Schedule

from web.cron import *

logger = logging.getLogger(__name__)

class MyCronJob(CronJobBase):
    RUN_EVERY_MINS =1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code='web.cron.update_all_user_feed'
    def do(self):
        logger.info('测试RSS定期任务')




def my_scheduled_job():
    logger.info('测试RSS定期任务,1min')
    update_all_user_feed()
