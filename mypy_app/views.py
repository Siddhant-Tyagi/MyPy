from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.shortcuts import render_to_response
from mypy_app.models import add_server
from mypy_app.forms import Add_Server_Form
from mypy_mysqldb import *
from sqlite_operations import *
from utility import *

servers_object = {}

def adding_server(request):
    context = RequestContext(request)
    if request.method == 'POST':
        form = Add_Server_Form(request.POST)
 
        if form.is_valid():
            #saving the server details in sqlite db
            form.save(commit=True)
            #current_object contains the last entry from the sqlite db which is the current server object
            current_object = add_server.objects.all()[len(add_server.objects.all())-1]
            #calling the connect_to_server method from mypy_mysqldb
            #takes in the current server object as a parameter
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
    #check if request method is POST
    if request.method == 'POST':
        #check if request is ajax and return json response
        #this will be used to return MySQL counter's data to the template
        if request.is_ajax():
            #get the selected checkbox values from jquery
            s1 = request.POST.get("server_list_from_jquery")
            #print type(s1)
            selected_servers_list = json.loads(s1)
            #print selected_servers_list
            #check if there are servers in servers_object and selected_servers_list
            if servers_object != {} and selected_servers_list != []:
                #if its not empty then delete the key value pair from the python's servers
                #object which are not in the present list of selected servers
                servers_to_be_deleted = []
                for server in servers_object:
                    if server not in selected_servers_list:
                        servers_to_be_deleted_list.append(server)
                for server in servers_to_be_deleted:
                    del servers_object[server]

            #checking if the currently selected server's list is not empty
            if selected_servers_list != []:
                #if not then updating the servers object with the relevant data
                for server in selected_servers_list:
                    #print server
                    if server not in servers_object:
                        #print "inside if"
                        #calling the external function and updating the servers_object
                        #this condition is executed when new server checkbox is clicked
                        current_server_obj = add_server.objects.filter(mysql_server_name=server)[0]
                        print "current_server_obj " + str(current_server_obj)
                        global_var_dict, global_status_dict = get_mysql_data(current_server_obj)
                        if global_var_dict == {} and global_status_dict == {}:
                            #print "global var dict is empty"
                            server_dict = build_server_details_dict(global_var_dict, global_status_dict)
                            #print server_dict
                            servers_object[server] = server_dict
                            return HttpResponse(json.dumps(servers_object))
                        #print global_var_dict
                        server_dict = build_server_details_dict(global_var_dict, global_status_dict)
                        servers_object[server] = server_dict
                        #print servers_object
                        return HttpResponse(json.dumps(servers_object)) 

                    else:
                        print "inside else"
                        #this is executed when the servers checked list is same
                        #and updating the servers_object data after a given data collection interval
                        current_server_obj = add_server.objects.filter(mysql_server_name=server)[0]
                        #print current_server_obj
                        global_var_dict, global_status_dict = get_mysql_data(current_server_obj)
                        server_dict = build_server_details_dict(global_var_dict, global_status_dict)
                        servers_object[server] = server_dict 


            return HttpResponse(json.dumps(servers_object)) 

            """#returns the server name selected one at a time from the list of checkbox
            server_name = request.POST.get("server_details_display_list")
            current_server_obj = add_server.objects.filter(mysql_server_name=server_name)[0]
            print current_server_obj
            global_var_dict = get_mysql_data(current_server_obj)
            #builds the dictionary data type to be passed as json response
            #this dict contains the various MySQL counters
            json_data = {
                          'server_name': server_name,

                          'general_info': {
                                           'available': 'yes yes', 
                                           'version': '5.6.14',
                                           'running_for': '5 hours',
                                           'start_time': '11 PM',
                                           'default_storage_engine': 'InnoDB',
                                           'innodb_version': '5.6',
                                         },

                          'connection_history': {
                                                 'attempts': '24',
                                                 'successful': '22',
                                                 'percentage_of_max_allowed_reached': '10',
                                                 'refused': '2',
                                                 'percentage_of_refused_connections': '5',
                                                 'terminated_abruptly': '0',
                                                },
                        }
            #json.dumps converts the dictionary data type to JSON response
            return HttpResponse(json.dumps(json_data))"""
        
        #deletes the server(s) selected from the SQLite database
        if request.POST['delete_server'] == 'Delete':
            #the delete_server_list returns the result as a list from the checkbox
            #containing the name of the mysql_server to be deleted from the sqlite database
            delete_server_list = request.POST.getlist('delete_server_checkbox')
            #print delete_server_list
            #calling delete_server method from sqlite_operations module
            delete_servers(delete_server_list)
            context_dict = {
                    'server_list': add_server.objects.all(),
                    }
            return render_to_response('mypy_app/index.html', context_dict, context) 
        
     
    #building the updated context from the database
    context_dict = {
            'server_list': add_server.objects.all(), 
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

def build_server_details_dict(global_var_dict, global_status_dict):
    from counters_structure import counters_dict
    #print counters_dict
    if global_var_dict == {}:
        return counters_dict

    #resolving general info counters

    #calulating running for period
    running_for = covert_time(int(global_status_dict['Uptime']))


    general_info = counters_structure['general_info']
    general_info['available'] = "Yes"
    general_info['version'] = global_var_dict['version']
    general_info['running_for'] = 
    #counters = resolve_counters(global_var_dict, global_status_dict)
    """counters_dict = {

                     'general_info': {
                                      'available': global_status_dict['Uptime'], 
                                      'version': '5.6.14',
                                      'running_for': '5 hours',
                                      'start_time': '11 PM',
                                      'default_storage_engine': 'InnoDB',
                                      'innodb_version': '5.6',
                                    },

                     'connection_history': {
                                            'attempts': '24',
                                            'successful': '22',
                                            'percentage_of_max_allowed_reached': '10',
                                            'refused': '2',
                                            'percentage_of_refused_connections': '5',
                                            'terminated_abruptly': '0',
                                           },
                    }
    #print "counters dict:  " + str(counters_dict)"""
    return counters_dict

def resolve_counters(global_var_dict, global_status_dict):
    resolved_counters_dict = {
                               'general_info': {},
                               'connection_history': {},
                             }
    
    #resolving general info counters


