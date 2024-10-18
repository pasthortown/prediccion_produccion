import requests

def descifrar(original, clave):
    descifrado = ''
    for char in original:
        ASCII_cifrado = ord(char)
        ASCII_cifrado = ASCII_cifrado - clave % 255
        descifrado += chr(ASCII_cifrado)
    return descifrado

def get_maxpoint_credentials():
    reintentar = True
    while(reintentar):
        try:
            url = "http://credenciales:8090/credencial"
            response = requests.get(url)
            response.raise_for_status()
            credenciales = response.json()
            server = credenciales.get("servidor")
            database = credenciales.get("base")
            username = credenciales.get("usuario")
            encrypted_password = credenciales.get("clave")
            clave_descifrado = 5
            password = descifrar(encrypted_password, clave_descifrado)
            reintentar = False
            return server, database, username, password
        except:
            pass

