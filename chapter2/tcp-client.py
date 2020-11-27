import socket

target_host = input('Target host: ')
target_port = int(input('Target port: '))
target_data = input('Target data: ').encode()

# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
client.connect((target_host, target_port))

# send some data
client.send(target_data)

# receive data
response = client.recv(4096)

print(response)