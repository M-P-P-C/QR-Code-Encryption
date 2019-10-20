# QR Code Encryption in Python

This python script was developed as a part to the project for the IGEM (international Genetic Enegineered Machines) competition by team Groningen 2019.

![alt text](https://raw.githubusercontent.com/M-P-P-C/QR-Code-Encryption/master/Example_QRcode_encrypted.png | width=100)


The goal of the script is to develop QR codes with AES encrypted messages and be able to decrypt them.

Encryption of a message will output a 3D version of the QR code to be 3D printed, or in PNG format.

Extruded version is achieved by extruding the png version using the numpy2stl script

HOW TO RUN:
- in the downloaded folder run the command "pip install -r requirements.txt" to install all requirements
- run python script "aesQRv2.py" and follow instructions in command line
- The final QR code files are outputted in the same folder as the python script
