# import the necessary packages
import pyzbar
from pyzbar.pyzbar import decode
import cv2
from tkinter import *  # import for creating GUI
import PIL.Image, PIL.ImageTk
import time

##for shape detector
from pyimagesearch.shapedetector import ShapeDetector
import imutils
 

#from threading import Thread

#from valueadjust import main

#thread = Thread(target = main)
#thread.start() # This code will execute in parallel to the current code

w=0
BWl=0
BWh=255 

class App:
    def __init__(self, window, window_title, camera=0):
        self.window = window
        self.window.title(window_title)
        self.camera=camera

        self.video = VideoCap(self.camera) # open video source (camera)

        # Create a canvas that can fit the above video source size
        self.canvas = Canvas(window, width = self.video.width, height = self.video.height)
        self.canvas.pack()

        self.delay = 15
        self.update()


        Button(master, text='B&W', command=camera).pack()

        self.window.mainloop()

        #master.mainloop()
    def update(self):
        # Get a frame from the video source
        ret, frame = self.video.get_frame()

        #self.photo=cv2.imshow("Capturing", frame)

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = NW)

        
        self.window.after(self.delay, self.update)


class VideoCap:
    def __init__(self, camera=0):
        self.video= cv2.VideoCapture(camera)

        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        if not self.video.isOpened():
            raise ValueError("Unable to open video source", camera)

        self.width = self.video.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.win = Scale(master, from_=0, to=255, orient=HORIZONTAL)
        self.win.set(100)
        self.win.pack()

        self.wout = Scale(master, from_=0, to=255, orient=HORIZONTAL)
        self.wout.set(255)
        self.wout.pack()

        self.blandwh = Scale(master, from_=0, to=1, orient=HORIZONTAL)
        self.blandwh.set(0)
        self.blandwh.pack()

        self.inv = Scale(master, from_=0, to=1, orient=HORIZONTAL)
        self.inv.set(0)
        self.inv.pack()

        
    def get_frame(self):
        if self.video.isOpened():
            check, frame = self.video.read()  

            self.BWl=self.win.get()
            self.BWh=self.wout.get()
            self.onoffBW= self.blandwh.get()
            self.onoffinv= self.inv.get()

            #frame = cv2.imread("/Users/maria/Desktop/IGEM/qrcode.png") #use this line to test with still pictures

            #overlay= cv2.imread("/Users/maria/Desktop/IGEM/SQR.jpg") 

            dim = (102, 102) #Resize Size of Square Overlay
            
            #overlay= cv2.resize(overlay, dim)
            #rows,cols,channels = overlay.shape

            #overlay=cv2.addWeighted(frame[0:0+rows, 0:0+cols],0,overlay,1,1)

            #frame[0:0+rows, 0:0+cols ] = overlay

            #frame= cv2.imwrite('combined.png', added_image)


            img= cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #turn picture to grayscale
            #overlay= cv2.cvtColor(overlay, cv2.COLOR_BGR2GRAY) #turn picture to grayscale
            

            resized = cv2.resize(img, (200, 200))#imutils.resize(img, width=300)
            ratio = img.shape[0] / float(resized.shape[0])

            #barcodes = decode(img) #decoding before black and white !!!!!!!!!!!!
            
            #if self.onoffBW == 1:
            #for i in range(20, 180, 10):
            (thresh, img) = cv2.threshold(img, self.BWl, self.BWh, cv2.THRESH_BINARY) #turn picture Black and White
            barcodes = decode(img) #to use to scan for barcodes before inverting image
            #    print(i)
            #    if not not barcodes:
            #        break

            #for i in range(20, 180, 5):
            #    (thresh, src) = cv2.threshold(img, 100, self.BWh, cv2.THRESH_BINARY) #turn picture Black and White
            #    barcodes = decode(src) #to use to scan for barcodes before inverting image
            #    #print(i)
            #    if not not barcodes:
            #        break
            
            #overlay = cv2.threshold(overlay, self.BWl, self.BWh, cv2.THRESH_BINARY)[1]
            
            

            #if self.onoffinv == 1:
            img = cv2.bitwise_not(img) #Invert color of image!!!!!!!!!!!!

            #overlay = cv2.bitwise_not(overlay) #Invert color of image
            #thresh = cv2.threshold(img, self.BWl, self.BWh, cv2.THRESH_BINARY)[1]

            #img = cv2.blur(img,(5,5)) #BLUR IMAGE

            barcodesinv = decode(img) #find QR codes (when picture is Black and Wait, seems to work better with out codes)

            if barcodes: #detection of barcodes without inverting image
                # loop over the detected barcodes
                for barcode in barcodes:
                    # extract the bounding box location of the barcode and draw the
                    # bounding box surrounding the barcode on the image
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 100), 3)
                    # the barcode data is a bytes object so if we want to draw it on
                    # our output image we need to convert it to a string first
                    barcodeData = barcode.data.decode("utf-8")
                    barcodeType = barcode.type
                    
                    #ciphertext=barcodeData
                    #from Crypto.Cipher import AES
                    #import base64
                    #block_size=16
                    #key=b'\xebT\xe7Tm\xf3S/\x06\xeb\x005\xc6z\x0f\x1f'
                    #ciphertext = base64.b64decode(ciphertext) #binascii.unhexlify(ciphertext) #puts in into byte format

                    #iv = ciphertext[:block_size]
                    #decipher = AES.new(key, AES.MODE_CBC, iv)
                    #ENCRYPTED=binascii.unhexlify(ciphertext)
                    #DECRYPTED=decipher.decrypt(ciphertext[AES.block_size:])
                    #DECRYPTED2 = DECRYPTED.rstrip(b"\0") #takes away padding
                    #DECRYPTED3 = DECRYPTED2.decode("utf-8") 
                    #plaintext = cipher.decrypt(ciphertext[AES.block_size:])
                    #print(DECRYPTED3)
                    #barcodeData=DECRYPTED3

                    # draw the barcode data and barcode type on the image
                    text = "{} ({})".format(barcodeData, barcodeType)
                    cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 2)
                    # print the barcode type and data to the terminal
                    print("[INFO] Found {} barcode\n Your message is: {}".format(barcodeType, barcodeData))
                    #break #uncomment this line to break loop as soon as QR code is detected

            if barcodesinv: #detection of barcodes with image inverted
                # loop over the detected barcodes
                for barcode in barcodesinv:
                    # extract the bounding box location of the barcode and draw the
                    # bounding box surrounding the barcode on the image
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 100), 3)
                    # the barcode data is a bytes object so if we want to draw it on
                    # our output image we need to convert it to a string first
                    barcodeData = barcode.data.decode("utf-8")
                    barcodeType = barcode.type
                        
                    # draw the barcode data and barcode type on the image
                    text = "{} ({})".format(barcodeData, barcodeType)
                    cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 2)
                    
                    ## print the barcode type and data to the terminal
                    #print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
                    self.info = "[INFO] Found {} barcode: {}".format(barcodeType, barcodeData)
                    #break #uncomment <--- this line to break loop as soon as QR code is detected

            ## Shape Detector
            cnts = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            sd = ShapeDetector()
            if len(cnts)>2:
                for c in cnts:
                    M = cv2.moments(c)
                    if M["m00"]!=0:
                        #if  cv2.moments(c)
                        # compute the center of the contour, then detect the name of the
                        # shape using only the contour
                        M = cv2.moments(c)
                        
                        cX = int((M["m10"] / M["m00"]) )
                        cY = int((M["m01"] / M["m00"]) )
                        shape = sd.detect(c)

                        # multiply the contour (x, y)-coordinates by the resize ratio,
                        # then draw the contours and the name of the shape on the image
                        c = c.astype("float")
                        #c *= ratio

                        #dim = (60, 60)  ##TO RESIZE Squares
                        #overlay= cv2.resize(overlay, dim)
                        #overlay = cv2.threshold(overlay, 100, 255, cv2.THRESH_BINARY)[1]

                        c = c.astype("int")
                        if shape=="square" or shape=="rectangle":
                            if cX>dim[1] and cY>dim[1] and cX<len(img)-dim[1] and cY<len(img)-dim[1]:
                                cv2.drawContours(img, [c], -1, (100, 100, 100), 10)
                                cv2.putText(img, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 2)
                                #overlay=cv2.addWeighted(img[cY-int(rows/2):cY+int(rows/2), cX-int(cols/2):cX+int(cols/2)],0,overlay,1,1) #ADDING squares in the center of other squares
                                #img[cY-int(rows/2):cY+int(rows/2), cX-int(cols/2):cX+int(cols/2)] = overlay


            return(check, frame)

    def __del__(self):
        return print(self.info)
        if self.video.isOpened():
            self.video.release()

master = Tk()

App(master, "Tkinter and OpenCV")

#main()