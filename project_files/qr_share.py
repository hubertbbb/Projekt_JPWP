import http.server
import socket
import socketserver
import webbrowser
import pyqrcode
from pyqrcode import QRCode
import png
import os
from tkinter import filedialog


def local_share():
    # assigning the appropriate port value
    PORT = 8010

    directory = filedialog.askdirectory(title="Wybierz folder do udostępnienia")

    # changing the directory to access the files desktop
    # with the help of os module
    desktop = os.path.join(directory)
    os.chdir(desktop)

    # creating a http request
    Handler = http.server.SimpleHTTPRequestHandler
    # returns, host name of the system under
    # which Python interpreter is executed
    hostname = socket.gethostname()

    # finding the IP address of the PC
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IP = "http://" + s.getsockname()[0] + ":" + str(PORT)
    link = IP

    # converting the IP address into the form of a QRcode
    # with the help of pyqrcode module

    # converts the IP address into a Qrcode
    url = pyqrcode.create(link)
    # saves the Qrcode inform of svg
    url.svg("myqr.svg", scale=8)
    # opens the Qrcode image in the web browser
    webbrowser.open('myqr.svg')

    # Creating the HTTP request and  serving the
    # folder in the PORT 8010,and the pyqrcode is generated

    # continuous stream of data between client and server
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        print("Type this in your Browser", IP)
        print("or Use the QRCode")
        httpd.serve_forever()
