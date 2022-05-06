from host_discovery import HostDiscovery
import threading
import time

hd = HostDiscovery()
hd.activate()
print(hd.ip)

def test():
    while True:
        peer = hd.get_peer()
        print(peer)

print(hd.scann_network())
host = hd.scann_network()[1]
t = threading.Thread(target=test)
t.start()
time.sleep(2)
if hd.connect(host):
    print(f"connected with {host}")