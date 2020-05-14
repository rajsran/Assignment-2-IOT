import socket
carnumber = "camry7"

while(True):
    print("Enter your credentials to unlock this car")
    email = input("Enter email id:")
    password = input("Enter password:")

    msgFromClient       = email+","+password+","+carnumber
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
    m = msgFromServer[0].decode("utf-8")
    if (m!="Wrong credentials. please try again to unlock car"):
        break

while (True):

    print("Enter your choice:")
    print("1.Close your booking and return the car")
    print("2.report an issue in the car")

    c = input("your Choice:")
    if (c=='1'):
        msgFromClient       = "close booking"
        bytesToSend         = str.encode(msgFromClient)
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        break
    elif (c=='2'):
        msgFromClient       = "report issue"
        bytesToSend         = str.encode(msgFromClient)
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        break
    else:
        print("invalid choice")
        
msgFromServer = UDPClientSocket.recvfrom(bufferSize)
msg = "Message from Server {}".format(msgFromServer[0])
print("Response recieved:")
print(msg)