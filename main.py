#!/usr/bin/env python

# This code developed at the University of Groningen for the IGEM project QRoningen  (Wiki link). Developed on Python 3.7 (32-bit), requires freecad

#make file with list of dependencies to make sure it's easy to just run the code
 #pip freeze > requirements.txt.
 #pip install -r requirements.txt
#implement decoding
#implement reader (zqr_test) to send message straight to decoder
#implement algorithm to look for correct location of freecad libraries
#implement question wether freecad should be used to allow it to be run without having to import library if not desired

#get stl_tools to work so that everything is done within python
#use this tool but it has to be done outside of python #https://github.com/rcalme/svg-to-stl

import os

#if you previously installed the "crypto" package the name in "lib/site-packages" of the folder needs to be changed from "crypto" to "Crypto"

from Crypto.Cipher import AES # pip install pycryptodome, If python won't recognize the crypto package make sure it's spelle the same way as in the folder of the package
from Crypto.Protocol.KDF import PBKDF2
from Crypto import Random
import secrets #used when generating the salt


import qrcode
import qrcode.image.svg
from lxml import etree

import base64 #

#import binascii # used to put encrypted message into characters supported by the qr code

import sys 

import numpy
sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) #ads current directory to path to find numpy2stl
from numpy2stl import numpy2stl #to extrude QR code
from scipy.ndimage import gaussian_filter
from PIL import Image

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM #turn SVG into PNG

#import matplotlib.pyplot as plt

import QRCodeGcodev2  #script to create gcode from QRcode (A script from my repository)


class Encryptor:
    def __init__(self, key, salt):
        self.key = key #hashlib.sha256(key).digest() 
        self.iv = Random.new().read(AES.block_size) #the initialization vector for the encryption
        self.salt = salt
        
    def pad(self, s): #function to pad message to encrypt in order to meet the requirement of being a multiple of 16 bytes
        length = AES.block_size - (len(s) % AES.block_size)
        print(s + b"\0" * length)
        return s + b"\0" * length
        

    def encrypt(self, message, key, key_size=256, ThrD=0): #function to encrypt message
        
        message = self.pad(message)
        
        #iv = b'6\xf1\xb7\xfc\xcf\t3!l\xe9\x16)\x06\x96\x8d\xb4' #Random.new().read(AES.block_size)

        cipher = AES.new(key, AES.MODE_CBC, self.iv)
        encrypted = self.iv + cipher.encrypt(message)
        print (encrypted)   
        encrypted= base64.b64encode(encrypted) #binascii.hexlify(encrypted) #putting encrypted message into hex format with acceptable characters for QR code
        print (encrypted)
        encryptedSTR=encrypted.decode("utf-8") #move byte string to text

        enc.qrcodeSVG(encryptedSTR)
        
        #iv = Random.new().read(AES.block_size)
        #cipher = AES.new(key, AES.MODE_CBC, iv)
        #return iv + cipher.encrypt(message)

    def nocrypt(self, message, ThrD=0): #this function generates a qr code without the encryption

        enc.qrcodeSVG(message, ThrD)


    def decrypt(self, ciphertext, key): 
        print("\nEnter Password message was encrypted with: IGEM\n")
        ciphertext = base64.b64decode(ciphertext) #puts in into byte format for algorithm to decrypt

        iv = ciphertext[:AES.block_size]
        decipher = AES.new(key, AES.MODE_CBC, iv)
        #ENCRYPTED=binascii.unhexlify(ciphertext)
        DECRYPTED=decipher.decrypt(ciphertext[AES.block_size:])
        DECRYPTED2 = DECRYPTED.rstrip(b"\0") #takes away padding
        DECRYPTED3 = DECRYPTED2.decode("utf-8") 

        print("The secret message is: " + DECRYPTED3 + "\n") #print decrypted message

    def qrcodeSVG(self, msg, ThrD=0): #this function makes the QR code and saves it as an SVG (3D file)
        
        self.sizepxl = 50
        self.bord = 2

        qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=self.sizepxl,
        border=self.bord,
        )

        qr.add_data(msg)

        factory = qrcode.image.svg.SvgFragmentImage

        img=qr.make_image(fill_color="black", back_color="white", image_factory=factory)

        img.save("QRSVGpy.svg")
        
        enc.editSVG(self.sizepxl, ThrD) #calls function to makes squares of QR code small before extrusion

    def editSVG(self, sizepxl, ThrD=0): #this function edits the svg and makes the squares in the QR code small
        tree = etree.parse(open('QRSVGpy.svg'))
        
        pxl = str(int(sizepxl/10)) + "mm"

        dessiz= 0.8 #desired size for the reduced square QR code, recommended 0.8
        
        for element in tree.iter(): #this loop finds all squares and makes them small
            if element.tag.split("}")[1] == "rect":
                if element.get("width") == pxl:
                    element.set("width", str(int(element.get("width")[0])*dessiz)+"mm")
                    element.set("height", str(int(element.get("height")[0])*dessiz)+"mm")

        tree.write('QRSVGpysmall.svg') #saves modified SVG into file 

        #svg=tree2.findall(".//{http://www.w3.org/2000/svg}rect") #find all rect elements COULD USE THIS TO FIND AND LEAVE THE BIG SQUARES BIG

        drawing = svg2rlg('QRSVGpysmall.svg')

        #renderPM.drawToFile(drawing, "QRSVGpysmall.png", fmt="PNG") #Uncomment this line to save automatically a png of the QR code with the smaller squares
        
        QRcodesmallsq = renderPM.drawToPIL(drawing) #This line saves the svg into a png to work with later with numpy as an array

        if ThrD == 1:
            enc.extrudeSVG(QRcodesmallsq)


    def extrudeSVG(self, QRcode): #extrudes qr code and generates 3D file to make stamp


        #QRcode = Image.open('QRSVGpysmall.png').convert('RGBA') #uncomment this when extruding an existing png
        
        A=numpy.array(QRcode)

        A=A[:,:,0]
        A= numpy.where(A>20, 0, 255) #invert colors of image so the extrusion extrudes the black colors
        #A=A

        #Full pixel size is 14x14

        x=2
        if x==2:
            sub = 14*4 #57 (for small non ecrypted QRcode)
        elif x==3:
            sub = -14*7


        A[27:40, 27:126] = 255 #the following values are all set to 255 to make the big squares solid rather than with dots
        A[27:126, 27:40] = 255
        A[113:126, 27:126] = 255
        A[27:126, 113:126] = 255        

        
        A[57:96, 57:96] = 255  


        A[27:40, 282-sub:380-sub] = 255
        A[27:126, 282-sub:296-sub] = 255
        A[113:126, 282-sub:380-sub] = 255
        A[27:126, 367-sub:380-sub] = 255


        A[57:96, 312-sub:351-sub] = 255  


        A[282-sub:380-sub, 27:40] = 255
        A[282-sub:296-sub, 27:126] = 255
        A[367-sub:380-sub, 27:126] = 255
        A[282-sub:380-sub, 113:126] = 255    

        A[312-sub:351-sub, 57:96] = 255  


        #cnt=0
        #while cnt==0:
            #plt.show(plt.matshow(A))

 
        #A.shape[1]

        numpy2stl(A, "STAMP.stl", max_width=55, scale=0.13, solid=True)#, scale=1, solid=True, max_depth=100) max_depth=20
        #numpy2stl(data, fname, scale=100, solid=True, max_width=228.6,max_depth=228.6, max_height=80, force_python=True) min_thickness_percent=0

        #mesh = pymesh.load_mesh("STAMP.stl")

        #mesh, info = pymesh.remove_isolated_vertices(mesh)
        print('FILE HAS BEEN EXTRUDED, have fun!')

        


####################

clear = lambda: os.system('cls')
clear()

Salt_size=8

salt='1d2f2' # secrets.token_hex(Salt_size) #'1d2f2'  #generates a string of random numbers to use as salt

gate = 0

while gate == 0:
    password = str(input("Setting up stuff. Enter a password that will be used for decryption: "))
    repassword = str(input("Confirm password: "))

    key = PBKDF2(password, salt, dkLen=16, count=2000) #salting process

    if password == repassword:
        gate=1
    else:
        print("Passwords Mismatched! Please try again")

    if gate == 1:
        break

enc = Encryptor(key, salt)

while gate == 1:
    choice = input("1. Press '1' to encrypt messsage.\n2. Press '2' to decrypt message.\n3. Press '3' to create QR code without encryption.\n4. Press '4' to read QR code.\n5. Press '5' to generate gcode to 3D print QR code.\n6. Press '6' to exit.\n") #clear()

    if choice == '1':
        ThrD=str(input("Do you want a 3D stamp? (yes=1 / no=0)"))
        enc.encrypt(str(input("Enter message to encrypt: ")).encode(), key)
    elif choice == '2':
        enc.decrypt(str(input("Enter message to decrypt: ")).encode(), key)
    elif choice == '3':
        ThrD=str(input("Do you want a 3D stamp? (yes=1 / no=0)"))
        enc.nocrypt(str(input("Enter message: ")).encode("utf-8"), ThrD)
    elif choice == '4':
        print('wait for camera to initialize\n')
        import QRcodereaderpython
    elif choice == '5':
        QRCodeGcodev2.QRgcode(str(input("Enter name of QR code png file: \n")))
    elif choice == '6':
        exit()
    else:
        print("Please select a valid option!")
