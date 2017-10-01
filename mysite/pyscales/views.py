from django.shortcuts import render

# Create your views here.
def scale_socks(request):
	return render(request, 'pyscales/scale_socket.html')

