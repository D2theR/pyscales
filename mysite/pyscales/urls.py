from django.conf.urls import url
from .views import log_in, log_out, sign_up, scale_socks

urlpatterns = [
	url(r'^log_in/$', log_in, name='log_in'),
    url(r'^log_out/$', log_out, name='log_out'),
    url(r'^sign_up/$', sign_up, name='sign_up'),
	url(r'^$', scale_socks, name='scale_socks'),
]