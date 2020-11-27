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

main()


    

