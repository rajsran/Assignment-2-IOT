#!/usr/bin/env python3
import bluetooth
import os
import time
from sense_hat import SenseHat

import MySQLdb

import socket


from imutils.video import VideoStream
from pyzbar import pyzbar
import datetime
import imutils
import time
import cv2

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
    engID = ""
    fromqr = ""
    with DatabaseUtils() as db:
            for row in db.getEngineersMACs():
                if (row[0]==foundMac):
                    engID = str(row[1])
                    
    qr = input("Please enter location of your qr code")
    found = set()

    # loop over the frames from the video stream

        # grab the frame from the threaded video stream and resize it to
        # have a maximum width of 400 pixels
    frame = cv2.imread("QR/e001.png")
    frame = imutils.resize(frame, width = 400)

        # find the barcodes in the frame and decode each of the barcodes
    barcodes = pyzbar.decode(frame)

        # loop over the detected barcodes
    for barcode in barcodes:
            # the barcode data is a bytes object so we convert it to a string
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type

            # if the barcode text has not been seen before print it and update the set
        if barcodeData not in found:
            print("[FOUND] Type: {}, Data: {}".format(barcodeType, barcodeData))
            found.add(barcodeData)
            fromqr = barcodeData
        # wait a little before scanning again
    time.sleep(1)
        
    if (fromqr==engID):
        print("Authentication done, your QR code confirms your identity!")
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
        
    else:
        print("Your QR code is Different from our records! Authentication failed!")

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

