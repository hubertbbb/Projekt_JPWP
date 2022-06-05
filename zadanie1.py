from cryptography.fernet import Fernet
#należy zainstalować pakiet cryptography
#pip install cryptography


###########
#zadanie 1

#Należy odczytać treść z pliku message.txt i przy użyciu
#poniższego klucza odszyfrować wiadomość

#Podpowiedź zawartość pliku message.txt należy przekonwertować do formatu bytes

###########


key = b'No_B1Q_P547h73bZk68JxzlX91pTPYzLaXlPRWPoYoU='
f = Fernet(key)

#Miejsce na twój kod
