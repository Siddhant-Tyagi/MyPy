import MySQLdb as my


def connect_to_server(connection_detail_object):
    """This connection_detail_object has the following attributes 
    as inherited from models.py:
    mysql_host,
    mysql_port,
    mysql_server_name,
    mysql_user,
    mysql_password """

    try:
        my.connect(
                host = str(connection_detail_object.mysql_host),
                port = int(connection_detail_object.mysql_port),
                user = str(connection_detail_object.mysql_user),
                passwd = str(connection_detail_object.mysql_password)
                )
    except my.Error as connection_error:
        return(str(connection_error.args[0]) + " " + str(connection_error.args[1]))

    return("Connection to " + connection_detail_object.mysql_server_name +  " successful.!!")
