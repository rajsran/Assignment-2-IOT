from imutils import paths
from imutils.video import VideoStream
import face_recognition
import argparse
import pickle
import cv2
import imutils
import os
import socket
import time
carnumber = "camry7"

while(True):
    choice = input("Enter 1 for facial recognition or 2 for entering userid and password")
    if (choice=='1'):
        #code to encode the image
        ch = input("enter 1 to encode")
        if (ch=='1'):
            ap = argparse.ArgumentParser()
            ap.add_argument("-i", "--dataset", default = "dataset",
               help="path to input directory of faces + images")
            ap.add_argument("-e", "--encodings", default = "encodings.pickle",
               help="path to serialized db of facial encodings")
            ap.add_argument("-d", "--detection-method", type = str, default = "hog",
               help="face detection model to use: either `hog` or `cnn`")
            args = vars(ap.parse_args())

# grab the paths to the input images in our dataset
            print("[INFO] quantifying faces...")
            imagePaths = list(paths.list_images(args["dataset"]))

# initialize the list of known encodings and known names
            knownEncodings = []
            knownNames = []

# loop over the image paths
            for (i, imagePath) in enumerate(imagePaths):
    # extract the person name from the image path
                print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))
                name = imagePath.split(os.path.sep)[-2]

    # load the input image and convert it from RGB (OpenCV ordering)
    # to dlib ordering (RGB)
                image = cv2.imread(imagePath)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # detect the (x, y)-coordinates of the bounding boxes
    # corresponding to each face in the input image
                boxes = face_recognition.face_locations(rgb, model = args["detection_method"])

    # compute the facial embedding for the face
                encodings = face_recognition.face_encodings(rgb, boxes)
    
    # loop over the encodings
                for encoding in encodings:
        # add each encoding + name to our set of known names and encodings
                    knownEncodings.append(encoding)
                    knownNames.append(name)

# dump the facial encodings + names to disk
            print("[INFO] serializing encodings...")
            data = { "encodings": knownEncodings, "names": knownNames }

            with open(args["encodings"], "wb") as f:
                f.write(pickle.dumps(data))
            
        chh = input("enter 2 to recognise")
        if (chh=='2'):
            ap = argparse.ArgumentParser()
            ap.add_argument("-e", "--encodings", default="encodings.pickle",
            help="path to serialized db of facial encodings")
            ap.add_argument("-r", "--resolution", type=int, default=240,
                help="Resolution of the video feed")
            ap.add_argument("-d", "--detection-method", type=str, default="hog",
                help="face detection model to use: either `hog` or `cnn`")
            args = vars(ap.parse_args())

# load the known faces and embeddings
            print("[INFO] loading encodings...")
            data = pickle.loads(open(args["encodings"], "rb").read())

# initialize the video stream and then allow the camera sensor to warm up
            print("[INFO] starting video stream...")
#vs = VideoStream(src = 0).start()
#time.sleep(2.0)

# loop over frames from the video file stream
            i=0
            while i < 1:
    # grab the frame from the threaded video stream
    #frame = vs.read()
                frame = cv2.imread('dataset//rdrd.jpg')

    # convert the input frame from BGR to RGB then resize it to have
    # a width of 750px (to speedup processing)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb = imutils.resize(frame, width = args["resolution"])

    # detect the (x, y)-coordinates of the bounding boxes
    # corresponding to each face in the input frame, then compute
    # the facial embeddings for each face
                boxes = face_recognition.face_locations(rgb, model = args["detection_method"])
                encodings = face_recognition.face_encodings(rgb, boxes)
                names = []

    # loop over the facial embeddings
                for encoding in encodings:
        # attempt to match each face in the input image to our known
        # encodings
                    matches = face_recognition.compare_faces(data["encodings"], encoding)
                    name = "Unknown"

        # check to see if we have found a match
                    if True in matches:
            # find the indexes of all matched faces then initialize a
            # dictionary to count the total number of times each face
            # was matched
                        matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                        counts = {}

            # loop over the matched indexes and maintain a count for
            # each recognized face face
                        for i in matchedIdxs:
                            name = data["names"][i]
                            counts[name] = counts.get(name, 0) + 1

            # determine the recognized face with the largest number
            # of votes (note: in the event of an unlikely tie Python
            # will select first entry in the dictionary)
                        name = max(counts, key = counts.get)

        # update the list of names
                    names.append(name)

   # loop over the recognized faces
                i = i+1
                for name in names:
        # print to console, identified person
                     print("Person found: {}".format(name))
                     break
        # Set a flag to sleep the cam for fixed time
                     time.sleep(3.0)

# do a bit of cleanup
#vs.stop()

            
            
    elif (choice=='2'):
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
    else:
        print("Invalid choice")

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