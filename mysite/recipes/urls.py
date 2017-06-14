from django.conf.urls import url
from . import views

urlpatters = [
	url(r'^recipes/', views.test_list, name='test_list'),
]