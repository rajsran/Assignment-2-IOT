#!/usr/bin/env python3
import bluetooth
import os
import time
from sense_hat import SenseHat

import MySQLdb

import socket
carnumber = "camry7"

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

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    

    def getEngineersMACs(self):
        with self.connection.cursor() as cursor:
            cursor.execute("select MAC, EmployeeID from Engineer")
            return cursor.fetchall()



# Main function
def main():
    foundMac = search()
    engID=""
    with DatabaseUtils() as db:
            for row in db.getEngineersMACs():
                if (row[0]==foundMac):
                    engID = str(row[1])
    
    print("Sending to Agent pi for unlocking with you ID:"+engID)
    
    msgFromClient       = carnumber  + "-" + engID
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
    

# Search for device based on device's name
def search():
    MACs = []
    print("Fetching all MAC addresses of engineers from cloud database and printing it..")
    with DatabaseUtils() as db:
            for mac in db.getEngineersMACs():
                print(mac[0]);
                MACs.append(str(mac[0]))
    
    
    while True:
        device_address = None
        print("Searching for nearby devices...")
        time.sleep(1) #Sleep three seconds 
        nearby_devices = bluetooth.discover_devices()
        f=0
        foundMac = ""
        for mac_address in nearby_devices:
            if mac_address in MACs:
                print('You are an authorized Engineer...')
                f=1
                foundMac = mac_address
                break
        if (f==1):
            return foundMac
            break
        else:
            if nearby_devices is not None:
                print("Hi, You are not an authorized Engineer, Car can not be unlocked...")
            else:
                print("Could not find target device nearby...! Car is still locked..")

#Execute program
main()

