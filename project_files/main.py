from host_discovery import HostDiscovery
from gui import Application
import threading
from tkinter import messagebox

if __name__ == "__main__":
    app = Application(HostDiscovery())
    app.mainloop()
