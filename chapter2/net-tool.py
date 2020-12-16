import sys
import socket
import getopt
import threading
import subprocess

#global variables
listen                  = False
command                 = False
upload                  = False
execute                 = ""
target                  = ""
upload_destination      = ""
port                    = 0

def usage():
    print("Net Tool")
    print("\b")
    print("Usage: net-tool.py -t host -p port")
    print("-l --listen                  - listen on [host]:[port] for incoming connections")
    print("-e --execute=file            - execute the given file upon receiving a connection")
    print("-c --command                 - initialize shell")
    print("-u --upload=destination      - upon connecting upload file to [destination]")
    print("\b\b")
    print("Example:")
    print("net-tool.py -t 0.0.0.0 -p 5000 -l -c")
    print("net-tool.py -t 0.0.0.0 -p 5000 -l -u=c:\\target.exe")
    print("net-tool.py -t 0.0.0.0 -p 5000 -l -e=\"cat /etc/passwd\"")
    print("echo 'abcdef' | ./net-tool.py -t 0.0.0.0 -p 135")
    sys.exit(0)

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()
    
    # read commandline options
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:", ["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

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

    # listen or send data from stdin?
    if not listen and len(target) and port > 0:

        # read in the buffer from command line
        # this will block, CTRL-D to break
        buffer = sys.stdin.read()

        # send data
        client_sender(buffer)

    # listen then maybe upload, execute, get shell depending on switches
    if listen:
        server_loop()

def client_sender(buffer):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to target host
        client.connect((target,port))

        if len(buffer):
            client.sendto(buffer)
        
        while True:
            #  wait for data back
            recv_len = 1
            response = ""

            while recv_len:

                data        = client.recv(4096)
                recv_len    = len(data)
                response    += data

                if recv_len < 4096:
                    break

            print(response)

            # wait for more input
            buffer = raw_input("")
            buffer += "\n"

            # send response
            client.send(buffer)

    except:

        print("[*] Exception! Exiting.")

        # tear down connection
        client.close()

def server_loop():
    global target

    # if no target is defined, listen on all interfaces
    if not len(target):
        target = "0.0.0.0"         

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        #start thread to handle new client
        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()

def run_command(command):

    # trim newline
    command = command.rstrip()

    # run command and grab output
    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT, shell=true)
    except:
        output = "failed to execute command.\r\n"

    return output

def client_handler(client_socket):
    global upload
    global execute
    global command

    # check for upload
    if len(upload_destination):

        # read bytes, write to destination
        file_buffer = ""

        # continue reading until no more
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        # IN bytes OUT string
        try:
            file_descriptor = open(upload_destination,"wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # File written notification
            client_socket.send(f'Successfully saved file to {upload_destination}')

    # check for command execution
    if len(execute):

        # run command
        output = run_command(execute)

        client_socket.send(output)

    # Check if shell was requested
    if command:

        while True:

            client_socket.send("<BHP:#> ")

                # receive until linefeed
                (enter_key)
            cmd_buffer = ""

            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1-24)

            # send back output
            response = run_command(cmd_buffer)

            # send back response
            client_socket.send(response)


main()


    

