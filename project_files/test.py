from host_discovery import HostDiscovery

hd = HostDiscovery()
hd.activate()

while True:
    # peer = (socket, (ip, port))
    peer = hd.get_peer()
    # peer = socket
    peer = hd.accept(peer)
    if peer:
        # mozna wymienac dane:
        # peer.recv() / peer.send()
        pass
    else:
        continue
