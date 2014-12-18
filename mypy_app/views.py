from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

def index(request):
    context = RequestContext(request)
    context_dict = {
            'boldmessage': "Message from index view",
            }
    return render_to_response('mypy_app/index.html', context_dict, context)

def about(request):
    return HttpResponse("<html> <body> <a href='/mypy/'>Home Page</a></body></html>")
