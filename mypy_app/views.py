from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.shortcuts import render_to_response
from mypy_app.models import add_server
from mypy_app.forms import Add_Server_Form
from mypy_mysqldb import *
from sqlite_operations import *

def adding_server(request):
    context = RequestContext(request)
    if request.method == 'POST':
        form = Add_Server_Form(request.POST)
 
        if form.is_valid():
            #saving the server details in sqlite db
            form.save(commit=True)
            #current_object contains the last entry from the sqlite db
            current_object = add_server.objects.all()[len(add_server.objects.all())-1]
            #calling the connect_to_server method from mypy_mysqldb
            #attempts to connect to the MySQL server and returns the response message
            adding_server_msg = connect_to_server(current_object)
            #if the connection to MySQL server fails, delete this entry from the sqlite db
            if "successful" not in adding_server_msg:
                current_object.delete()
            return render_to_response('mypy_app/add_server.html', 
                    {
                        'form': form, 
                        'add_server_info': adding_server_msg,
                        'server_list': add_server.objects.all()\
                        }, context)
        else:
            #str(form.errors)
            adding_server_msg = ""
            #if the forms.error returns an error about the existence of the server name,
            #adding_server_msg now contains the appropriate msg to be shown in js alert box
            if "already exists" in str(form.errors):
                adding_server_msg = "The server name specified already exists. Please choose another name."

    #if request.method is not post, render the form again
    else:
        form = Add_Server_Form()
        adding_server_msg = ""

    context_dict = {
            'form': form,
            'add_server_info': adding_server_msg,
            'server_list': add_server.objects.all()
            }
    return render_to_response('mypy_app/add_server.html', context_dict , context)



def index(request):
    context = RequestContext(request)
    server_name = ""
    #print "inside index: " + adding_server_msg
    #current_object = add_server.objects.all()[len(add_server.objects.all())-1]
    if request.method == 'POST':
        server_name = request.POST.get("server_details_display_list") 
        print server_name
        #the delete_server_list returns the result as a list from the checkbox
        #containing the name of the mysql_server to be deleted from the sqlite database
        delete_server_list = request.POST.getlist('delete_server_checkbox')
        #print delete_server_list
        #calling delete_server method from sqlite_operations module
        delete_servers(delete_server_list)

    """if request.is_ajax():
        server_name = request.POST.get("server_details_display_list")
        print server_name"""
     
    #building the updated context from the database
    context_dict = {
            'server_list': add_server.objects.all(),
            'data': server_name, 
            }


    return render_to_response('mypy_app/index.html', context_dict, context)


def monitors(request):
    context = RequestContext(request)
    context_dict = {"test_var": "monitors page",}
    return render_to_response('mypy_app/monitors.html', context_dict, context)


def realtime(request):
    context = RequestContext(request)
    context_dict = {"test_var": "realtime page",}
    return render_to_response('mypy_app/realtime.html', context_dict, context)
