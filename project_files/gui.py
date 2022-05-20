import tkinter as tk
from tkinter import messagebox
import threading


class Application(tk.Tk):
    def __init__(self, hostDiscovery):
        super().__init__()
        self.deviceOptions = [
            "Connect",
            "Show Resources",
            "Disconnect"
        ]
        self.hostBar = None
        self.myMachineBar = None
        self.topBar = None
        self.navigationBar = None
        self.hostDiscovery = hostDiscovery
        self.hdThread = self.hostDiscovery.activate(self)
        self.hdThread.start()
        self.title("Title")
        self.createWidgets()
        self.deviceButtons = []

    def createWidgets(self):
        self.topBar = tk.LabelFrame(self, text="self.topBar", width=1000, height=150)
        self.navigationBar = tk.LabelFrame(self, text="navBar", width=200, height=500)
        self.myMachineBar = tk.LabelFrame(self, text="self.myMachineBar", width=400, height=500)
        self.hostBar = tk.LabelFrame(self, text="self.hostBar", width=400, height=500)

        self.topBar.grid(row=0, column=0, columnspan=3, sticky="ew")
        self.navigationBar.grid(row=1, column=0)
        self.myMachineBar.grid(row=1, column=1)
        self.hostBar.grid(row=1, column=2)

        self.topBar.grid_propagate(False)
        self.navigationBar.grid_propagate(False)
        self.myMachineBar.grid_propagate(False)
        self.hostBar.grid_propagate(False)

        navDefaultLabel = tk.Label(self.navigationBar, text="No devices found")
        navDefaultLabel.grid()

        findDevicesButton = tk.Button(self.topBar, text="Find Devices", command=self.scan)
        findDevicesButton.grid()

    def deviceActions(self):
        pass

    def scan(self):
        for widget in self.navigationBar.winfo_children():
            widget.destroy()
        devices = self.hostDiscovery.scann_network()
        if len(devices) == 0:
            navDefaultLabel = tk.Label(self.navigationBar, text="No devices found")
            navDefaultLabel.grid()
        else:
            for device in devices:
                menuButton = tk.Menubutton(self.navigationBar, text=device, background='#f55442')
                menu = tk.Menu(menuButton, tearoff=0)
                menu.add_command(label="Connect", command=lambda: self.connect(device))
                menuButton['menu'] = menu
                self.deviceButtons.append(menuButton)
                self.deviceButtons[-1].pack()

    def connect(self, device):
        peer = self.hostDiscovery.connect(device)
        if peer:
            for deviceButton in self.deviceButtons:
                if deviceButton.cget('text') == device:
                    # print(deviceButton.cget('menu'))
                    deviceButton.config(background='#42f58d')
                    menu = tk.Menu(deviceButton, tearoff=0)
                    menu.add_command(label="Disconnect", command=lambda: self.disconnect(device))
                    menu.add_command(label="Show resources", command=lambda: self.show_resources(device))
                    deviceButton['menu'] = menu
                    # print(deviceButton.winfo_children())
                else:
                    continue
        else:
            messagebox.showerror("Error", f"Connection with {device} refused")

    def disconnect(self, device):
        pass

    def show_resources(self, device):
        pass

    def accept(self, peer):
        host = peer[1][0]
        response = messagebox.askyesno("Access request", f"Accept connection from {host} ?")
        if response:
            if host in map(lambda x: x.cget('text'), self.deviceButtons):
                for deviceButton in self.deviceButtons:
                    if deviceButton.cget('text') == host:
                        deviceButton.config(background='#42f58d')
                        menu = tk.Menu(deviceButton, tearoff=0)
                        menu.add_command(label="Disconnect", command=lambda: self.disconnect(device))
                        menu.add_command(label="Show resources", command=lambda: self.show_resources(device))
                        deviceButton['menu'] = menu
                    else:
                        continue
            else:
                self.deviceButtons.append(tk.Button(self.navigationBar, text=host, background='#42f58d',
                                                    command=lambda: self.hostDiscovery.connect(host)))
                self.deviceButtons[-1].pack()

        return response

    def switchWidget(self):
        pass
