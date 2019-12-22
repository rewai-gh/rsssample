
from django.core.management.base import BaseCommand
from django.utils import timezone

import feedparser
from feed.utils import current_ts
import logging
import django
from datetime import datetime
from django.utils.timezone import timedelta
from web.models import Article,Site






logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        time = timezone.now().strftime('%X')
        self.stdout.write("It's now %s" % time)
        """
        清除历史数据
        :return:
        """
        logger.info('开始清理历史数据')
        last1day = datetime.now() - timedelta(days=1)
        Article.objects.all().prefetch_related('site').filter(ctime__lte=last1day).delete()

        logger.info('历史数据清理完毕')



