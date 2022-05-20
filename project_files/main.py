from host_discovery import HostDiscovery
from gui import Application
from tkinter import messagebox

hd = HostDiscovery()
hd.activate()
app = Application(hd)
app.mainloop()

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
