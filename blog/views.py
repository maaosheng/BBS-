from django.shortcuts import render, HttpResponse, redirect
from django.contrib import auth
from PIL import ImageFont, Image, ImageDraw
from blog import models
import random
import json
from django.db.models import Count
import os
from blog import often
from django.urls import reverse


# Create your views here.
# --------------------设置随机图片-------------------！！！
def get_valid_img(request):
    from io import BytesIO
    # /**生成随机颜色**/
    def get_random_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    width = 100
    height = 35
    # /生成图片对象
    im = Image.new(
        'RGB',
        (width, height),
        get_random_color()
    )
    # /生成画笔对象
    draw_obj = ImageDraw.Draw(im)
    # /生成文字对象
    font_obj = ImageFont.truetype('arial.ttf', 23)

    # /生成随机字符串
    tem_list = []
    for i in range(0, 4):
        u = chr(random.randint(65, 90))
        r = chr(random.randint(97, 122))
        l = str(random.randint(0, 9))
        tem = random.choice([u, r, l])
        tem_list.append(tem)
        draw_obj.text((5 + 20 * i, 2), tem, font=font_obj)

    # /绘制干扰点
    for i in range(50):
        xy = (random.randint(0, width), random.randint(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw_obj.point(xy, fill=fill)

    del draw_obj
    request.session['verifycode'] = ''.join(tem_list)
    buf = BytesIO()
    im.save(buf, 'png')
    data = buf.getvalue()
    return HttpResponse(data)


def test(request):
    return render(request, 'ceshi.html')


# !------------------------登录-----------------------------!!!
def login(request):
    if request.method == 'POST':
        res = {'status': 1, 'msg': None}
        user1 = request.POST.get('user')
        pawd = request.POST.get('pawd')
        yzm = request.POST.get('re_pawd')
        yzm_session = request.session.get('verifycode')
        if yzm and yzm.upper() == yzm_session.upper():
            user = auth.authenticate(username=user1, password=pawd)
            if user:
                auth.login(request, user)
                res['msg'] = '/index/'
            else:
                res['status'] = 0
                res['msg'] = '用户名或密码错误'
        else:
            res['status'] = 0
            res['msg'] = '验证码错误'
        return HttpResponse(json.dumps(res))

    return render(request, 'login.html')


# !------------------------resgister-----------------!!!
def logout(request):
    auth.logout(request)
    return redirect('/index/')


# !------------------------resgister-----------------!!!
from blog.forms import RegForm


def resgister(request):
    res = {'status': 1, 'msg': None}
    if request.method == 'POST':
        obj = RegForm(request.POST)
        avatar = request.FILES.get('avatar')
        if obj.is_valid():
            obj.cleaned_data.pop('re_password')
            models.UserInfo.objects.create_user(**obj.cleaned_data, avatar=avatar)
            res['msg'] = "/login/"
        else:
            res['status'] = 0
            res['msg'] = obj.errors
        return HttpResponse(json.dumps(res))
    obj1 = RegForm()
    return render(request, 'resgister.html', {'obj': obj1})


# !------------------------主页面-----------------!!!
def index(request):
    article_list = models.Article.objects.all()
    return render(request, 'index.html', {'article_list': article_list})


# !------------------------个人博客页面-----------------!!!
def home(request, username):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse('404')
    # 如果用户存在，需将TA所写的文章全部取出来
    blog = user.blog
    print(blog)
    # 我的文章列表
    article_list = models.Article.objects.filter(user=user)
    # 我的文章分类一每个分类下的文章个数
    # 将我的文章按照我的分类分组，并统计出每个分类下的文章数
    # article_category = models.Category.objects.filter(blog=blog).values('title').annotate(c=(Count('blog'))).values('title','c')
    # article_category = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values('title', 'c')
    # article_category = models.Category.objects.filter(blog=blog).annotate(c= Count('article')).values('title','c')
    # # select title,sum(blog_id) from .Category groupby(title)
    # # for i in article_category:
    # #     print(i.title,i.article_set.all())
    # # 获取标签分类
    # ret_tag = models.Tag.objects.filter(blog=blog).annotate(c=Count('article')).values('title', 'c')
    # print(ret.article_set.all)

    # 获取时间分类
    # article_date = models.Article.objects.filter(user=user).extra(
    #     select={"achieve": "date_format('2019-06-04 ','%%Y-%%m')"}
    # ).values('achieve').annotate(c=Count('pk')).values('achieve', 'c')
    #
    # print(article_date)
    article_category, ret_tag, article_date = often.Myofen(username, user, blog)

    return render(request, 'home.html',locals())


from django.utils.safestring import mark_safe


def article_detail(request, username, id):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse('404')
    blog = user.blog
    article = models.Article.objects.filter(pk=id).first()
    try:
        article_show = mark_safe(article.articledetail.content)
    except:
        #前往添加文章详情页面
        article_show = mark_safe('你并未为此文章添加详情<button style="color:red" id="add_articledetail">点击前往添加</button>')

    # # ---------------------传入其他对象-------------！！！！！
    # article_category = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values('title', 'c')
    # # for i in article_category:
    # #     print(i.title,i.article_set.all())
    # # 获取标签分类
    # ret_tag = models.Tag.objects.filter(blog=blog).annotate(c=Count('article')).values('title', 'c')
    # # print(ret.article_set.all)
    #
    # # 获取时间分类
    # article_date = models.Article.objects.filter(user=user).extra(
    #     select={"achieve": "date_format(create_time,'%%Y-%%m')"}
    # ).values('achieve').annotate(c=Count('pk')).values('achieve', 'c')
    article_category, ret_tag, article_date = often.Myofen(username,user,blog)

    content_list = models.Comment.objects.filter(article_id=id).all()

    return render(request, 'article_detail.html',locals())
    # 'article_date': article_date,

    # --------------------分类-标签-时间-------------！！！！！


def category_show(request, username, title):
    if title=='c':
        title = title+'++'
    print(title)
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse('404')
    blog = user.blog
    try:
        # ------------------生活分类 - -------------！！！！
        article_list = models.Category.objects.filter(blog=blog, title=title).first().article_set.all()
    except:
        # ------------------技术分类--------------！！！！
        article_list = models.Tag.objects.filter(blog=blog, title=title).first().article_set.all()

    # ---------------------传入其他对象-------------！！！！！
    # article_category = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values('title', 'c')
    # # for i in article_category:
    # #     print(i.title,i.article_set.all())
    # # 获取标签分类
    # ret_tag = models.Tag.objects.filter(blog=blog).annotate(c=Count('article')).values('title', 'c')
    # # print(ret.article_set.all)
    #
    # # 获取时间分类
    # article_date = models.Article.objects.filter(user=user).extra(
    #     select={"achieve": "DATE_FORMAT(create_time,'%%Y-%%m')"}
    # ).values('achieve').annotate(c=Count('pk')).values('achieve', 'c')
    article_category, ret_tag, article_date = often.Myofen(username, user, blog)

    return render(request, 'category_show.html',locals())


def category_time(request, username, time):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse('404')
    blog = user.blog
    article_list1 = []
    time_obj = models.Article.objects.filter(user=user).all()
    for foo in time_obj:
        if time in str(foo.create_time):
            article_list1.append(foo)
    print(article_list1)

    # ---------------------传入其他对象-------------！！！！！
    # article_category = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values('title', 'c')
    # # for i in article_category:
    # #     print(i.title,i.article_set.all())
    # # 获取标签分类
    # ret_tag = models.Tag.objects.filter(blog=blog).annotate(c=Count('article')).values('title', 'c')
    # # print(ret.article_set.all)
    #
    # # 获取时间分类
    # article_date = models.Article.objects.filter(user=user).extra(
    #     select={"achieve": "date_format(create_time,'%%Y-%%m')"}
    # ).values('achieve').annotate(c=Count('pk')).values('achieve', 'c')

    article_category, ret_tag, article_date = often.Myofen(username, user, blog)
    return render(request, 'category_show.html',locals())


from django.db.models import F


def article_up_down(request):


    req = {'statu': 1, 'msg': None}
    user = request.user
    article_id = int(request.POST.get('article_id'))
    is_up = json.loads(request.POST.get('is_up'))
    try:
        models.ArticleUpDown.objects.create(user=user, article_id=article_id, is_up=is_up)
        if is_up:
            models.Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
        else:
            models.Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)
    except:
        req['statu'] = 0
        req['msg'] = models.ArticleUpDown.objects.filter(user=user, article_id=article_id).first().is_up
    return HttpResponse(json.dumps(req))

    # ---------------------传入其他对象-------------！！！！！


from django.http import JsonResponse
from datetime import datetime, timedelta
import time


def comment(request):
    user = request.user
    article_id = request.POST.get('article_id'),
    comment = request.POST.get('comment'),
    parent_comment = request.POST.get('parent_comment')
    article_all = list(models.Comment.objects.all().values('nid', 'content', 'parent_comment', 'user__username'))
    res = {'statu': 1, 'msg': None, 'article_all': article_all}
    if comment[0]:
        print('------------')
        if not parent_comment:
            comment_obj = models.Comment.objects.create(user=user, article_id=article_id[0], content=comment[0])
        else:
            comment_obj = models.Comment.objects.create(user=user, article_id=article_id[0], content=comment[0],
                                                        parent_comment_id=parent_comment)
            res['parent_username'] = comment_obj.parent_comment.user.username
            res['parent_content'] = comment_obj.parent_comment.content
        res['create_date'] = comment_obj.create_time
        res['username'] = request.user.username
        res['comment'] = comment
    else:
        res['statu'] = 0
        res['msg'] = '评论内容不能为空'
    return JsonResponse(res)


# ---------------------添加文章-------------！！！！！

from bs4 import BeautifulSoup


def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title'),
        article_content = request.POST.get('article_content')
        user = request.user
        bs = BeautifulSoup(article_content, 'html.parser')  # <!---------固定格式---------!!!>
        for info in bs.find_all():
            print(info.name, type(info.name))
            if info.name == 'script':
                info.decompose()
        content = bs.text[0:150]
        article_obj_id = models.Article.objects.create(title=title, desc=content, user=user).pk
        models.ArticleDetail.objects.create(content=str(bs), article_id=article_obj_id)
        return HttpResponse('添加成功')
    return render(request, 'add_article.html')


from bbs import settings


def upload(request):
    ret = request.FILES.get('upload_img')
    img_path = os.path.join(settings.MEDIA_ROOT, 'add_article_img', ret.name)
    with open(img_path, 'wb') as f:
        for info in ret:
            f.write(info)
    f.close()
    res = {
        'error': 0,
        'url': '/media/add_article_img/' + ret.name
    }
    return HttpResponse(json.dumps(res))


def test_user(request):
    res = {'status':0,'msg':None}
    username = request.POST.get('name')
    ret = models.UserInfo.objects.filter(username=username).first()
    if  ret:
        res['status'] = 0
        res['msg'] = '用户名重复'
    return HttpResponse(json.dumps(res))


def add_articledetail(request):
    print(1234545)
    req = {'status':1,'msg':None}
    if request.method=='POST':
        username = request.POST.get('username')
        id = request.POST.get('id')
        if username != request.user.username:
            req['status'] = 0
            req['msg'] = '你没有权限操作'
        else:
            detail_url = '/blog/add_acd/%s/%s' % (username,id)
            req['msg'] = detail_url
        return HttpResponse(json.dumps(req))

def add_acd(request,username,id):

    print(username,id,type(id))
    if request.method=='GET':
        article = models.Article.objects.filter(nid=int(id)).first()
        print(article.title)
        return render(request,'add_acd.html',{'article':article})
    else:
        article_content = request.POST.get('article_content')
        models.ArticleDetail.objects.create(content=article_content,article_id =int(id))
        url ='/blog/article/%s/%s'%(username,id)
        return redirect(url)










