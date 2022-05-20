import tkinter as tk
from tkinter import messagebox
import threading


class Application(tk.Tk):
    def __init__(self, hostDiscovery):
        super().__init__()
        self.hostDiscovery = hostDiscovery
        self.hdThread = self.hostDiscovery.activate(self)
        self.hdThread.start()
        self.title("Title")
        self.createWidgets()
        self.deviceButtons = []

    def createWidgets(self):
        topBar = tk.LabelFrame(self, text="topBar", width=1000, height=150)
        navigationBar = tk.LabelFrame(self, text="navBar", width=200, height=500)
        myMachineBar = tk.LabelFrame(self, text="myMachineBar", width=400, height=500)
        hostBar = tk.LabelFrame(self, text="hostBar", width=400, height=500)

        topBar.grid(row=0, column=0, columnspan=3, sticky="ew")
        navigationBar.grid(row=1, column=0)
        myMachineBar.grid(row=1, column=1)
        hostBar.grid(row=1, column=2)

        topBar.grid_propagate(False)
        navigationBar.grid_propagate(False)
        myMachineBar.grid_propagate(False)
        hostBar.grid_propagate(False)

        navDefaultLabel = tk.Label(navigationBar, text="No devices found")
        navDefaultLabel.grid()

        findDevicesButton = tk.Button(topBar, text="Find Devices", command=lambda: self.scan(navigationBar))
        findDevicesButton.grid()

    def scan(self, navBar):
        for widget in navBar.winfo_children():
            widget.destroy()
        devices = self.hostDiscovery.scann_network()
        deviceButtons = []
        if len(devices) == 0:
            navDefaultLabel = tk.Label(navBar, text="No devices found")
            navDefaultLabel.grid()
        else:
            for device in devices:
                deviceButtons.append(tk.Button(navBar, text=device,
                                               command=lambda: self.hostDiscovery.connect(device)))
                deviceButtons[-1].pack()

    @staticmethod
    def accept(peer):
        response = messagebox.askyesno("Access request", f"Accept connection from {peer[1][0]} ?")
        return response

    def switchWidget(self):
        pass
