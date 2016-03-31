# coding=utf-8
import hello.views

from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()


# Examples:
# url(r'^$', 'stocktalk.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'^$', hello.views.index, name='index'),
    url(r'^detail/$', hello.views.detail, name='detail'),
    url(r'^detail/(?P<ticker>.+)/$', hello.views.detail, name='detail'),
    url(r'^check/(?P<load_type>[a-zA-Z]+)/(?P<ticker>[a-zA-Z]+)/$', hello.views.test, name="load"),
    url(r'^admin/', include(admin.site.urls)),
]
