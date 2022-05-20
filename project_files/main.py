from host_discovery import HostDiscovery
from gui import Application
import threading
from tkinter import messagebox

if __name__ == "__main__":
    hd = HostDiscovery()
    app = Application(hd)
    app.mainloop()