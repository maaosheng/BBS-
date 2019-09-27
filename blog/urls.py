from django.conf.urls import url
from blog import views
urlpatterns = [
    url('add_articledetail',views.add_articledetail),
    url('add_acd/(?P<username>\w+)/(?P<id>\d+)',views.add_acd),
    url('^upload/',views.upload),
    url('^backned/add_article',views.add_article),
    url('^comment',views.comment),
    url('^article_up_down',views.article_up_down,name='up_dowm'),
    url('^category/(?P<username>\w+)/(?P<time>\d+-\d+)',views.category_time),
    url('^category/(?P<username>\w+)/(?P<title>\w+)',views.category_show),
    url('^article/(?P<username>\w+)/(?P<id>\d+)',views.article_detail,),
    url('^(\w+)',views.home),#


]