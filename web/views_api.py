
from django.http import HttpResponseNotFound, HttpResponseServerError, JsonResponse
#from .models import *
from .models import Article,Site,Message
from datetime import date, timedelta, datetime
from .utils import incr_action, get_subscribe_sites, get_hash_name
from .views_html import get_all_issues
from .verify import verify_request
import logging
import feedparser
import django

logger = logging.getLogger(__name__)

defaultsubmitted=tuple()
defaultunsubmitted=tuple()

@verify_request
def get_lastweek_articles(request):
    """
    过去一周的文章id列表
    """
    #default_sub=['d253a81dcbd138d0b9e275e17e711e18','7eaee5ad5cebcdb9ca29151cb77c6f19','dc74259bf233633f98148ecb0423c754', 'd4acab5a091984c4fa986c3c8c48d5ff', '8c1186f4afd3db1bb6fba8a295e2849c', 'de4e43493bc02ea735d6ef5f841dcdd6']
    #default_unsub=['c2941323f00ad4606e2f76cc472e984b','fe4626441957500dee088f5864015f94', '59ac2d060c62d16daaaceb530155e9c0', '640d9f4046fc002b9df768130bd4e334']
     

    uid = request.POST.get('uid', '')

    sub_feeds = request.POST.get('sub_feeds', '').split(',')
    unsub_feeds = request.POST.get('unsub_feeds', '').split(',')

    ext = request.POST.get('ext', '')

    #sub_feeds =list(set(sub_feeds) - set(default_sub))
    #unsub_feeds=list(set(unsub_feeds) - set(default_unsub))
    logger.info(f"收到订阅源查询请求：`{uid}`{sub_feeds}`{unsub_feeds}`{ext}")

    lastweek_dt = datetime.now() - timedelta(days=7)
    
    my_sub_feeds = get_subscribe_sites(tuple(sub_feeds), tuple(unsub_feeds))


    my_lastweek_articles = list(Article.objects.all().prefetch_related('site').filter(status='active', site__name__in=my_sub_feeds, ctime__gte=lastweek_dt).values_list('uindex', flat=True))
   
    return JsonResponse({"result": my_lastweek_articles})


@verify_request
def add_log_action(request):
    """
    增加文章浏览数据打点
    """
    uindex = request.POST.get('id')
    action = request.POST.get('action')

    if incr_action(action, uindex):
        return JsonResponse({})
    else:
        logger.warning(f"打点增加失败：`{uindex}`{action}")
        return HttpResponseNotFound("Param error")


@verify_request
def leave_a_message(request):
    """
    添加留言
    """
    uid = request.POST.get('uid', '').strip()[:100]

    content = request.POST.get('content', '').strip()[:500]
    nickname = request.POST.get('nickname', '').strip()[:20]
    contact = request.POST.get('contact', '').strip()[:50]

    if uid and content:
        try:
            msg = Message(uid=uid, content=content, nickname=nickname, contact=contact)
            msg.save()
            return get_all_issues(request)
        except:
            logger.error(f"留言增加失败：`{uid}`{content}`{nickname}`{contact}")
            return HttpResponseServerError('Inter error')

    logger.warning(f"参数错误：`{uid}`{content}")
    return HttpResponseNotFound("Param error")


@verify_request
def submit_a_feed(request):
    """
    用户添加一个自定义的订阅源
    """
    feed_url = request.POST.get('url', '').strip()[:200]
    if feed_url:
        feed_obj = feedparser.parse(feed_url)
        #print(type(feed_obj))
        #for entry in feedparser.parse(feed_url).entries:  
        #    print(entry.title)

        if feed_obj.feed.get('title'):
            name = get_hash_name(feed_url)# サイト名をハッシュ掛け
            cname = feed_obj.feed.title[:20]

            if feed_obj.feed.get('link'):
                link = feed_obj.feed.link[:100]
            else:
                link = feed_url

            if feed_obj.feed.get('subtitle'):
                brief = feed_obj.feed.subtitle[:100]
            else:
                brief = cname

            author = feed_obj.feed.get('author', '')[:10]
            favicon = f"https://cdn.v2ex.com/gravatar/{name}?d=monsterid&s=32"

            #site = Site(name=name, cname=cname, link=link, brief=brief, star=9, freq='小时', copyright=30, tag='RSS',creator='user', rss=feed_url, favicon=favicon, author=author)
            #site.save()   
                       
            try:
                site = Site(name=name, cname=cname, link=link, brief=brief, star=9, freq='小时', copyright=30, tag='RSS',creator='user', rss=feed_url, favicon=favicon, author=author)
               # site = Site(name=name, cname=cname, link=link, brief=brief, star=9, freq='小时', status='active',copyright=30, tag='RSS',
               #             creator='user', rss=feed_url, favicon=favicon, author=author,ctime'11',mtime='22',renmark='nothing')            
                site.save()
            except django.db.utils.IntegrityError:
                logger.warning(f"数据插入失败：`{feed_url}")

            return JsonResponse({"name": name})
            
        else:
            logger.warning(f"RSS解析失败：`{feed_url}")
    return HttpResponseNotFound("Param error")
