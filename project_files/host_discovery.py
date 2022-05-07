import nmap
import socket
import ipaddress


class HostDiscovery:
    PORT = 6000
    FORMAT = 'utf-8'
    HELLO = "11111"
    REJECT = "00000"
    MESSAGE_LENGTH = 5

    def __init__(self):
        self.reserved_ports = [self.PORT]
        self.server = None
        self.active = None
        self.ip = self._get_network()

    def _get_network(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        return ipaddress.ip_address(ip)

    def scann_network(self):
        nm = nmap.PortScanner()
        nm.scan(hosts=str(ipaddress.ip_network(str(self.ip) + "/24", strict=False)),
                arguments=f" -p {self.PORT} --open")
        return [host for host in nm.all_hosts()]

    def get_peer(self):
        connected = True
        while connected:
            conn, address = self.server.accept()
            if address[0] == str(self.ip):
                continue
            try:
                message = conn.recv(self.MESSAGE_LENGTH).decode(self.FORMAT)
                if message == self.HELLO:
                    connected = False
            except:
                continue
        print(f"[NEW CONNECTION REQUESTED] {address[0]} on port {address[1]}")
        return conn, address

    def stop(self):
        self.server.close()

    def activate(self):
        print(f"[READY FOR CONNECTIONS]")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((str(self.ip), self.PORT))
        self.active = True
        self.server.listen()

    def connect(self, host):
        port = self.reserved_ports[-1] + 1
        peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer.bind((str(self.ip), port))
        peer.connect((host, self.PORT))
        while True:
            msg = peer.recv(self.MESSAGE_LENGTH).decode(self.FORMAT)
            if msg == self.HELLO:
                return peer
            elif msg == self.REJECT:
                print("[CONNECTION REJECTED]")
                peer.close()
                return False
            else:
                continue


    def accept(self, peer):
        while True:
            ans = input(f"Accept connection from {peer[1][0]} ? (y/n)")
            if ans == 'y' or ans == 'Y':
                peer[0].send(self.HELLO.encode(self.FORMAT))
                return peer[0]
            elif ans == 'n' or ans == 'N':
                peer[0].send(self.REJECT.encode(self.FORMAT))
                print(f"Connection with {peer} closed")
                return False
            else:
                continue



