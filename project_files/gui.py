import tkinter as tk
from tkinter import messagebox
import threading
from functools import partial
from tkinter import filedialog
from qr_share import local_share
from client import send_file

class Application(tk.Tk):
    def __init__(self, host_discovery):
        super().__init__()
        self.deviceOptions = [
            "Connect",
            "Show Resources",
            "Disconnect"
        ]
        self.peer_frame = None
        self.my_device_frame = None
        self.top_frame = None
        self.devices_frame = None
        self.host_discovery = host_discovery
        self.hdThread = self.host_discovery.activate(self)
        self.hdThread.start()
        self.title("Title")
        self.create_widgets()

        # Elements to track
        self.peer_menu_buttons = list()
        """
        Structure of elements in self.shared_files:
        {
            "ip of peer": [filenames]
        }
        """
        self.shared_files = dict()

    def create_widgets(self):
        """ Creates all necessary widgets"""

        self.devices_frame = tk.LabelFrame(self, text="Devices", width=200, height=500)
        self.my_device_frame = tk.LabelFrame(self, text="my_device_frame", width=800, height=500)

        self.devices_frame.grid(row=1, column=0)
        self.my_device_frame.grid(row=1, column=1, columnspan=3)

        self.devices_frame.grid_propagate(False)
        self.my_device_frame.grid_propagate(False)

        find_devices_button = tk.Button(self, text="Find Devices", command=self.scan)
        find_devices_button.grid(row=2, column=0)

        local_share_button = tk.Button(self, text="Share files locally", command=lambda: local_share())
        local_share_button.grid(row=2, column=1)

        add_button = tk.Button(self, text='Add files', command=self.add_files_to_frame)
        add_button.grid(row=2, column=2)

        send_button = tk.Button(self, text='Send files', command=self.send_selected_files)
        send_button.grid(row=2, column=3)

        devices_default_label = tk.Label(self.devices_frame, text="No devices found")
        devices_default_label.grid()

    def scan(self):
        """ Scans network and puts founded devices into devices_frame """

        # Remove widgets in devices_frame
        for widget in self.devices_frame.winfo_children():
            widget.destroy()
        # Get list of peers ready to establish connection
        peer_list = self.host_discovery.scan_network()
        if len(peer_list) == 0:
            # No devices found - put the default label
            devices_default_label = tk.Label(self.devices_frame, text="No devices found")
            devices_default_label.grid()
        else:
            # For each peer create Menubutton and put them into devices_frame
            for peer in peer_list:
                # Red color = Connection with peer not established yet
                device_button = tk.Menubutton(self.devices_frame, text=peer, background='#f55442')
                menu = tk.Menu(device_button, tearoff=0)
                connect_method = partial(self.connect, peer)
                # Add 'Connect' option
                menu.add_command(label="Connect", command=connect_method)
                device_button['menu'] = menu
                device_button.grid()

    def connect(self, peer_ip):
        """ Establishes connection with given peer"""

        peer_socket = self.host_discovery.connect(peer_ip)
        # Connection successful, peer_socket was assigned value
        if peer_socket:
            for menu_button in self.devices_frame.winfo_children():
                if menu_button.cget('text') == peer_ip:
                    # Change peer's Menubutton color to green
                    menu_button.config(background='#42f58d')
                    menu = tk.Menu(menu_button, tearoff=0)
                    # Create new menu with 'Disconnect' and 'Show resources' commands
                    disconnect_method = partial(self.disconnect, peer_ip)
                    show_resources_method = partial(self.show_resources, peer_ip)
                    menu.add_command(label="Disconnect", command=disconnect_method)
                    menu.add_command(label="Show resources", command=show_resources_method)
                    # Replace 'Connect' command with 'Disconnect' and 'Show resources'
                    menu_button['menu'] = menu
        else:
            messagebox.showerror("Error", f"Connection with {peer_ip} refused")

    def add_files_to_frame(self):
        # Select file that we want to share
        peer_ip = self.my_device_frame.cget('text')
        filename = filedialog.askopenfilename(title="Select a file",
                                              filetypes=(("all files", "*"),
                                                         ("text files", "*.txt"),
                                                         ))
        # No file has been selected
        if not filename:
            return
        # Some file has been selected
        else:
            # Check if a file is already in the Label
            if peer_ip in self.shared_files:
                if filename in self.shared_files[peer_ip]:
                    print("file already reside in the table")
                    return
                else:
                    self.shared_files[peer_ip].append(filename)
                    tk.Label(self.my_device_frame, text=filename).grid()
            else:
                self.shared_files[peer_ip] = list()

    def send_selected_files(self):
        peer_ip = self.my_device_frame.cget('text')
        print("Sending files...")
        # print(self.peer_ip)
        for file in self.shared_files[peer_ip]:
            send_file(peer_ip, file)

    def show_resources(self, peer_ip):
        self.my_device_frame.config(text=peer_ip)
        for widget in self.my_device_frame.winfo_children():
            widget.destroy()

        if peer_ip in self.shared_files:
            for file in self.shared_files[peer_ip]:
                tk.Label(self.my_device_frame, text=file).grid()
        else:
            self.shared_files[peer_ip] = list()

    def disconnect(self, peer_ip):
        """
        This command is added to Menubutton when connection with peer is established

        It removes all widgets associated with given peer_ip
        """
        self.my_device_frame.config(text="No device selected")
        for widget in self.my_device_frame.winfo_children():
            widget.destroy()

        for widget in self.devices_frame.winfo_children():
            if widget.cget('text') == peer_ip:
                widget.destroy()

        del self.shared_files[peer_ip]

    def accept(self, peer):
        """ Ask user whether he wants to establish connection with peer of given ip address"""

        peer_ip = peer.getpeername()[0]
        print(peer_ip)
        self.peer_ip = peer_ip
        response = messagebox.askyesno("Access request", f"Accept connection from {peer_ip} ?")
        if response:
            # Check if peer already resides in devices_frame
            # If so - change it's color to green and add 'Disconnect' and 'Show resources' option
            if peer_ip in map(lambda x: x.cget('text'), self.peer_menu_buttons):
                for device_button in self.peer_menu_buttons:
                    if device_button.cget('text') == peer_ip:
                        device_button.config(background='#42f58d')
                        menu = tk.Menu(device_button, tearoff=0)
                        menu.add_command(label="Disconnect", command=lambda: self.disconnect(peer_ip))
                        menu.add_command(label="Show resources", command=lambda: self.show_resources(peer_ip))
                        device_button['menu'] = menu
                    else:
                        continue
            # Peer not present in devices_frame - create new Menubutton
            else:
                device_button = tk.Menubutton(self.devices_frame, text=peer_ip, background='#42f58d')
                menu = tk.Menu(device_button, tearoff=0)
                menu.add_command(label="Disconnect", command=lambda: self.disconnect(peer_ip))
                menu.add_command(label="Show resources", command=lambda: self.show_resources(peer_ip))
                device_button['menu'] = menu
                # Track new Menubutton
                self.peer_menu_buttons.append(device_button)
                self.peer_menu_buttons[-1].grid()
        return response
