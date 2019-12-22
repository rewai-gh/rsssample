from django.http import JsonResponse
from django.shortcuts import render
from .utils import *
import logging
import json
from pyecharts import options
from pyecharts.charts import Line, Page, Pie

logger = logging.getLogger(__name__)


def get_xaxis_days(days=60):
    """
    获取 X 坐标，按天。取两个月数据
    """
    xaxis_days = []
    for i in range(0, days):
        xaxis_days.append(time.strftime("%Y%m%d", time.localtime(time.time() - i * 86400)))
    xaxis_days.sort()
    return xaxis_days


def uv_line_chart() -> Line:
    """
    UV折线图，包括总UV、新用户UV
    """
    xaxis = get_xaxis_days()

    uv_all_redis_keys = [settings.REDIS_UV_ALL_KEY % day for day in xaxis]
    uv_new_redis_keys = [settings.REDIS_UV_NEW_KEY % day for day in xaxis]

    uv_all = redis_server.mget(*uv_all_redis_keys)
    uv_new = redis_server.mget(*uv_new_redis_keys)

    line = (
        Line()
        .add_xaxis(xaxis)
        .add_yaxis("总用户数", uv_all, is_connect_nones=True, is_smooth=True)
        .add_yaxis("新用户数", uv_new, is_connect_nones=True, is_smooth=True)
        .set_global_opts(title_opts=options.TitleOpts(title="用户数UV走势"),
                         yaxis_opts=options.AxisOpts(
                             is_scale=True,
                             splitline_opts=options.SplitLineOpts(is_show=True)
                         ),
                         tooltip_opts=options.TooltipOpts(trigger='axis'),
                         )
        .dump_options()
    )
    return line


def refer_pv_line_chart() -> Line:
    """
    UV折线图，外域的每天流量趋势
    """
    xaxis = get_xaxis_days(days=60)

    uv_twitter_redis_keys = [settings.REDIS_REFER_PV_DAY_KEY % ('www.twitter.com', day) for day in xaxis]
    uv_instagram_redis_keys = [settings.REDIS_REFER_PV_DAY_KEY % ('www.instagram.com', day) for day in xaxis]
    uv_bing_redis_keys = [settings.REDIS_REFER_PV_DAY_KEY % ('www.bing.com', day) for day in xaxis]
    uv_facebook_redis_keys = [settings.REDIS_REFER_PV_DAY_KEY % ('www.facebook.com', day) for day in xaxis]
    uv_google_redis_keys = [settings.REDIS_REFER_PV_DAY_KEY % ('www.google.com', day) for day in xaxis]
    uv_qiita_redis_keys = [settings.REDIS_REFER_PV_DAY_KEY % ('www.qiita.com', day) for day in xaxis]
    uv_yahoo_redis_keys = [settings.REDIS_REFER_PV_DAY_KEY % ('www.yahoo.co.jp', day) for day in xaxis]

    """
    uv_zhihu = R.mget(*uv_zhihu_redis_keys)
    uv_ryf = R.mget(*uv_ryf_redis_keys)
    uv_github = R.mget(*uv_github_redis_keys)
    uv_baidu = R.mget(*uv_baidu_redis_keys)
    uv_google = R.mget(*uv_google_redis_keys)
    uv_hao123 = R.mget(*uv_hao123_redis_keys)
    uv_wanqu = R.mget(*uv_wanqu_redis_keys)
    """
    uv_twitter = redis_server.hmget(*uv_twitter_redis_keys)
    uv_instagram = redis_server.hmget(*uv_instagram_redis_keys)
    uv_bing = redis_server.hmget(*uv_bing_redis_keys)
    uv_facebook = redis_server.hmget(*uv_facebook_redis_keys)
    uv_google = redis_server.hmget(*uv_google_redis_keys)
    uv_qiita = redis_server.hmget(*uv_qiita_redis_keys)
    uv_yahoo = redis_server.hmget(*uv_yahoo_redis_keys)


    line = (
        Line()
        .add_xaxis(xaxis)
        .add_yaxis("twitter", uv_twitter, is_connect_nones=True, is_smooth=True)
        .add_yaxis("instagram", uv_instagram, is_connect_nones=True, is_smooth=True)
        .add_yaxis("bing", uv_bing, is_connect_nones=True, is_smooth=True)
        .add_yaxis("facebook", uv_facebook, is_connect_nones=True, is_smooth=True)
        .add_yaxis("google", uv_google, is_connect_nones=True, is_smooth=True)
        .add_yaxis("qiita", uv_qiita, is_connect_nones=True, is_smooth=True)
        .add_yaxis("yahoo", uv_yahoo, is_connect_nones=True, is_smooth=True)
        .set_global_opts(title_opts=options.TitleOpts(title="Referer各域名PV走势"),
                         yaxis_opts=options.AxisOpts(
                             is_scale=True,
                             splitline_opts=options.SplitLineOpts(is_show=True)
                         ),
                         tooltip_opts=options.TooltipOpts(trigger='axis'),
                         )
        .dump_options()
    )
    return line


def refer_pie_chart() -> Pie:
    refer_hosts = list(filter(lambda x: x, redis_server.smembers(settings.REDIS_REFER_ALL_KEY)))
    refer_host_pv_keys = [settings.REDIS_REFER_PV_KEY % host for host in refer_hosts]

    c = (
        Pie()
        .add(
            "",
            [list(z) for z in zip(refer_hosts, redis_server.mget(*refer_host_pv_keys))],
             radius=["30%", "75%"],
             rosetype="radius",
        )
        .set_global_opts(
            title_opts=options.TitleOpts(title="Referer来源占比"),
            legend_opts=options.LegendOpts(
                type_="scroll", pos_left="80%", orient="vertical"
            ),
        )
        .set_series_opts(label_opts=options.LabelOpts(formatter="{b}: {c}"))
        .dump_options()
    )
    return c


def get_uv_chart_data(request):
    return JsonResponse(json.loads(uv_line_chart()))


def get_refer_pie_data(request):
    return JsonResponse(json.loads(refer_pie_chart()))


def get_refer_pv_chart_data(request):
    return JsonResponse(json.loads(refer_pv_line_chart()))


def dashboard(request):
    return render(request, 'dashboard/index.html')
