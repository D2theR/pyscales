from django.shortcuts import render
from .models import Chemical
# Create your views here.

def chemical(request):
	return render(request, 'chemical/base.html')