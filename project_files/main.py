from host_discovery import HostDiscovery
from gui import Application
import threading
from tkinter import messagebox

hd = HostDiscovery()
app = Application(hd)
app.mainloop()