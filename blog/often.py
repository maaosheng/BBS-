from blog import models
from django.shortcuts import  HttpResponse
from django.db.models import Count
def Myofen(username,user,blog):

    article_category = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values('title', 'c')
    # for i in article_category:
    #     print(i.title,i.article_set.all())
    # 获取标签分类
    ret_tag = models.Tag.objects.filter(blog=blog).annotate(c=Count('article')).values('title', 'c')
    # print(ret.article_set.all)

    # 获取时间分类e
    article_date = models.Article.objects.filter(user=user).extra(
        select={"achieve": "date_format(create_time,'%%Y-%%m')"}
    ).values('achieve').annotate(c=Count('pk')).values('achieve', 'c')
    # print(article_date   )
    return article_category, ret_tag ,article_date
