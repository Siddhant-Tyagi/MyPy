from django.http import HttpResponse
import json
from threading import Thread
import Queue
from django.template import RequestContext
from django.shortcuts import render_to_response
from mypy_app.models import add_server
from mypy_app.forms import Add_Server_Form
from mypy_mysqldb import *
from sqlite_operations import *
from utility import *
from counters_structure import groups
from math import ceil
import time
from mypy_app.mypy_mysqldb import get_mysql_data


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
            #if "successful" not in adding_server_msg:
            #current_object.delete()
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
    t1 = 0.00
    context = RequestContext(request)
    #check if request method is POST
    if request.method == 'POST':
        #check if request is ajax and return json response
        #this will be used to return MySQL counter's data to the template
        if request.is_ajax():
            #fires an event when the server checkbox is checked
            if request.POST.get("single_selected_server"):
                server_name = request.POST.get("single_selected_server")
                #get the details of the current server from sqlite db
                current_server_obj = add_server.objects.filter(mysql_server_name=server_name)[0]
                #initialing a thread safe queue for storing the server details
                single_server_queue = Queue.Queue()
                #spawning a thread with the current mysql credentials from the sqlite database
                #this thread creates a new connection and get the mysql details
                connection_thread = Thread(target=get_mysql_data, args=(current_server_obj, single_server_queue))
                connection_thread.start()
                #wait for the thread to return
                connection_thread.join()
                #getting the dictionary of the global variables, status and slave status 
                current_server_data = single_server_queue.get()
                #structure of the dictionary is:
                # { 'Server_name': {
                #                   'global_var_dict': {},
                #                   'global_status_dict': {},
                #                   'slave_status_dict': {},
                #                   }
                # }
                
                #building the counters value dict from the mysql data
                server_dict = build_server_details_dict(
                                            current_server_data[current_server_data.keys()[0]]['global_var_dict'],
                                            current_server_data[current_server_data.keys()[0]]['global_status_dict'],
                                            current_server_data[current_server_data.keys()[0]]['slave_status_dict']
                                        )
                
                servers_object[current_server_data.keys()[0]] = server_dict
                return HttpResponse(json.dumps(servers_object))
            
            #enters else every other data collection interval and resolves all the servers in sqlite database
            else:
                server_list = add_server.objects.all()
                server_info_queue = Queue.Queue()
                thread_list = []
                start_time = time.time()
                for current_server_obj in server_list:
                    #start_time = time.time()
                    connection_thread = Thread(target=get_mysql_data, args=(current_server_obj, server_info_queue))
                    connection_thread.start()
                    thread_list.append(connection_thread)
                
                for thread in thread_list:
                    thread.join()
                print "Time taken: " + str(time.time() - start_time)
                for _ in xrange(len(server_list)):
                    current_server_data = server_info_queue.get()
                    #print str(current_server_obj.mysql_server_name) + "  " + str(current_server_obj.mysql_host)
                    #global_var_dict, global_status_dict, slave_status_dict = get_mysql_data(current_server_obj)
                    #t1 += time.time() - start_time
                    #if global_var_dict == {}:
                        #print current_server_obj.mysql_host
                    server_dict = build_server_details_dict(
                                            current_server_data[current_server_data.keys()[0]]['global_var_dict'],
                                            current_server_data[current_server_data.keys()[0]]['global_status_dict'],
                                            current_server_data[current_server_data.keys()[0]]['slave_status_dict']
                                        )
                    #print server_dict['general_info']['available']
                    servers_object[current_server_data.keys()[0]] = server_dict
                    
                #print t1
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

def build_server_details_dict(global_var_dict, global_status_dict, slave_status_dict):
    #global t1
    #start_time = time.time()
    #print "inside func"
    #print "inside build server details"
    counter_object = groups()
    counters_dict = counter_object.counters_dict
    if global_var_dict == {}:
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
    innodb_cache = counters_dict['innodb_cache']
    innodb_cache['innodb_buffer'] = convert_memory(int(global_var_dict['innodb_buffer_pool_size']))
    innodb_cache['innodb_instances'] = global_var_dict['innodb_buffer_pool_instances']
    
    #innodb free memory
    innodb_pages_data = int(global_status_dict['Innodb_buffer_pool_pages_data'])
    innodb_pages_free = int(global_status_dict['Innodb_buffer_pool_pages_free'])
        
    page_size = float(global_var_dict['innodb_buffer_pool_size'])/float(global_status_dict['Innodb_buffer_pool_pages_total'])
    if innodb_pages_data>0:
        innodb_cache['free_memory'] = convert_memory(page_size*innodb_pages_free)

    innodb_cache['cache_blocks'] = convert_memory(int(global_status_dict['Innodb_buffer_pool_read_requests']))
    innodb_cache['cache_misses'] = global_status_dict['Innodb_buffer_pool_reads']
    
    innodb_cache['cache_hit_ratio'] = str("%.2f"
           %(float(global_status_dict['Innodb_buffer_pool_reads']) /
             float(global_status_dict['Innodb_buffer_pool_read_requests']) * 100)) + " %"

    innodb_cache['cache_write_wait'] = str("%.2f"
            %(float(global_status_dict['Innodb_buffer_pool_wait_free']) /
              float(global_status_dict['Innodb_buffer_pool_write_requests'])))

    innodb_cache['adtl_pool_size'] = convert_memory(int(global_var_dict['innodb_additional_mem_pool_size']))
    innodb_cache['free_page_waits'] = global_status_dict['Innodb_buffer_pool_wait_free']
    innodb_cache['buffer_max_size'] = global_var_dict['innodb_change_buffer_max_size']

    #resolving threads counter
    threads = counters_dict['threads']
    threads['thread_cache_size'] = global_var_dict['thread_cache_size']
    threads['threads_cached'] = global_status_dict['Threads_cached']
    threads['threads_created'] = global_status_dict['Threads_created']
    
    #cache hit rate
    created = int(threads['threads_created'])
    conns = int(global_status_dict['Connections'])
    if created > conns:
        threads['cache_hit_rate'] = '100'
    else:
        threads['cache_hit_rate'] = str((1-(created/conns)) * 100) + " %"

    threads['slow_launch_time'] = global_var_dict['slow_launch_time']
    threads['slow_launch_threads'] = global_status_dict['Slow_launch_threads']

    #resolving query cache counters
    query_cache = counters_dict['query_cache']
    query_cache['enabled'] = global_var_dict['have_query_cache']
    query_cache['type'] = global_var_dict['query_cache_type']
    query_cache['cache_size'] = convert_memory(int(global_var_dict['query_cache_size']))
    query_cache['max_size'] = convert_memory(int(global_var_dict['query_cache_limit']))
    query_cache['free_memory'] = convert_memory(int(global_status_dict['Qcache_free_memory']))
    query_cache['query_buffer'] = convert_memory(int(global_var_dict['query_prealloc_size']))
    query_cache['block_size'] = convert_memory(int(global_var_dict['query_cache_min_res_unit']))
    query_cache['total_blocks'] = global_status_dict['Qcache_total_blocks']
    query_cache['free_blocks'] = global_status_dict['Qcache_free_blocks']

    query_cache['fragmentation'] = str("%.2f"
            %(float(global_status_dict['Qcache_free_blocks']) /
              float(ceil((float(global_status_dict['Qcache_total_blocks'])) /2 )) * 100 )) + " %"
   
    query_cache['query_cache'] = global_status_dict['Qcache_queries_in_cache']
    query_cache['query_not_cached'] = global_status_dict['Qcache_not_cached']
    query_cache['cache_misses'] = global_status_dict['Qcache_inserts']
    query_cache['cache_hits'] = global_status_dict['Qcache_hits']
    
    try:
        query_cache['cache_hit_ratio'] = str("%.2f"
            %(float(global_status_dict['Qcache_hits'])/
            (float(global_status_dict['Qcache_inserts']) + float(global_status_dict['Qcache_hits']))
            * 100)) + " %"
    except:
        query_cache['cache_hit_ratio'] = "0 %"
    
    query_cache['queries_pruned'] = global_status_dict['Qcache_lowmem_prunes']
    
    try:
        query_cache['pruned_percentage'] = str("%.2f"
                %(float(global_status_dict['Qcache_lowmem_prunes']) /
                  float(global_status_dict['Qcache_inserts']) * 100)) + " %"
    except:
        query_cache['pruned_percentage'] = "0.00 %"

    #resolving index usage counters
    index_usage = counters_dict['index_usage']

    #full table scan
    numerator = int(global_status_dict['Handler_read_rnd']) + int(global_status_dict['Handler_read_rnd_next'])
    denominator = numerator + int(global_status_dict['Handler_read_first']) + int(global_status_dict['Handler_read_next']) + int(global_status_dict['Handler_read_key']) + int(global_status_dict['Handler_read_prev'])
    try:
        index_usage['full_table_scans'] = str("%.2f"
                %(float(numerator) / float(denominator) * 100)) + " %"
    except:
        index_usage['full_table_scans'] = "0.00 %"

    index_usage['buffer'] = convert_memory(int(global_var_dict['read_buffer_size']))
    index_usage['select_scans'] = global_status_dict['Select_scan']
    index_usage['buffer_joins'] = global_var_dict['join_buffer_size']
    index_usage['joins_required'] = global_status_dict['Select_full_join']
    index_usage['joins_revaluate'] = global_status_dict['Select_range_check']

    #resolving statements counters
    statements = counters_dict['statements']
    statements['all'] = global_status_dict['Questions']
    try:
        statements['selects'] = str(int(global_status_dict['Com_select']) + int(global_status_dict['Qcache_hits']))
    except:
        statements['selects'] = "0.00"
        
    try:
        statements['inserts'] = str("%.2f"
                    %(float(global_status_dict['Com_insert']) + float(global_status_dict['Com_replace']))
                    / float(global_status_dict['Questions']))
    except:
        statements['inserts'] = "0.00"
    
    try:
        statements['updates'] = str("%.2f"
                    %(float(global_status_dict['Com_update']) / float(global_status_dict['Questions'])))
    except:
        statements['updates'] = "0.00"
    
    try:
        statements['deletes'] = str("%.2f"
                    %(float(global_status_dict['Com_delete']) / float(global_status_dict['Questions'])))
    except:
        statements['delete'] = "0.00"
    
    
    statements['dms'] = str(float(statements['selects']) + float(statements['inserts']) + float(statements['updates']) +
                             float(statements['deletes']))
                        
    statements['rows'] = str("%.2f"
                %(float(global_status_dict['Handler_read_first']) + float(global_status_dict['Handler_read_key'])
                  + float(global_status_dict['Handler_read_next']) + float(global_status_dict['Handler_read_prev']) +
                  float(global_status_dict['Handler_read_rnd']) + float(global_status_dict['Handler_read_rnd_next'])
                  + float(global_status_dict['Sort_rows'])))
    
    statements['rows_index'] = str("%.2f"
            %(float(global_status_dict['Handler_read_first']) + float(global_status_dict['Handler_read_key']) + 
              float(global_status_dict['Handler_read_next']) + float(global_status_dict['Handler_read_prev'])))
    
    try:
        statements['avg_rows'] = str("%.2f"
                    %(float(statements['rows']) / float(global_status_dict['Questions'])))
    except:
        statements['avg_rows'] = "0.00"
    
    statements['rows_percentage'] = str("%.2f"
                %(float(statements['rows_index']) / float(statements['rows']) * 100)) + " %"
    
    statements['max_prepared'] = global_var_dict['max_prepared_stmt_count']
    
    #t1 += (time.time() - start_time)
    
    #resolving replication counters
    if slave_status_dict != {}:
        replication = counters_dict['replication']
        if global_status_dict['Slave_running']=="ON": replication['running'] = "Yes"
        replication['read_only'] = global_var_dict['read_only'] 
        replication['io_running'] = slave_status_dict['Slave_IO_Running']
        replication['io_state'] = slave_status_dict['Slave_IO_State']
        replication['slave_sql'] = slave_status_dict['Slave_SQL_Running']
        replication['sbm'] = slave_status_dict['Seconds_Behind_Master']
        replication['skip'] = global_var_dict['slave_skip_errors']
        replication['err_no'] = slave_status_dict['Last_Errno']
        if len(slave_status_dict['Last_Error']) > 0: replication['err_msg'] = slave_status_dict['Last_Error']
        if len(slave_status_dict['Last_IO_Error']) > 0: replication['io_err'] = slave_status_dict['Last_IO_Error']
        replication['ntw_timeout'] = convert_time(int(global_var_dict['slave_net_timeout']))
        replication['trsc_count'] = global_status_dict['Slave_retried_transactions']
        replication['m_host'] = slave_status_dict['Master_Host']
        replication['m_port'] = slave_status_dict['Master_Port']
        replication['m_user'] = slave_status_dict['Master_User'] 
        replication['mlog_file'] = slave_status_dict['Master_Log_File']
        replication['mlog_read_pos'] = slave_status_dict['Read_Master_Log_Pos']
        replication['rm_log'] = slave_status_dict['Relay_Master_Log_File']
        replication['rm_log_pos'] = slave_status_dict['Exec_Master_Log_Pos']
        replication['rlog'] = slave_status_dict['Relay_Log_File']
        replication['rlog_pos'] = slave_status_dict['Relay_Log_Pos'] 
        
      
    #print general_info['running_for']
    #counters = resolve_counters(global_var_dict, global_status_dict)
    #print "counters dict:  " + str(counters_dict)
    return counters_dict
