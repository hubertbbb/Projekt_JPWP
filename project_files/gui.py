import tkinter as tk
from tkinter import messagebox
import threading
from functools import partial
from tkinter import filedialog


class Application(tk.Tk):
    def __init__(self, host_discovery):
        super().__init__()
        self.deviceOptions = [
            "Connect",
            "Show Resources",
            "Disconnect"
        ]
        self.downloads_folder = self.set_downloads_folder()
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
        Structure of elements in self.shared_resource_frames:
        {"ip of peer": {
            "my_device_frame": Frame widget,
            "peer_frame": Frame widget
        }}
        """
        self.shared_resources_frames = dict()
        """
        Structure of elements in self.shared_resource_widgets:
        {"ip of peer": {
            "my_device_frame": [list of Label widgets],
            "peer_frame": [list of Checkbutton widgets]
        }}
        """
        self.shared_resources_widgets = dict()

    def create_widgets(self):
        self.top_frame = tk.LabelFrame(self, text="self.top_frame", width=1000, height=150)
        self.devices_frame = tk.LabelFrame(self, text="navBar", width=200, height=500)
        self.my_device_frame = tk.LabelFrame(self, text="self.my_device_frame", width=400, height=500)
        self.peer_frame = tk.LabelFrame(self, text="self.peer_frame", width=400, height=500)

        self.top_frame.grid(row=0, column=0, columnspan=3, sticky="ew")
        self.devices_frame.grid(row=1, column=0)
        self.my_device_frame.grid(row=1, column=1)
        self.peer_frame.grid(row=1, column=2)

        self.top_frame.grid_propagate(False)
        self.devices_frame.grid_propagate(False)
        self.my_device_frame.grid_propagate(False)
        self.peer_frame.grid_propagate(False)

        devices_default_label = tk.Label(self.devices_frame, text="No devices found")
        devices_default_label.grid()

        find_devices_button = tk.Button(self.top_frame, text="Find Devices", command=self.scan)
        find_devices_button.grid()

    def set_downloads_folder(self):
        """ Sets destination folder for files to be downloaded """
        downloads_folder = filedialog.askdirectory(title="Choose directory for downloaded files")
        while not downloads_folder:
            downloads_folder = filedialog.askdirectory(title="Choose directory for downloaded files")
        return downloads_folder

    def scan(self):
        """ Scans network and puts founded devices into devices_frame"""
        for widget in self.devices_frame.winfo_children():
            widget.destroy()
        devices = self.host_discovery.scan_network()
        if len(devices) == 0:
            devices_default_label = tk.Label(self.devices_frame, text="No devices found")
            devices_default_label.grid()
        else:
            self.peer_menu_buttons = []
            for device in devices:
                device_button = tk.Menubutton(self.devices_frame, text=device, background='#f55442')
                menu = tk.Menu(device_button, tearoff=0)
                connect_method = partial(self.connect, device)
                menu.add_command(label="Connect", command=connect_method)
                device_button['menu'] = menu
                self.peer_menu_buttons.append(device_button)
                self.peer_menu_buttons[-1].pack()

    def connect(self, peer_ip):
        """ Establishes connection with given peer"""
        peer_socket = self.host_discovery.connect(peer_ip)
        # Connection successful, peer_socket was assigned value
        if peer_socket:
            for peer_menu_button in self.peer_menu_buttons:
                if peer_menu_button.cget('text') == peer_ip:
                    # Change peer's Menubutton color to green
                    peer_menu_button.config(background='#42f58d')
                    # Create new menu with 'Disconnect' and 'Show resources' commands
                    menu = tk.Menu(peer_menu_button, tearoff=0)
                    disconnect_method = partial(self.disconnect, peer_ip)
                    show_resources_method = partial(self.show_resources, peer_ip)
                    menu.add_command(label="Disconnect", command=disconnect_method)
                    menu.add_command(label="Show resources", command=show_resources_method)
                    # Replace 'Connect' command with 'Disconnect' and 'Show resources'
                    peer_menu_button['menu'] = menu
                    # Tracking shared resources frames
                    self.shared_resources_frames[peer_ip] = self.create_frames(peer_ip)
                    # Tracking shared resources widgets containing filenames
                    self.shared_resources_widgets[peer_ip] = self.create_resource_widgets(peer_ip)
                else:
                    continue
        # Connection failed, peer_socket is None
        else:
            messagebox.showerror("Error", f"Connection with {peer_ip} refused")

    def get_files_from_frame(self, frame):
        """ Returns list of filenames of given frame """
        filenames = []
        for widget in frame.winfo_children():
            # In case we deal with my_device_frame with Labels
            if isinstance(widget, tk.Checkbutton):
                filenames.append(widget.cget('text'))
            # In case we deal with peer_frame with Checkbuttons
            elif isinstance(widget, tk.Label):
                filenames.append(widget.cget('text'))
            # Button widget
            else:
                continue
        return filenames

    def add_files_to_frame(self, frame, is_peer_frame):
        """
        Adds files that will be shared with corresponding peer

        Depending on the is_peer_flag, this method will modify either
        my_device_frame or peer_frame. The distinction is important because
        my_device_frame have to invoke file dialog to add filenames into Labels,
        while peer_frame have to receive filenames from peer and put them into
        Checkbuttons.
        """
        # These are files shared by peer
        if is_peer_frame:
            # Invoke method that will get names of file shared by peer
            filenames = []
            # Checkbuttons will store filenames
            check_buttons = []
            for filename in filenames:
                file_exists = False
                # Check if a file is already in the checkbox
                for widget in frame.winfo_children():
                    if isinstance(widget, tk.Checkbutton):
                        if widget.cget('text') == filename:
                            # File is already in checkbox
                            file_exists = True
                            break
                        else:
                            # Check another one
                            continue
                    # Temporarily remove 'Download' button
                    if isinstance(widget, tk.Button):
                        widget.destroy()
                # No Checkbutton with matching filename found - create one
                if not file_exists:
                    check_buttons.append(tk.Menubutton(frame, text=filename))
            # Add file Checkbuttons to peer_frame
            for checkbutton in check_buttons:
                checkbutton.pack()
            # Restore 'Download' button
            download_files_method = partial(self.download_files, frame)
            download_button = tk.Button(frame, text='Download files', command=download_files_method)
            download_button.pack()
        # These are files that we want to share with particular peer
        else:
            # Select file that we want to share
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
                for widget in frame.winfo_children():
                    if isinstance(widget, tk.Label):
                        if widget.cget('text') == filename:
                            print("file already reside in the table")
                            return
                    # Temporarily remove 'Add files' button
                    if isinstance(widget, tk.Button):
                        widget.destroy()
                # No Label with matching filename found - create one
                label = tk.Label(frame, text=filename)
                label.pack()
                # Restore 'Add files' button
                add_files_method = partial(self.add_files_to_frame, frame, False)
                add_button = tk.Button(frame, text='Add files', command=add_files_method)
                add_button.pack()

    def download_files(self, frame):
        """ Downloads files from peer """
        pass

    def create_resource_widgets(self, peer):
        """ Adds 'add files' button to my_device_frame and 'download' button to peer_frame"""
        widgets = dict()
        my_device_frame = self.shared_resources_frames[peer]['my_device_frame']
        peer_frame = self.shared_resources_frames[peer]['peer_frame']
        add_files_method = partial(self.add_files_to_frame, my_device_frame, False)
        download_files_method = partial(self.download_files, peer_frame)
        add_button = tk.Button(my_device_frame, text='Add files', command=add_files_method)
        download_button = tk.Button(peer_frame, text='Download files', command=download_files_method)
        add_button.pack()
        download_button.pack()
        widgets['my_host_widgets'] = [add_button]
        widgets['peer_widgets'] = [download_button]
        return widgets

    def show_resources(self, peer_ip):
        """
        This command is added to Menubutton when connection with peer is established

        It simply finds my_device_frame and peer_frame associated with given peer_ip in
        self.shared_resources_frames dictionary and puts them into main window.

        Structure of elements in self.shared_resource_frames:
        {"ip of peer": {
            "my_device_frame": frame-widget,
            "peer_frame": frame-widget,
        }}
        """
        # Replace currently displayed 'my_device_frame'
        self.my_device_frame.grid_remove()
        self.my_device_frame = self.shared_resources_frames[peer_ip]["my_device_frame"]
        self.my_device_frame.grid(row=1, column=1)
        # Replace currently displayed 'peer_frame'
        self.peer_frame.grid_remove()
        self.peer_frame = self.shared_resources_frames[peer_ip]["peer_frame"]
        self.peer_frame.grid(row=1, column=2)

    def disconnect(self, peer_ip):
        """
        This command is added to Menubutton when connection with peer is established

        It removes all widgets associated with given peer_ip

        Structure of elements in self.shared_resource_frames:
        {"ip of peer": {
            "my_device_frame": frame-widget,
            "peer_frame": frame-widget,
        }}
        """
        # Remove frames
        self.my_device_frame.grid_remove()
        self.peer_frame.grid_remove()
        # Don't need to track frames anymore
        self.shared_resources_frames.pop(peer_ip)
        # Put 'default' frames into main window
        self.my_device_frame = tk.LabelFrame(self, text="self.my_device_frame", width=400, height=500)
        self.peer_frame = tk.LabelFrame(self, text="self.peer_frame", width=400, height=500)
        self.my_device_frame.grid(row=1, column=1)
        self.peer_frame.grid(row=1, column=2)
        self.my_device_frame.grid_propagate(False)
        self.peer_frame.grid_propagate(False)

        for device_button in self.peer_menu_buttons:
            if device_button.cget('text') == peer_ip:
                # Remove Menubutton with peer_ip
                device_button.destroy()
                self.peer_menu_buttons.remove(device_button)
                # Let the peer know about end of connection
                self.host_discovery.disconnect(peer_ip)
            else:
                continue

    def create_frames(self, peer_ip):
        """ Create new resource frames """
        frames = dict()
        my_device_frame = tk.LabelFrame(self, text=self.host_discovery.ip, width=400, height=500)
        peer_frame = tk.LabelFrame(self, text=peer_ip, width=400, height=500)
        frames["my_device_frame"] = my_device_frame
        frames["peer_frame"] = peer_frame
        return frames

    def accept(self, peer):
        """ Ask user whether he wants to establish connection with peer of given ip address"""
        peer_ip = peer.getpeername()[0]
        response = messagebox.askyesno("Access request", f"Accept connection from {peer_ip} ?")
        if response:
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
            else:
                device_button = tk.Menubutton(self.devices_frame, text=peer_ip, background='#42f58d')
                menu = tk.Menu(device_button, tearoff=0)
                menu.add_command(label="Disconnect", command=lambda: self.disconnect(peer_ip))
                menu.add_command(label="Show resources", command=lambda: self.show_resources(peer_ip))
                device_button['menu'] = menu
                self.peer_menu_buttons.append(device_button)
                self.peer_menu_buttons[-1].pack()
        return response
