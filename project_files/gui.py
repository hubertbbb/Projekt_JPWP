import tkinter as tk
from tkinter import messagebox
import threading
from functools import partial

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
        self.create_widgets()
        self.device_buttons = list()
        self.shared_resources = dict()

    def create_widgets(self):
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
            self.device_buttons = []
            for device in devices:
                device_button = tk.Menubutton(self.navigationBar, text=device, background='#f55442')
                menu = tk.Menu(device_button, tearoff=0)
                command = partial(self.connect, device)
                menu.add_command(label="Connect", command=command)
                device_button['menu'] = menu
                self.device_buttons.append(device_button)
                self.device_buttons[-1].pack()

    def connect(self, device):
        peer = self.hostDiscovery.connect(device)
        if peer:
            for device_button in self.device_buttons:
                if device_button.cget('text') == device:
                    # print(device_button.cget('menu'))
                    device_button.config(background='#42f58d')
                    menu = tk.Menu(device_button, tearoff=0)
                    menu.add_command(label="Disconnect", command=lambda: self.disconnect(device))
                    menu.add_command(label="Show resources", command=lambda: self.show_resources(device))
                    device_button['menu'] = menu
                    # Tracking shared resources
                    self.shared_resources[device] = self.create_frames(device)
                    # print(device_button.winfo_children())
                else:
                    continue
        else:
            messagebox.showerror("Error", f"Connection with {device} refused")

    def show_resources(self, device):
        for peer_resources in self.shared_resources.keys():
            if peer_resources == device:
                self.myMachineBar.grid_remove()
                self.myMachineBar = self.shared_resources[peer_resources]["my_host_frame"]
                self.myMachineBar.grid(row=1, column=1)
                self.hostBar.grid_remove()
                self.hostBar = self.shared_resources[peer_resources]["peer_frame"]
                self.hostBar.grid(row=1, column=2)
                # self.hostBar.grid(row=1, column=2)
            else:
                continue

    def disconnect(self, device):
        for device_button in self.device_buttons:
            if device_button.cget('text') == device:
                device_button.destroy()
                self.hostDiscovery.disconnect(device)
            else:
                continue

    def create_frames(self, device):
        frames = dict()
        my_host_frame = tk.LabelFrame(self, text=self.hostDiscovery.ip, width=400, height=500)
        # my_host_frame.grid(row=1, column=1)
        peer_frame = tk.LabelFrame(self, text=device, width=400, height=500)
        # peer_frame.grid(row=1, column=2)
        frames["my_host_frame"] = my_host_frame
        frames["peer_frame"] = peer_frame
        return frames

    def accept(self, peer):
        peer_ip = peer.getpeername()[0]
        response = messagebox.askyesno("Access request", f"Accept connection from {peer_ip} ?")
        if response:
            if peer_ip in map(lambda x: x.cget('text'), self.device_buttons):
                for device_button in self.device_buttons:
                    if device_button.cget('text') == peer_ip:
                        device_button.config(background='#42f58d')
                        menu = tk.Menu(device_button, tearoff=0)
                        menu.add_command(label="Disconnect", command=lambda: self.disconnect(peer_ip))
                        menu.add_command(label="Show resources", command=lambda: self.show_resources(peer_ip))
                        device_button['menu'] = menu
                    else:
                        continue
            else:
                device_button = tk.Menubutton(self.navigationBar, text=peer_ip, background='#42f58d')
                menu = tk.Menu(device_button, tearoff=0)
                menu.add_command(label="Disconnect", command=lambda: self.disconnect(peer_ip))
                menu.add_command(label="Show resources", command=lambda: self.show_resources(peer_ip))
                device_button['menu'] = menu
                self.device_buttons.append(device_button)
                self.device_buttons[-1].pack()
                # self.device_buttons.append(tk.Button(self.navigationBar, text=peer_ip, background='#42f58d',
                #                                     command=lambda: self.hostDiscovery.connect(peer_ip)))
                # self.device_buttons[-1].pack()

        return response
