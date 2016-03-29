import hello.views

from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()


# Examples:
# url(r'^$', 'stocktalk.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'^$', hello.views.index, name='index'),
    url(r'^search/$', hello.views.search, name='search'),
    url(r'^detail/$', hello.views.detail, name='detail'),
    url(r'^check/(?P<ticker>[a-zA-Z]+)/$', hello.views.test),
    url(r'^admin/', include(admin.site.urls)),
]
