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
        
        #when the form is submitted
        if form.is_valid():
            print "inside form"
            #saving the server details in sqlite db
            print form.data['original_server_name']
            form.save(commit=True)
            #current_object contains the last entry from the sqlite db which is the current server object
            current_object = add_server.objects.all()[len(add_server.objects.all())-1]
            print current_object
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
        
        #if form is not valid
        else:
            print "inside form"
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
    
    print "inside get"
    context_dict = {
            'form': form,
            'add_server_info': adding_server_msg,
            'server_list': add_server.objects.all()
            }
    return render_to_response('mypy_app/add_server.html', context_dict , context)

#original_server_name = ""

def edit_server(request):
    context = RequestContext(request)
           
    #fires the edit server window
    if request.is_ajax():
        #print "inside ajax"
        server_name = request.POST.get('server_name')
        #print server_name
        # request.POST.get('csrfmiddlewaretoken')
        obj = add_server.objects.filter(mysql_server_name=server_name)[0]
        server_details = {key: value for (key,value) in vars(obj).iteritems() if 'mysql' in key}                  
        return HttpResponse(json.dumps(server_details))
    
        
    if request.method == 'POST':
        form = Add_Server_Form(request.POST)
        #print form.data['original_server_name']
        #print request.POST.get('original_server_name')
        #when the form is submitted and is valid i.e. server name is different than the one present in the db    
        if form.is_valid():
            #print "inside if"
            #server_name = request.POST.get('original_server_name')
            #print "inside : "  + s1
            server_obj = add_server.objects.get(mysql_server_name=form.data['original_server_name'])
            for current_field in vars(server_obj):
                try:
                    server_obj.__dict__[current_field] = form.data[current_field]
                except:
                    pass
            #print server_obj
            server_obj.save()
            #saving the server details in sqlite db
            #form.save(commit=True)
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
            return render_to_response('mypy_app/edit_server.html', 
                      {
                        'form': form, 
                        'add_server_info': adding_server_msg,
                      }, context)
        
        #if form is not valid(when the server name is the same as earlier)
        else:
            #print "inside else"
            server_name =  form.data['mysql_server_name']
            #fetching the respective server object from models
            server_obj = add_server.objects.get(mysql_server_name=server_name)
            #updating the details of each field in the server object
            #the form.data dictionary doesn't contain any entry of the server name
            for current_field in vars(server_obj):
                try:
                    server_obj.__dict__[current_field] = form.data[current_field]
                except:
                    pass
            #saving the updated models object to the database
            server_obj.save()
            adding_server_msg, connection_obj = connect_to_server(server_obj)
            if connection_obj:
                connection_obj.close()
            return render_to_response('mypy_app/edit_server.html', 
                      {
                        'form': form, 
                        'add_server_info': adding_server_msg,
                      }, context)

    #if request.method is not post, render the form again
    else:
        form = Add_Server_Form()
        adding_server_msg = ""
    
    context_dict = {
            'form': form,
            'add_server_info': adding_server_msg,
            }
    return render_to_response('mypy_app/edit_server.html', context_dict , context)
        


def index(request):
    #initializing the server's object dictionary
    #this will be passed as the JSON response to the AJAX data collection request
    servers_object = {}

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
                
                #mapping server in the server object dict with its counter's dict 
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


def build_server_details_dict(global_var_dict, global_status_dict, slave_status_dict):
    #initializing counters dictionary from the groups class constructor
    counter_object = groups()
    counters_dict = counter_object.counters_dict
    
    #if the get_mysql_data method returns an empty dictionary
    #it means that connection to the MySQL server was unsuccessful 
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
    try:
        connection_history['percentage_of_max_allowed_reached'] = str("%.2f"
            %(float(global_status_dict['Max_used_connections']) / 
              float(global_var_dict['max_connections']) * 100)) + " %"
    except:
        pass
    
    connection_history['refused'] = global_status_dict['Aborted_connects']

    try:
        connection_history['percentage_of_refused_connections'] = str("%.2f"
            %(float(global_status_dict['Aborted_connects']) /
              float(global_status_dict['Connections']) * 100)) + " %"
    except:
        pass

    connection_history['terminated_abruptly'] = global_status_dict['Aborted_clients']
    connection_history['bytes_received'] = convert_memory(int(global_status_dict['Bytes_received']))
    connection_history['bytes_sent'] = convert_memory(int(global_status_dict['Bytes_sent']))
    

    #resolving current connection counters
    current_connections = counters_dict['current_connections']
    current_connections['max_allowed'] = global_var_dict['max_connections']
    current_connections['open_connections'] = global_status_dict['Threads_connected']

    try:
        current_connections['connection_usage'] = str("%.2f"
            %(float(global_status_dict['Threads_connected']) /
              float(global_var_dict['max_connections']) * 100)) + " %"
    except:
        pass
    
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
    try:    
        page_size = float(global_var_dict['innodb_buffer_pool_size'])/float(global_status_dict['Innodb_buffer_pool_pages_total'])
        if innodb_pages_data>0:
            innodb_cache['free_memory'] = convert_memory(page_size*innodb_pages_free)
    except:
        pass
    
    innodb_cache['cache_blocks'] = convert_memory(int(global_status_dict['Innodb_buffer_pool_read_requests']))
    innodb_cache['cache_misses'] = global_status_dict['Innodb_buffer_pool_reads']
    
    try:
        innodb_cache['cache_hit_ratio'] = str("%.2f"
           %(float(global_status_dict['Innodb_buffer_pool_reads']) /
             float(global_status_dict['Innodb_buffer_pool_read_requests']) * 100)) + " %"
    except:
        pass
    
    try:
        innodb_cache['cache_write_wait'] = str("%.2f"
            %(float(global_status_dict['Innodb_buffer_pool_wait_free']) /
              float(global_status_dict['Innodb_buffer_pool_write_requests'])))
    except:
        pass
    
    innodb_cache['adtl_pool_size'] = convert_memory(int(global_var_dict['innodb_additional_mem_pool_size']))
    innodb_cache['free_page_waits'] = global_status_dict['Innodb_buffer_pool_wait_free']
    innodb_cache['buffer_max_size'] = global_var_dict['innodb_change_buffer_max_size']

    #resolving threads counter
    threads = counters_dict['threads']
    threads['thread_cache_size'] = global_var_dict['thread_cache_size']
    threads['threads_cached'] = global_status_dict['Threads_cached']
    threads['threads_created'] = global_status_dict['Threads_created']
    
    #cache hit rate
    try:
        created = int(threads['threads_created'])
        conns = int(global_status_dict['Connections'])
        if created > conns:
            threads['cache_hit_rate'] = '100'
        else:
            threads['cache_hit_rate'] = str((1-(created/conns)) * 100) + " %"
    except:
        pass
    
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

    try:
        query_cache['fragmentation'] = str("%.2f"
            %(float(global_status_dict['Qcache_free_blocks']) /
              float(ceil((float(global_status_dict['Qcache_total_blocks'])) /2 )) * 100 )) + " %"
    except:
        pass
    
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
