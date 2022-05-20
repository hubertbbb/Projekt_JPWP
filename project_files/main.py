from host_discovery import HostDiscovery
from gui import Application
import threading
from tkinter import messagebox

hd = HostDiscovery()
hd.activate()
app = Application(hd)
app_thread = threading.Thread(target=app.mainloop)
app_thread.start()
while True:
    # peer = (socket, (ip, port))
    peer = hd.get_peer()
    # peer = socket
    peer = hd.accept(peer, app)
    if peer:
        # mozna wymienac dane:
        # peer.recv() / peer.send()
        pass
    else:
        continue
