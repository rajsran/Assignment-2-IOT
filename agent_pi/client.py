import socket

print("Enter your credentials to unlock this car")
email = input("Enter email id:")
password = input("Enter password:")

msgFromClient       = email+","+password
bytesToSend         = str.encode(msgFromClient)
serverAddressPort   = ("218.214.235.136", 65000)
bufferSize          = 1024
print("connecting...")
# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
print("checking your credentials...")
# Send to server using created UDP socket
UDPClientSocket.sendto(bytesToSend, serverAddressPort)
print("details sent to server...")
print("waiting for response...")
msgFromServer = UDPClientSocket.recvfrom(bufferSize)
msg = "Message from Server {}".format(msgFromServer[0])
print("Response recieved:")
print(msg)


"""
    Acknowledgement: Copyright of https://pythontic.com/modules/socket used
    for educational learning only
"""