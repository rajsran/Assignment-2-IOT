import socket
from flask_bcrypt import Bcrypt
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os, requests, json, sqlite3
import MySQLdb
from datetime import date
from index import closeBooking, reportIssue

bcrypt = Bcrypt()
neededBooking = None
username = None

class DatabaseUtils:
    HOST = "34.87.232.0"
    USER = "root"
    PASSWORD = "123456"
    DATABASE = "People"

    def __init__(self, connection = None):
        if(connection == None):
            connection = MySQLdb.connect(DatabaseUtils.HOST, DatabaseUtils.USER,
                DatabaseUtils.PASSWORD, DatabaseUtils.DATABASE)
        self.connection = connection
        
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.connection.close()
        
    def getUser(self):
        with self.connection.cursor() as cursor:
            cursor.execute("select * from User")
            return cursor.fetchall()
        
    def getBooking(self):
        with self.connection.cursor() as cursor:
            cursor.execute("select * from Booking")
            return cursor.fetchall()

#localIP     = "127.0.0.1"
localIP     = "192.168.1.10"
localPort   = 65000
bufferSize  = 1024

msgFromServer       = ""
bytesToSend         = str.encode(msgFromServer)

 
# Create a datagram socket
# communication domain in which the socket should be created. Some of address families are AF_INET (IP), AF_INET6 (IPv6), 
# AF_UNIX (local channel, similar to pipes), AF_ISO (ISO protocols), and AF_NS (Xerox Network Systems protocols).
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("UDP server up and listening")
f=0
b=0
bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
message = bytesAddressPair[0]
clientMsg = "Message from Client:{}".format(message)
print(clientMsg)
msg = message.decode("utf-8")
details = msg.split(',',2)
if (details[0]=="1"):
    creds = False
    username = details[1]
    carnumber = details[2]
    with DatabaseUtils() as db:
        for user in db.getUser():
            if (user[0]==username):
                f=1
    
    if (f==1):
        msgFromServer       = "Photo verified.Welcome, "+ username+"."
        with DatabaseUtils() as db:
            for booking in db.getBooking():
                if (booking[1]==carnumber and booking[2]==username and booking[3]==date.today() ):
                    if (booking[4]==None):
                        b=1
                    else:
                        b=2
                    neededBooking = booking[0]
                    
        if (b==1):
            msgFromServer += "Your car has been unlocked" 
            bytesToSend         = str.encode(msgFromServer)
            print(msgFromServer)
            address = bytesAddressPair[1]
            UDPServerSocket.sendto(bytesToSend, address)
            
        elif (b==2):
            msgFromServer += "You have already closed this booking.Please make another booking for this car first" 
            bytesToSend         = str.encode(msgFromServer)
            print(msgFromServer)
            address = bytesAddressPair[1]
            UDPServerSocket.sendto(bytesToSend, address)

        else:
            msgFromServer += "You have not made a booking for this car today. Please make a booking first." 
            bytesToSend         = str.encode(msgFromServer)
            print(msgFromServer)
            address = bytesAddressPair[1]
            UDPServerSocket.sendto(bytesToSend, address)

    else:
        msgFromServer       = "User not found"
        bytesToSend         = str.encode(msgFromServer)
        print(msgFromServer)
        address = bytesAddressPair[1]
        UDPServerSocket.sendto(bytesToSend, address)
        

else:
    creds= True


# Listen for incoming datagrams
while(creds):
    print("Checking credentials")
    clientMsg = "Message from Client:{}".format(message)
    print(clientMsg)
    f=0
    b=0
    email = details[0]
    password = details[1]
    carnumber = details[2]
    
    with DatabaseUtils() as db:
        for user in db.getUser():
            if (user[1]==email and bcrypt.check_password_hash(user[2], password)):
                f=1
                username = user[0]
    
    if (f==1):
        msgFromServer       = "Correct credentials.Welcome, "+ username+"."
        with DatabaseUtils() as db:
            for booking in db.getBooking():
                if (booking[1]==carnumber and booking[2]==username and booking[3]==date.today()):
                    if (booking[4]==None):
                        b=1
                    else:
                        b=2
                    neededBooking = booking[0]
                    
        if (b==1):
            msgFromServer += "Your car has been unlocked" 
            bytesToSend         = str.encode(msgFromServer)
            print(msgFromServer)
            address = bytesAddressPair[1]
            UDPServerSocket.sendto(bytesToSend, address)
            break
        elif (b==2):
            msgFromServer += "You have already closed this booking.Please make another booking for this car first" 
            bytesToSend         = str.encode(msgFromServer)
            print(msgFromServer)
            address = bytesAddressPair[1]
            UDPServerSocket.sendto(bytesToSend, address)
            break
        else:
            msgFromServer += "You have not made a booking for this car today. Please make a booking first." 
            bytesToSend         = str.encode(msgFromServer)
            print(msgFromServer)
            address = bytesAddressPair[1]
            UDPServerSocket.sendto(bytesToSend, address)
            break
    else:
        msgFromServer       = "Wrong credentials. please try again to unlock car"
        bytesToSend         = str.encode(msgFromServer)
        print(msgFromServer)
        address = bytesAddressPair[1]
        UDPServerSocket.sendto(bytesToSend, address)
    #clientIP  = "Client IP Address:{}".format(address)
    #print(clientIP)

    # Sending a reply to client
    
bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
message = bytesAddressPair[0]
clientMsg = "Message from Client:{}".format(message)
msg = message.decode("utf-8")

if (msg=="close booking"):
    url = 'http://127.0.0.1:5000/closeBooking?booking_id=' + neededBooking + '&user=' + username
    r = requests.get(url)
    msgFromServer       = "closing your booking"
    bytesToSend         = str.encode(msgFromServer)
    
elif (msg=="report issue"):
    url = 'http://127.0.0.1:5000/reportIssue?booking_id=' + neededBooking + '&user=' + username
    r = requests.get(url)
    msgFromServer       = "issue has been reported"
    bytesToSend         = str.encode(msgFromServer)
    
else:
    msgFromServer       = "Unrecognized command..."
    bytesToSend         = str.encode(msgFromServer)
print(bytesToSend)
address = bytesAddressPair[1]
UDPServerSocket.sendto(bytesToSend, address)
print("Transaction close")
