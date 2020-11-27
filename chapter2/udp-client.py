import socket

#target_host = input('Target Host: ')
#target_port = int(input('Target Port: '))
#target_data = input('Target Data: ')

# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send some data
client.sendto(b"AAABBBCCC", ("0.0.0.0", 9999))

# receive some data
data, addr = client.recvfrom(4096)

print(data)