import socket
from flask_bcrypt import Bcrypt
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os, requests, json, sqlite3
import MySQLdb

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
basedir = os.path.abspath(os.path.dirname(__file__))
bcrypt = Bcrypt(app)

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

# Listen for incoming datagrams
while(True):

    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    clientMsg = "Message from Client:{}".format(message)
    f=0
    
    msg = message.decode("utf-8")
    details = msg.split(',',1)
    email = details[0]
    password = details[1]
    
    with DatabaseUtils() as db:
        for user in db.getUser():
            if (user[1]==email):
                if (bcrypt.check_password_hash(user[2], password)):
                    f=1
                    break
    
    if (f==1):
        msgFromServer       = "Correct credentials. car has been unlocked"
        bytesToSend         = str.encode(msgFromServer)
    else:
        msgFromServer       = "Wrong credentials. please try again to unlock car"
        bytesToSend         = str.encode(msgFromServer)
      
    
    address = bytesAddressPair[1]
    #clientIP  = "Client IP Address:{}".format(address)
    #print(clientIP)

    # Sending a reply to client
    UDPServerSocket.sendto(bytesToSend, address)

"""
    Acknowledgement: Copyright of https://pythontic.com/modules/socket used
    for educational learning only
"""

if (__name__) == '__main__':
    app.run(debug=True)
