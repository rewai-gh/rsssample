
from django.core.management.base import BaseCommand
from django.utils import timezone

import feedparser
from feed.utils import current_ts
import logging
import django
from datetime import datetime
#from .views_html import *
from web.models import Article,Site




logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        time = timezone.now().strftime('%X')
        self.stdout.write("It's now %s" % time)
        logger.info("the job sheduler stared")

        logger.info('开始运行定时更新RSS任务')
        now = datetime.now()
        if now.hour % 4 == 0:
            feeds = Site.objects.filter(status='active', creator='user').order_by('-star')
        elif now.hour % 4 == 1:
            feeds =feeds = Site.objects.filter(status='active', creator='user',star__gte=50).order_by('-star')
        elif now.hour % 4 == 2:
            feeds = Site.objects.filter(status='active', creator='user', star__gte=20).order_by('-star')
        elif now.hour % 4 == 3:
            feeds = Site.objects.filter(status='active', creator='user', star__gte=9).order_by('-star')

        feeds = Site.objects.filter(status='active', creator='user', star__gte=9).order_by('-star')

        for site in feeds:

            logger.info(f"RSS源`{site.rss}")

            feed_obj=feedparser.parse(site.rss)
            logger.info('定时更新RSS任务运行结束')

            for entry in feed_obj.entries[:10]:
                try:
                    title = entry.title
                    link = entry.link
                    #logger.info(f"RSS源`{title}")
                except AttributeError:
                    logger.warning(f'必要属性获取失败：`{site.rss}')
                    continue

           # if is_crawled_url(link):
           #     continue

                try:
                    author = entry['author'][:11]
                    logger.info(f"RSS源数据author`{author}")
                except:
                    author = None
                    #logger.info(f"RSS源数据author`{author}")

                try:
                    value = entry.content[0].value
                except:
                    value = entry.get('description') or entry.link


                

                try:
                    article = Article(site=site, title=title, author=author, src_url=link, uindex=current_ts(), content=value)
                    article.save()
                #mark_crawled_url(link)

                except django.db.utils.IntegrityError:
                    logger.info(f'数据重复插入：`{title}`{link}')
                except:
                    logger.warning(f'数据插入异常：`{title}`{link}')

        logger.info('定时更新RSS任务运行结束')



