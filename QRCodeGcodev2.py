#!/usr/bin/env python

# The function in this script takes any QR code png and writes gcode capable of making a 3d printer extrude it as 1 layer (could also be adapted to laser CNC machines by changing extrusion)

#import imageio
from PIL import Image
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import os

def QRgcode(QRcodefile): 

################## This first section of the code deconstructs the image of the QR code into singular pixels to analyze

    try:
        f = open(str(QRcodefile))
        f.close()
    except FileNotFoundError:
        return print('\nQR code file couldn\'t be found, please make sure it\'s in the same folder as this script\n')
        

    black=1 #or 255 this depends on the color of the image
    white=0

    #QRi = np.array(imageio.imread(str(QRcodefile))).astype(int) #get image as numpy array

    QRi = np.asarray(Image.open(QRcodefile))

    S=QRi.shape[1]

    pix = S / 7 #How many squares in width (or height) of the qr code

    #ind=np.where(QRi[0] == 255) #determine where the white part starts and black part  ends of first row of QR code

    ind=np.where(QRi[0] == white)

    pix =round(S/(ind[0][0]/7)).astype(int)

    #QRw=np.array([]).astype(int)


    QRw=np.empty([0,pix], dtype=int) #np.array([]).astype(int).reshape(0,pix) #initialize the QRw matrix
    
    QRrowhold = np.array([]).astype(int) #initialize the QRrowhold matrix

    #This for loop skips every square to get a pixel out of every square, to just build the final qr where every square is one pixel
    for i in sp.arange(2, QRi.shape[1], S/pix).astype(int): 
        for j in sp.arange(2, QRi.shape[1], S/pix).astype(int):
            QRrowhold = np.hstack((QRrowhold, QRi[i][j])) 

        QRw=np.vstack((QRw, QRrowhold))   
        QRrowhold=np.array([]).astype(int)

    #plt.title('Input QR code')   #use these lines to show a plot of the QR code that will be outputted
    #plt.imshow(QRw, cmap='gray')
    #plt.show()

    QRw[0:8, 0:8] = white #These three lines erase the big squares as they are already prebuilt
    QRw[0:8, -8:] = white
    QRw[-8:, 0:8] = white

    #plt.title('Gcode QR code')
    #plt.imshow(QRw, cmap='gray')
    #plt.show()

############### From Here on the Code starts to assemble the Gcode 

    j=open('QRcodeinGcode.txt', "w+") #start up the gcode file
    #j=open(QRcodefile+'Gcode.txt', "w+") #start up the gcode file

    startx=150 #starting point where the QR code will be printed
    starty=150
    startz=25 #height between steps, make sure this is higher than the walls of the plate to be printed on to avoid the bioprinter moving the plate
    Z= 0 #plate touch (edit this value to get the bioprinter to touch the agar)

    size= 45 ## desired total size of QR in mm

    pxl=size/21 #calculates size of pixels of QR code (don't edit this line)

    j.write("M82 " + "; Absolute extrusion mode"+"\n") #this section initializes the gcode file for the 3D printer
    j.write("G28 " + "; Home extruder"+"\n")
    j.write("M107 " + "; Turn off fan"+"\n")
    j.write("G90 " + "; ABSOLUTE positioning"+"\n")
    j.write("M83 " + "; Extruder in relative mode"+"\n")
    j.write("M302 E0 " + "; Take away temperature requirements or extrusion"+"\n") #to allow the 3D printer to extrude at room temperatures
    j.write("G1 Z50 F1500" + "; Raise"+"\n")
    #j.write("G1 Z50 "+"\n")
    j.write("G1 F1500 E+0.5"+"; liquid at tip"+"\n")
    j.write("M400" +"\n")

    j.write("G91 " + "; RELATIVE positioning"+"\n")

    j.write("G1 " + "E+" + str(0.3) +"\n")

    class QRgcode:
        def bsquare(startx, starty, startz, n): #This section will make the Big Square
            j.write(";############ BIG SQUARE START############ BSQ:"+ str(n) +"\n")
            j.write("G90 " + "; ABSOLUTE positioning"+"\n")
            j.write("G1 " + "X"+ str(startx) + " Y" + str(starty) + "Z"+ str(startz) +" E+0.4" +"F4000" + "\n")
            j.write("M400" +"\n")
            j.write("G1 " + "Z" + str(Z) +"F3000" +"\n") #lower to plate
            j.write("G91 " + "; RELATIVE positioning"+"\n")
            j.write("M400" +"\n")
            j.write("G1 " + "X+" + str(pxl*7) +  " E+0.4" +"F500"+"\n")
            j.write("M400" +"\n")
            j.write("G1 " + "Y+" + str(pxl*7) +  " E+0.4" +"\n")
            j.write("M400" +"\n")
            j.write("G1 " + "X-" + str(pxl*7) +  " E+0.4" +"\n")
            j.write("M400" +"\n")
            j.write("G1 " + "Y-" + str(pxl*7) +  " E+0.4" +"\n")
            j.write("M400" +"\n")
            j.write("G90 " + "; ABSOLUTE positioning"+"\n")
            j.write("G1 " + "Z" + str(Z+2)  +"F3000"+ "\n") #lift from plate
            j.write("G91 " + "; RELATIVE positioning"+"\n")
            j.write("G1 " + "E-" + str(0.7) +"\n")
            j.write("M400" +"\n")
            j.write("G1 " + "X+"+ str(pxl*2) + "Y+" + str(pxl*2) + "\n") #move to position to do small square
            j.write(";############ BIG SQUARE END############"+"\n")



        def ssquare(startz, n): #This section makes the small Squares inside the big squares
            j.write(";############ SMALL SQUARE START############ SSQ:"+ str(n) +"\n")
            j.write("G90 " + "; ABSOLUTE positioning"+"\n")
            j.write("G1 " + "Z" + str(Z) +"F3000" +"\n") #lower to plate
            j.write("G91 " + "; RELATIVE positioning"+"\n")
            j.write("M400" +"\n")
            j.write("G1 " + "X+" + str(pxl*3) +  " E+0.3" +"F400"+"\n")
            j.write("M400" +"\n")
            j.write("G1 " + "Y+" + str(pxl*3) +  " E+0.3" +"\n")
            j.write("M400" +"\n")
            j.write("G1 " + "X-" + str(pxl*3) +  " E+0.3" +"\n")
            j.write("M400" +"\n")
            j.write("G1 " + "Y-" + str(pxl*3) +  " E+0.3" +"\n")
            j.write("M400" +"\n")
            j.write("G90 " + "; ABSOLUTE positioning"+"\n")
            j.write("G1 " + "Z" + str(Z+5)  +"F3000"+ "\n") #lift from plate
            j.write("G91 " + "; RELATIVE positioning"+"\n")
            j.write("G1 " + "E-" + str(0.7) +"\n")
            j.write(";############ SMALL SQUARE END############"+"\n")


        def line(n, at): #to make a QR code with lines
            j.write(";############ LINE START############"+"\n")
            j.write("G1 " + "X+" + str(pxl*at-1) +  " E+" + str(0.1) + "F2000"+"\n")
            j.write("M400" +"\n")
            j.write("G90 " + "; ABSOLUTE positioning"+"\n")
            j.write("G1 " + "Z" + str(Z) +"F3000" +"\n") #lower to plate
            j.write("G91 " + "; RELATIVE positioning"+"\n")
            j.write("M400" +"\n")
            j.write("G1 " + "X+" + str(pxl*n-1) +  " E+" + str(pxl*n*0.08) + "F400"+"\n")
            j.write("M400" +"\n")
            j.write("G1 " + "E-" + str(0.2) +"\n")
            j.write("G90 " + "; ABSOLUTE positioning"+"\n")
            j.write("G1 " + "Z" + str(Z+2)  +"F3000"+ "\n") #lift from plate
            j.write("G91 " + "; RELATIVE positioning"+"\n")
            j.write("M400" +"\n")
            j.write(";############ LINE END ############"+"\n")



        def dot(at, n): #to make a QR code with dots
            j.write(";############ DOT START ############ DOT:"+ str(n) +"\n")
            j.write("G1 " + "X+" + str(pxl*at-1) +  " E+" + str(0.1) + " F400 "+"\n")
            j.write("G90 " + "; ABSOLUTE positioning"+"\n")
            j.write("G1 " + "Z" + str(Z) +"F3000" +"\n") #lower to plate
            j.write("G91 " + "; RELATIVE positioning"+"\n")
            #j.write("G1 " + "X+" + str(pxl*at) +  " E+" + str(pxl*n*0.3) + "F300"+"\n")
            j.write("M400" +"\n")
            j.write("G1 " + "E-" + str(0.2) +"\n")
            j.write("G90 " + "; ABSOLUTE positioning"+"\n")
            j.write("G1 " + "Z" + str(Z+2)  +"F3000"+ "\n") #lift from plate
            j.write("G91 " + "; RELATIVE positioning"+"\n")
            j.write(";############ DOT END ############"+"\n")


        def newrow(n):
            j.write(";############ NEW ROW START ############ ROW:"+ str(n) +" \n")
            j.write("G90 " + "; ABSOLUTE positioning"+"\n")
            j.write("G1 " + "Z" + str(Z+3) +"F3000" +"\n") #rise from plate
            j.write("G1 " + "X" + str(startx1) + "F3000"+"\n")
            j.write("G91 " + "; RELATIVE positioning"+"\n")
            j.write("G1 " + "Y-" + str(pxl) +  " E-" + str(0.3) + "F400"+"\n")
            j.write("M400" +"\n")
            j.write(";############ NEW ROW END ############"+"\n")



    ### This section builds the Three big Squares first
    QRgcode.bsquare(startx, starty, startz, 1)
    QRgcode.ssquare(startz, 1)
    startx1=startx-pxl*14
    QRgcode.bsquare(startx1, starty, startz, 2)
    QRgcode.ssquare(startz, 2)
    starty1=starty-pxl*14
    QRgcode.bsquare(startx1, starty1, startz, 3)
    QRgcode.ssquare(startz, 3)
    ###

    #startx2=startx-pxl*21

    ###This section brings the extruder to the position to start printing the content of the QR code
    j.write("G90 " + "; ABSOLUTE positioning"+"\n")
    j.write("G1 " + "X"+ str(startx1) +" Y" + str(starty+pxl*7) + "Z"+ str(Z+5) +"F3000" + "\n") #"X"+ str(startx1) + 
    j.write("G91 " + "; RELATIVE positioning"+"\n")
    j.write("M400" +"\n")


    #n=0 #initialize n variable (used to cound length of lines)
    dot=1

    for i in range(pix): #This loop builds based on the pixels of the QR code where to position the dots using the bioprinter by scanning each row of the QR code
        k=pix-1
        empty=0
        for h in range(pix): 
            #dum=dum+QRw[i, j]
            
            if QRw[i,h]== black: #if pixel is black deposit a dot after a number of "empty" pixels
                #if n == 1:
                QRgcode.dot(empty, dot)
                empty=0
                dot=dot+1
                """if n > 1:
                    empty=empty-n
                    QRgcode.line(n, empty)
                    empty=0"""
                #n=0
            
            if QRw[i,h] == white: #if pixel is empty then check next pixel and keep track in variable "empty" how many empty pixels are acccumulating
                empty=empty+1
                #n=n+1
                #k=h+1


        '''if i <= 6:
            g= 0
        elif i in range(6, pix-6):
            g= 0
        elif i in range(pix-6, pix):
            g = 0'''
        dot=1 #restart dot count
        QRgcode.newrow(i+2) #when the row is done scanning switch to the next row
        


    j.write("G1 Z50 F3000 " +"\n")
    j.write("M400 " +"\n")
    j.write("G28 " +"\n")
    j.write("M84 " +"; Shut down steppers"+"\n")        

    print('\nYou will find your gcode in the folder of this script\n')  




QRcodefile= "qrcode.png"
QRgcode(QRcodefile)