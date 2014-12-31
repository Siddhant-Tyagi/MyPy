import sqlite3
import os

#the delete_server_list conatins the mysql server's names to be deleted
#the method is called in the index view for deleting server
def delete_servers(delete_server_list):
    #building the path to the sqlite database file
    sqlite_db_path = os.path.join(os.path.dirname(__file__), os.pardir)
    sqlite_db_path = os.path.abspath(os.path.join(sqlite_db_path, "mypy_app.db"))
    #using the sqlite3 python API to modify the database
    sqlite_connection_obj = sqlite3.connect(sqlite_db_path)
    sqlite_cursor_obj = sqlite_connection_obj.cursor()
    #executing commands on the sqlite database for deleting servers
    for server_name in delete_server_list:
        sqlite_cursor_obj.execute("delete from mypy_app_add_server where mysql_server_name='%s'" \
                %server_name)
    sqlite_connection_obj.commit()
    sqlite_connection_obj.close()

