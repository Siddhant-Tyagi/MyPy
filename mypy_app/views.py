from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from mypy_app.models import add_server
from mypy_app.forms import Add_Server_Form
from mypy_mysqldb import *

def adding_server(request):
    context = RequestContext(request)
    if request.method == 'POST':
        form = Add_Server_Form(request.POST)
 
        if form.is_valid():
            form.save(commit=True)
            current_object = add_server.objects.all()[len(add_server.objects.all())-1]
            adding_server_msg = connect_to_server(current_object)
            if "successful" not in adding_server_msg:
                current_object.delete()
            print adding_server_msg
            #return index(request, adding_server_msg)
            return render_to_response('mypy_app/add_server.html', {'form': form, \
                    'add_server_info': adding_server_msg}, context)
        else:
            print form.errors
            adding_server_msg = ""
    else:
        form = Add_Server_Form()
        adding_server_msg = ""
    print "how come i am here" 
    return render_to_response('mypy_app/add_server.html', {'form': form, \
            'add_server_info': adding_server_msg}, context)



def index(request):
    context = RequestContext(request)
    #print "inside index: " + adding_server_msg
    #current_object = add_server.objects.all()[len(add_server.objects.all())-1]
    if request.method == 'POST':
        delete_server_list = request.POST.getlist('delete_server_checkbox')
        print delete_server_list
    context_dict = {
            'server_list': add_server.objects.all(),
            }

    #if "successful" not in context_dict['add_server_info']:
        #current_object.delete()

    """context_dict = {
            'add_server_info': add_server.objects.all(),
            }"""

    return render_to_response('mypy_app/index.html', context_dict, context)

