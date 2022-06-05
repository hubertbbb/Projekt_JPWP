import socket
"""
Wykorzystując gniazdo TCP wyślij zdanie nieprzekraczające 1024
znaków do hosta 70.34.255.175, korzystającego z portu 30000.
W odpowiedzi powinieneś otrzymać identyczną wiadomość z zamienioną wielkością liter.
"""
if __name__ == "__main__":
	HOST = '70.34.255.175'
	PORT = 30000
	# Gniazdo IPv4, TCP
	s = socket.socket()
	# Wiadomość do wysłania
	message = "".encode('utf-8')
	s.close()