import nmap
import socket
import ipaddress


class HostDiscovery:
    PORT = 6000
    FORMAT = 'utf-8'
    HELLO = "HELLO"
    HELLO_LENGTH = 5
    def __init__(self):
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
                message = conn.recv(self.HELLO_LENGTH).decode(self.FORMAT)
                if message == self.HELLO:
                    connected = False
            except:
                continue
        print(f"[NEW CONNECTION] {address[0]} on port {address[1]}")
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
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((host, self.PORT))
            client.send(self.HELLO.encode())
            return client
        except:
            return False


