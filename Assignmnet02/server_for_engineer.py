import socket
from flask_bcrypt import Bcrypt
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os, requests, json, sqlite3
import MySQLdb
from datetime import date
from index import closeBooking, reportIssue

bcrypt = Bcrypt()
foundIssue = None

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
        
        
    def getIssue(self):
        with self.connection.cursor() as cursor:
            cursor.execute("select carnumber, isOpen, reportID from Issue")
            return cursor.fetchall()
        
    def updateIssue(self, reportID, solvedBy, closedOn, carnumber):
        with self.connection.cursor() as cursor:
            cursor.execute("update Issue set isOpen=false, solvedBy=%s, closedOn = %s where reportID = %s", (solvedBy, closedOn, reportID,))
            cursor.execute("update Car set maintenance = 0 where carnumber=%s", (carnumber,))
        self.connection.commit()

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
details = msg.split('-',2)


with DatabaseUtils() as db:
            for row in db.getIssue():
                if (row[0]==details[0] and row[1]==True):
                    f=1
                    foundIssue = str(row[2])
                    break

if (f==1):
    closedOn = date.today()
    with DatabaseUtils() as db:
            db.updateIssue(foundIssue, details[1], closedOn, details[0])
    msgFromServer       = "Unlocking the car and uploading your details"
    bytesToSend         = str.encode(msgFromServer)
    
else:
    msgFromServer       = "This car has not been reported to have any issues"
    bytesToSend         = str.encode(msgFromServer)

print(bytesToSend)
address = bytesAddressPair[1]
UDPServerSocket.sendto(bytesToSend, address)
print("Transaction close")
                    
