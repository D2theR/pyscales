from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.scale_socks, name='scale_socks'),
]