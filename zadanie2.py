import http.server
import socket
import socketserver
import webbrowser #Podpowiedź
import pyqrcode
import os
from tkinter import filedialog

#należy zainstalować pakiet pyqrcode
#pip install pyqrcode

###############
#Zadanie 2

# W odpowiednim miejscu wygenerować Kod QR z zmiennej IP, zapisanie do formatu svg
# oraz otwarcie zapisanego obrazu w przeglądarce

###############


# assigning the appropriate port value
PORT = 8010

directory = filedialog.askdirectory(title="Wybierz folder do udostępnienia")
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

##################################
#Miejsce na twój kod





##################################

# Creating the HTTP request and  serving the
# folder in the PORT 8010,and the pyqrcode is generated

# continuous stream of data between client and server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    print("Type this in your Browser", IP)
    print("or Use the QRCode")
    httpd.serve_forever()