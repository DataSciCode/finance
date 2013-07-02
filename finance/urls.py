from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('finance.views',
    # Examples:
    # url(r'^$', 'finance.views.home', name='home'),
    # url(r'^finance/', include('finance.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'home'),
    url(r'^api/v1/snapshots$', 'snapshots'),
    url(r'^api/v1/stocks/(?P<snapshot>\d+)$', 'stocks'),
)

urlpatterns += staticfiles_urlpatterns()
