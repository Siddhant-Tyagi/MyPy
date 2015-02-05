import MySQLdb as my

connection_obj = my.connect

def connect_to_server(connection_detail_object):
    """This connection_detail_object has the following attributes 
    as inherited from models.py:
    mysql_host,
    mysql_port,
    mysql_server_name,
    mysql_user,
    mysql_password """
    
    global connection_obj
    #print str(connection_detail_object)
    try:
        connection_obj = my.connect(
                   host = str(connection_detail_object.mysql_host),
                   port = int(connection_detail_object.mysql_port),
                   user = str(connection_detail_object.mysql_user),
                   passwd = str(connection_detail_object.mysql_password)
                )
    except my.Error as connection_error:
        return(str(connection_error.args[0]) + " " + str(connection_error.args[1]))

    return("Connection to " + connection_detail_object.mysql_server_name +  " successful.!!")

def get_mysql_data(current_server_object):
    #print "inside get_mysql_data method"
    #print current_server_object
    #print current_server_object.mysql_server_name
    connection_msg = connect_to_server(current_server_object)
    #print "hello hello"
    if 'successful' in connection_msg:
        global connection_obj
        #print str(type(connection_obj))
        cursor_obj = connection_obj.cursor()
        cursor_obj.execute("show global variables")
        global_variables = cursor_obj.fetchall()
        cursor_obj.execute("show global status")
        global_status = cursor_obj.fetchall()
        connection_obj.close()
        return dict(global_variables), dict(global_status)
    return {}, {}
