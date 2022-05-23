import threading

import nmap
import socket
import ipaddress


class HostDiscovery:
    """
    A Class to perform host discovery and establishing connections for data transmission
    """

    PORT = 6000
    FORMAT = 'utf-8'
    HELLO = "11111"
    REJECT = "00000"
    MESSAGE_LENGTH = 5

    def __init__(self):
        self.reserved_ports = [self.PORT]
        self.peers = list()
        self.main = None
        self.active = None
        self.ip = self.my_ip()

    @staticmethod
    def my_ip():
        """ Returns the IP address used to connect within LAN """

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        return ipaddress.ip_address(ip)

    def scann_network(self):
        """ Scans network to find hosts running the same application """

        nm = nmap.PortScanner()
        nm.scan(hosts=str(ipaddress.ip_network(str(self.ip) + "/24", strict=False)),
                arguments=f" -p {self.PORT} --open")
        hosts = [host for host in nm.all_hosts()]
        # Remove your own IP address
        hosts.remove(str(self.ip))
        return hosts

    def stop(self):
        """ Closing the main socket """

        # Not finished yet
        self.main.close()

    def activate(self, app):
        """ Creates the main socket """

        try:
            self.main = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.main.bind((str(self.ip), self.PORT))
            self.active = True
            self.main.listen()
        except Exception as exc:
            print(exc)
            # Notify GUI class
            return None
        else:
            print(f"[READY FOR CONNECTIONS]")
            # Now the object is ready to get connection requests
            return threading.Thread(target=self.handle_connections, args=[app])

    def handle_connections(self, app):
        """ Handles incoming connection request """

        while True:
            # Allow only valid connection requests
            # peer is of type socket
            peer = self.get_peer()
            # Ask user whether he wants to accept connection
            peer = self.accept(peer, app)
            if peer:
                # Tracking active sockets
                self.peers.append(peer)
                # Now peer object can be used to data transmission
                # peer.recv() / peer.send()
                pass
            else:
                # Connection was rejected
                print("[CONNECTION REJECTED]")
                continue

    def get_peer(self):
        """ Listens for connection requests"""

        connected = True
        while connected:
            # Get socket and address of device that wants to connect to us
            peer_socket, _ = self.main.accept()
            try:
                peer_ip = peer_socket.getpeername()[0]
                peer_port = peer_socket.getpeername()[1]
            except OSError:
                # Ignore connections made during host discovery process
                continue

            # if peer_ip == str(str(self.ip)):
                # continue
            try:
                while True:
                    # Check if it really is connection request
                    message = peer_socket.recv(self.MESSAGE_LENGTH).decode(self.FORMAT)
                    if message == self.HELLO:
                        # It is valid connection request
                        connected = False
                        print(f"[NEW CONNECTION REQUESTED] {peer_ip} on port {peer_port}")
                        return peer_socket
                    else:
                        # It is not valid connection request
                        continue
            except Exception as exc:
                print(exc)
                continue

    def accept(self, peer, app):
        """ Accept or deny connection request """

        while True:
            response = app.accept(peer)
            if response:
                peer.send(self.HELLO.encode(self.FORMAT))
                print(peer)
                print(f"[CONNECTION ESTABLISHED] {peer}")
                return peer
            else:
                peer.send(self.REJECT.encode(self.FORMAT))
                peer.close()
                print(f"[CONNECTION CLOSED] {peer}")
                return None

    def connect(self, host):
        """ Request other device to establish connection """

        port = self.reserved_ports[-1] + 1
        self.reserved_ports.append(port)
        peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer.bind((str(self.ip), port))
        peer.connect((host, self.PORT))
        peer.send(self.HELLO.encode(self.FORMAT))
        while True:
            msg = peer.recv(self.MESSAGE_LENGTH).decode(self.FORMAT)
            if msg == self.HELLO:
                return peer
            elif msg == self.REJECT:
                peer.close()
                return False
            else:
                continue

    def disconnect(self, ip_addr):
        for peer in self.peers:
            if ip_addr == peer.getpeername[0]:
                peer.close()
                self.peers.remove(peer)
