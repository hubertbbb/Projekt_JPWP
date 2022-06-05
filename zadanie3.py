import nmap
"""
Korzystając z modułu python-nmap przeskanuj dostępne porty TCP od 1 do 100 
hosta o adresie 70.34.255.175, a następnie wyświetl ich stan

Podpowiedź: Zobacz co zawiera struktura zwracana przez metode scan()
"""
if __name__ == "__main__":
	IP = '70.34.255.175'
	nm = nmap.PortScanner()
	result = nm.scan()
