import tkinter as tk
from tkinter import messagebox
import threading
from functools import partial
from tkinter import filedialog


class Application(tk.Tk):
    def __init__(self, hostDiscovery):
        super().__init__()
        self.deviceOptions = [
            "Connect",
            "Show Resources",
            "Disconnect"
        ]
        self.downloads_folder = self.set_downloads_folder()
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
        self.shared_resources_frames = dict()
        self.shared_resources_widgets = dict()

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

    def set_downloads_folder(self):
        """ Sets destination folder for files to be downloaded """
        downloads_folder = filedialog.askdirectory(title="Choose directory for downloaded files")
        while not downloads_folder:
            downloads_folder = filedialog.askdirectory(title="Choose directory for downloaded files")
        return downloads_folder

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
                connect_method = partial(self.connect, device)
                menu.add_command(label="Connect", command=connect_method)
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
                    disconnect_method = partial(self.disconnect, device)
                    show_resources_method = partial(self.show_resources, device)
                    menu.add_command(label="Disconnect", command=disconnect_method)
                    menu.add_command(label="Show resources", command=show_resources_method)
                    device_button['menu'] = menu
                    # Tracking shared resources frames
                    self.shared_resources_frames[device] = self.create_frames(device)
                    self.shared_resources_widgets[device] = self.create_resource_widgets(device)
                    # print(device_button.winfo_children())
                else:
                    continue
        else:
            messagebox.showerror("Error", f"Connection with {device} refused")

    def get_files_from_frame(self, frame):
        """ Returns list of filenames of given frame """
        filenames = []
        for widget in frame.winfo_children():
            # In case we deal with my_host_frame
            if isinstance(widget, tk.Checkbutton):
                filenames.append(widget.cget('text'))
            # In case we deal with peer_frame
            elif isinstance(widget, tk.Label):
                filenames.append(widget.cget('text'))
            # Button widget
            else:
                continue
        return filenames

    def add_files_to_frame(self, frame, is_peer_frame):
        """ Adds files that will be shared with corresponding peer """
        # These are files shared by peer
        if is_peer_frame:
            # Invoke method that will give files shared by peer
            filenames = []
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
                # No Checkbutton with matching filename found - create one:
                if not file_exists:
                    check_buttons.append(tk.Menubutton(frame, text=filename))
            # Add file checkboxes to frame
            for checkbutton in check_buttons:
                checkbutton.pack()
            # Restore 'Download' button
            download_files_method = partial(self.download_files, frame)
            download_button = tk.Button(frame, text='Download files', command=download_files_method)
            download_button.pack()
        # These are files that we want to share with peer
        else:
            # Select file that we want to share with peer
            filename = filedialog.askopenfilename(title="Select a file",
                                                  filetypes=(("all files", "*"),
                                                             ("text files", "*.txt"),
                                                             ))
            # No file has been selected
            if not filename:
                return
            # Some file has been selected
            else:
                # Check if a file is already in the checkbox
                for widget in frame.winfo_children():
                    if isinstance(widget, tk.Label):
                        if widget.cget('text') == filename:
                            print("file already reside in the table")
                            return
                    # Temporarily remove 'Add files' button
                    if isinstance(widget, tk.Button):
                        widget.destroy()
                # No Label with matching filename found - create one:
                label = tk.Label(frame, text=filename)
                label.pack()
                # Restore 'Add files' button
                add_files_method = partial(self.add_files_to_frame, frame, False)
                add_button = tk.Button(frame, text='Add files', command=add_files_method)
                add_button.pack()
                # Checkbutton(frame, text=filename, command=lambda: download(filename)).pack()

    def download_files(self, frame):
        pass

    def create_resource_widgets(self, peer):
        """ Adds 'add files' button to my_host_frame and 'download' button to peer_frame"""
        widgets = dict()
        my_host_frame = self.shared_resources_frames[peer]['my_host_frame']
        peer_frame = self.shared_resources_frames[peer]['peer_frame']
        add_files_method = partial(self.add_files_to_frame, my_host_frame, False)
        download_files_method = partial(self.download_files, peer_frame)
        add_button = tk.Button(my_host_frame, text='Add files', command=add_files_method)
        download_button = tk.Button(peer_frame, text='Download files', command=download_files_method)
        add_button.pack()
        download_button.pack()
        widgets['my_host_widgets'] = [add_button]
        widgets['peer_widgets'] = [download_button]
        return widgets

    def show_resources(self, peer):
        self.myMachineBar.grid_remove()
        self.myMachineBar = self.shared_resources_frames[peer]["my_host_frame"]
        self.myMachineBar.grid(row=1, column=1)
        self.hostBar.grid_remove()
        self.hostBar = self.shared_resources_frames[peer]["peer_frame"]
        self.hostBar.grid(row=1, column=2)

    def disconnect(self, device):
        self.myMachineBar.grid_remove()
        self.hostBar.grid_remove()
        self.myMachineBar = tk.LabelFrame(self, text="self.myMachineBar", width=400, height=500)
        self.hostBar = tk.LabelFrame(self, text="self.hostBar", width=400, height=500)
        self.myMachineBar.grid(row=1, column=1)
        self.hostBar.grid(row=1, column=2)
        self.myMachineBar.grid_propagate(False)
        self.hostBar.grid_propagate(False)
        self.shared_resources_frames.pop(device)

        for device_button in self.device_buttons:
            if device_button.cget('text') == device:
                device_button.destroy()
                self.device_buttons.remove(device_button)
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
