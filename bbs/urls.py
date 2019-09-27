"""bbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url,include
from blog import views
from django.views.static import serve
from bbs import settings
from blog import urls as blog_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    url('^get_valid_img?', views.get_valid_img),
    url('^resgister/', views.resgister),
    url('^login/', views.login),
    url('^index/', views.index),
    url('^logout/', views.logout),
    url('^media/(?P<path>.*)$',serve,{"document_root":settings.MEDIA_ROOT}),#media相关得路由


    url('^blog/',include(blog_urls)),#将所有以blog开头的urlq请求都交给blog下边处理,
    # url('^blog/',include(blog_urls)),#将所有以blog开头的urlq请求都交给blog下边处理,

    url('^test_user/',views.test_user)

]
