import MySQLdb as my
import time

#connection_obj = my.connect

def connect_to_server(connection_detail_object):
    """This connection_detail_object has the following attributes 
    as inherited from models.py:
    mysql_host,
    mysql_port,
    mysql_server_name,
    mysql_user,
    mysql_password """
    
    #global connection_obj
    #print str(connection_detail_object)
    try:
        connection_obj = my.connect(
                   host = str(connection_detail_object.mysql_host),
                   port = int(connection_detail_object.mysql_port),
                   user = str(connection_detail_object.mysql_user),
                   passwd = str(connection_detail_object.mysql_password),
                   connect_timeout = 5
                )
    except my.Error as connection_error:
        #print "coudnt connect"
        return (str(connection_error.args[0]) + " " + str(connection_error.args[1])), None

    return ("Connection to " + connection_detail_object.mysql_server_name +  " successful!!"), connection_obj


def get_mysql_data(current_server_object, server_info_queue):
    connection_msg, connection_obj = connect_to_server(current_server_object)
    #print "hello hello"
    #print connection_msg
    if connection_obj:
        #print "connection_obj is not null"
        #print str(type(connection_obj))
        cursor_obj = connection_obj.cursor()
        cursor_obj.execute("show global variables")
        global_variables = cursor_obj.fetchall()
        cursor_obj.execute("show global status")
        global_status = cursor_obj.fetchall()
        try:
            cursor_obj.execute("show slave status")
            slave = cursor_obj.description
            slave_field = [i[0] for i in slave]
            slave_values = cursor_obj.fetchall()
            slave_status = {}
            for key, value in zip(slave_field, slave_values[0]):
                slave_status[key] = str(value)
        
        except:
            slave_status = {}
        connection_obj.close()
        server_info_queue.put({str(current_server_object.mysql_server_name): 
                               {
                                'global_var_dict': dict(global_variables), 
                                'global_status_dict': dict(global_status), 
                                'slave_status_dict': dict(slave_status)
                                }
                              })

    else:
        server_info_queue.put({str(current_server_object.mysql_server_name): 
                               {
                                'global_var_dict': {}, 
                                'global_status_dict': {}, 
                                'slave_status_dict': {}
                                }
                              })
