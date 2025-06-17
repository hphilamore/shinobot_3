#!/usr/bin/env python3

import socket
from time import sleep
from time import time
import json

# Listen on all interfaces
host = "0.0.0.0"  

# Port to listen on (non-privileged ports are > 1023)
port = 65448    


# Set up server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.settimeout(1.0)  # a bit longer timeout
server_socket.listen()


while True:
    try:
        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected by {addr}")
            # data = conn.recv(16384)  # increased buffer size
            # if not data:
            #     continue  # don't break the server loop
            # msg = data.decode()
            # msg = json.loads(msg)
            

            # Wrap the socket in a file-like object to read full lines
            with conn.makefile('r') as f:
                msg = f.readline().strip() # remove newline
                msg = json.loads(msg)

            print('msg', type(msg), msg)


    except socket.timeout:
        print('no connection from client')
        continue


