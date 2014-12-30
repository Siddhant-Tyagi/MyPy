import sqlite3
import os


def delete_servers(delete_server_list):
    sqlite_db_path = os.path.join(os.path.dirname(__file__), os.pardir)
    sqlite_db_path = os.path.abspath(os.path.join(sqlite_db_path, "mypy_app.db"))
    sqlite_connection_obj = sqlite3.connect(sqlite_db_path)
    sqlite_cursor_obj = sqlite_connection_obj.cursor()
    for server_name in delete_server_list:
        sqlite_cursor_obj.execute("delete from mypy_app_add_server where mysql_server_name='%s'" \
                %server_name)
    sqlite_connection_obj.commit()
    sqlite_connection_obj.close()

