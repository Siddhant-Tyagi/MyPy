#!/usr/bin/env python
# 
# A clone of manage.py, with multi-threadedness monkeypatched in.

import os, sys
from django.core.management import execute_from_command_line
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write(
        "Error: Can't find the file 'settings.py' in the directory containing %r. "
        "It appears you've customized things.\n"
        "You'll have to run django-admin.py, passing it your settings module.\n"
        "(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n"  
        % __file__
        )
    sys.exit(1)

def monkey_patch_for_multi_threaded():
    # This monkey-patches BaseHTTPServer to create a base HTTPServer class that 
    # supports multithreading 
    import BaseHTTPServer, SocketServer  
    OriginalHTTPServer = BaseHTTPServer.HTTPServer

    class ThreadedHTTPServer(SocketServer.ThreadingMixIn, OriginalHTTPServer):  
        def __init__(self, server_address, RequestHandlerClass=None):  
            OriginalHTTPServer.__init__(self, server_address, RequestHandlerClass)  

    BaseHTTPServer.HTTPServer = ThreadedHTTPServer

if __name__ == "__main__":
    monkey_patch_for_multi_threaded()
    execute_from_command_line(sys.argv)