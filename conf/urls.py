from django.conf.urls import patterns, include, url
from django.contrib import admin

from ikwen.flatpages.views import FlatPageView
from ikwen.core.views import DefaultHome

from website.views import Kakocase, PinsView, About, Terms


from ikwen_foulassi.foulassi.views import EventList

from dbbackup.views import Home

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^laakam/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    # url(r'^$', DefaultHome.as_view(), name='home'),
    url(r'^billing/', include('ikwen.billing.urls', namespace='billing')),
    url(r'^cashout/', include('ikwen.cashout.urls', namespace='cashout')),
    url(r'^retail/', include('ikwen.partnership.urls', namespace='partnership')),
    url(r'^theming/', include('ikwen.theming.urls', namespace='theming')),
    url(r'^rewarding/', include('ikwen.rewarding.urls', namespace='rewarding')),
    url(r'^revival/', include('ikwen.revival.urls', namespace='revival')),
    url(r'^kakocase/', include('ikwen_kakocase.kakocase.urls', namespace='kakocase')),
    url(r'^shavida/', include('ikwen_shavida.shavida.urls', namespace='shavida')),
    url(r'^web/', include('ikwen_webnode.web.urls', namespace='web')),
    url(r'^foulassi/', include('ikwen_foulassi.foulassi.urls', namespace='foulassi')),
    url(r'^page/(?P<url>[-\w]+)/$', FlatPageView.as_view(), name='flatpage'),
    url(r'^echo/', include('echo.urls', namespace='echo')),
    url(r'^ikwen/', include('ikwen.core.urls', namespace='ikwen')),
    url(r'^kakocase/', Kakocase.as_view(), name='kakocase'),
    url(r'^pinsview/', PinsView.as_view(), name='pinsview'),
    url(r'^about/', About.as_view(), name='about'),
    url(r'^terms/', Terms.as_view(), name='terms_and_conditions'),
    url(r'^webnode/', include('ikwen_webnode.webnode.urls', namespace='webnode')),
    url(r'^daraja/', include('daraja.urls', namespace='daraja')),
    url(r'^$', Home.as_view(), name='home'),
    url(r'^', include('dbbackup.urls', namespace='dbbackup')),
)
