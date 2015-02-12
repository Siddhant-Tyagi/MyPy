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
from counters_structure import groups

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
            adding_server_msg, connection_obj = connect_to_server(current_object)
            if connection_obj:
                connection_obj.close()
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


#servers_object = {}

def index(request):
    servers_object = {}
    context = RequestContext(request)
    #check if request method is POST
    if request.method == 'POST':
        #check if request is ajax and return json response
        #this will be used to return MySQL counter's data to the template
        if request.is_ajax():
            if request.POST.get("single_selected_server"):
                server_name = request.POST.get("single_selected_server")
                current_server_obj = add_server.objects.filter(mysql_server_name=server_name)[0]
                #print "current_server_obj " + str(current_server_obj)
                global_var_dict, global_status_dict = get_mysql_data(current_server_obj)
                server_dict = build_server_details_dict(global_var_dict, global_status_dict)
                servers_object[server_name] = server_dict
                return HttpResponse(json.dumps(servers_object))

            else:
                server_list = add_server.objects.all()
                #print server_list
                for current_server_obj in server_list:
                    #print str(current_server_obj.mysql_server_name) + "  " + str(current_server_obj.mysql_host)
                    global_var_dict, global_status_dict = get_mysql_data(current_server_obj)
                    #if global_var_dict == {}:
                        #print current_server_obj.mysql_host
                    server_dict = build_server_details_dict(global_var_dict, global_status_dict)
                    #print server_dict['general_info']['available']
                    servers_object[current_server_obj.mysql_server_name] = server_dict

                return HttpResponse(json.dumps(servers_object))

            """#get the selected checkbox values from jquery
            s1 = request.POST.get("server_list_from_jquery")
            #print type(s1)
            selected_servers_list = json.loads(s1)
            print selected_servers_list
            for e in range(0, len(selected_servers_list)):
                selected_servers_list[e] = str(selected_servers_list[e])
            print selected_servers_list
            #print selected_servers_list
            #check if there are servers in servers_object and selected_servers_list
            global servers_object
            print str(type(servers_object))
            if servers_object != {} and selected_servers_list != []:
                #if its not empty then delete the key value pair from the python's servers
                #object which are not in the present list of selected servers
                servers_to_be_deleted = []
                for server in servers_object:
                    if server not in selected_servers_list:
                        servers_to_be_deleted.append(server)
                for server in servers_to_be_deleted:
                    del servers_object[server]

            #checking if the currently selected server's list is not empty
            if selected_servers_list != []:
                #global servers_object
                #if not then updating the servers object with the relevant data
                for server in selected_servers_list:
                    #print server + "  " + servers_object[server]['general_info']['running_for']
                    if server not in servers_object:
                        print "inside if"
                        #calling the external function and updating the servers_object
                        #this condition is executed when new server checkbox is clicked
                        current_server_obj = add_server.objects.filter(mysql_server_name=server)[0]
                        #print "current_server_obj " + str(current_server_obj)
                        global_var_dict, global_status_dict = get_mysql_data(current_server_obj)
                        #empty dictioanry returned means unable to connect to mysql server
                        #returning n/a for all counters
                        if global_var_dict == {} and global_status_dict == {}:
                            #print "global var dict is empty"
                            server_dict = build_server_details_dict(global_var_dict, global_status_dict)
                            #print server_dict
                            servers_object[istr(server)] = server_dict
                            return HttpResponse(json.dumps(servers_object))
                        #print global_status_dict
                        server_dict = build_server_details_dict(global_var_dict, global_status_dict)
                        servers_object[str(server)] = server_dict
                        #print server + "  " + servers_object[server]['general_info']['running_for']
                        return HttpResponse(json.dumps(servers_object)) 

                    else:
                        #global servers_object
                        print "inside else"
                        #this is executed when the servers checked list is same
                        #and updating the servers_object data after a given data collection interval
                        current_server_obj = add_server.objects.filter(mysql_server_name=server)[0]
                        #print current_server_obj
                        global_var_dict, global_status_dict = get_mysql_data(current_server_obj)
                        if global_var_dict == {} and global_status_dict == {}:
                            #print "global var dict is empty"
                            server_dict = build_server_details_dict(global_var_dict, global_status_dict)
                            #print server_dici
                            #global servers_object
                            servers_object[str(server)] = server_dict
                            return HttpResponse(json.dumps(servers_object))
 
                        server_dict = build_server_details_dict(global_var_dict, global_status_dict)
                        #global servers_object
                        #del servers_object[server]
                        #servers_object[str(server)] = server_dict
                        print servers_object

                        #print "else  " + server + "  " + servers_object[server]['general_info']['running_for']
                        #print "inside loop " + str(hex(id(servers_object)))
                    #servers_object[server] = server_dict
                    #print "for loop:  " + server + "  " + servers_object[server]['general_info']['running_for']
                    #print servers_object
                    if server == selected_servers_list[-1]:
                        return HttpResponse(json.dumps(servers_object)) 
                
                #print servers_object['production_server']['general_info']['running_for']
                #print servers_object['Metabox MySQL server']['general_info']['running_for']
                #print "outside loop  " + str(hex(id(servers_object)))"""
                #return HttpResponse(json.dumps(servers_object)) 

        
        if request.POST['delete_server'] == 'Delete':
            print "inside delete"
            #the delete_server_list returns the result as a list from the checkbox
            #containing the name of the mysql_server to be deleted from the sqlite database
            #s1 = request.POST.get("server_list_from_jquery")
            #delete_server_list = json.loads(s1)
            delete_server_list = request.POST.getlist('selected_server_checkbox')
            #print "inside delete"
            print delete_server_list
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
    #print "inside func"
    #print "inside build server details"
    counter_object = groups()
    counters_dict = counter_object.counters_dict
    if global_var_dict == {}:
        #from counters_structure import counters_dict
        #print "inside if. yes yes yes"
        """for group in counters_dict:
            for counter in group:
                counters_dict[group][counter] = 'n/a'
        counters_dict['general_info']['available'] = 'No'"""
        return counters_dict
    
    
    #resolving general info counters
    general_info = counters_dict['general_info']

    general_info['available'] = "Yes"
    general_info['version'] = global_var_dict['version']
    general_info['running_for'] = convert_time(int(global_status_dict['Uptime']))
    general_info['default_storage_engine'] = global_var_dict['default_storage_engine']
    general_info['innodb_version'] = global_var_dict['innodb_version']
    general_info['performance_schema'] = global_var_dict['performance_schema']
    general_info['uptime_since_flush_status'] = convert_time(int(global_status_dict['Uptime_since_flush_status']))
    
    
    #resolving connection history counters
    connection_history = counters_dict['connection_history']
    connection_history['attempts'] = global_status_dict['Connections']

    connection_history['successful'] = str(int(global_status_dict['Connections']) - 
                                                  int(global_status_dict['Aborted_connects']))
    
    connection_history['percentage_of_max_allowed_reached'] = str("%.2f"
            %(float(global_status_dict['Max_used_connections']) / 
              float(global_var_dict['max_connections']) * 100)) + " %"
    
    connection_history['refused'] = global_status_dict['Aborted_connects']

    connection_history['percentage_of_refused_connections'] = str("%.2f"
            %(float(global_status_dict['Aborted_connects']) /
              float(global_status_dict['Connections']) * 100)) + " %"

    connection_history['terminated_abruptly'] = global_status_dict['Aborted_clients']
    connection_history['bytes_received'] = convert_memory(int(global_status_dict['Bytes_received']))
    connection_history['bytes_sent'] = convert_memory(int(global_status_dict['Bytes_sent']))
    

    #resolving current connection counters
    current_connections = counters_dict['current_connections']
    current_connections['max_allowed'] = global_var_dict['max_connections']
    current_connections['open_connections'] = global_status_dict['Threads_connected']

    current_connections['connection_usage'] = str("%.2f"
            %(float(global_status_dict['Threads_connected']) /
              float(global_var_dict['max_connections']) * 100)) + " %"

    current_connections['running_threads'] = global_status_dict['Threads_running']
    current_connections['concurrent_connections'] = global_status_dict['Max_used_connections']
    current_connections['idle_timeout'] = convert_time(int(global_var_dict['wait_timeout']))
    current_connections['max_interrupts'] = global_var_dict['max_connect_errors']
    current_connections['connect_timeout'] = convert_time(int(global_var_dict['connect_timeout']))
    current_connections['back_log'] = global_var_dict['back_log']

    
    #resolving innodb cache counters


    #print general_info['running_for']
    #counters = resolve_counters(global_var_dict, global_status_dict)
    #print "counters dict:  " + str(counters_dict)
    return counters_dict
