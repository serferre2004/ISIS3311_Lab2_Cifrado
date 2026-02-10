import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from base64 import urlsafe_b64encode, urlsafe_b64decode
from ftplib import FTP

# Funciones criptográficas
def derive_key(password: str) -> bytes:
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(password.encode()), salt

def encrypt(plaintext: str, password: str) -> str:
    key, salt = derive_key(password)
    iv = os.urandom(12)
    aesgcm = AESGCM(key)

    ciphertext = aesgcm.encrypt(iv, plaintext.encode(), None)
    return urlsafe_b64encode(salt + iv + ciphertext).decode()

def decrypt(ciphertext: str, password: str) -> str:
    try:
        decoded = urlsafe_b64decode(ciphertext.encode())
        salt, iv, ct = decoded[:16], decoded[16:28], decoded[28:]
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password.encode())
        aesgcm = AESGCM(key) #Lanza excepción si la contraseña es incorrecta
        return aesgcm.decrypt(iv, ct, None).decode()
    except Exception as e:
        raise ValueError("Contraseña incorrecta o archivo corrupto") from e
    
# Funciones de FTP
def encrypt_file(input_path: str, ftp_user: str, ftp_psswd: str) -> bool:
    try: 
        with open(input_path, 'r') as f:
            plaintext = f.read()
            password = input("Ingrese la contraseña para cifrar el archivo: ")
            ciphertext = encrypt(plaintext, password)
        
        with open(input_path + '.aes', 'w') as enc_file:
            enc_file.write(ciphertext)

        ftp = FTP()
        ftp.connect("192.201.10.20", 21)
        ftp.login(ftp_user, ftp_psswd)
        with open(input_path + '.aes', 'rb') as f:
            ftp.storbinary('STOR ' + os.path.basename(input_path + '.aes'), f)
        ftp.quit()

    except Exception as e:
        print(f"Error al cifrar el archivo: {e}")
        raise e
    return True

def decrypt_file(filename: str, ftp_user: str, ftp_psswd: str, output_path: str) -> bool:
    try:
        ftp = FTP()
        ftp.connect("192.201.10.20", 21)
        ftp.login(ftp_user, ftp_psswd)
        temp_file = os.path.join(os.path.dirname(output_path), filename + '.aes')
        with open(temp_file, 'wb') as f:
            ftp.retrbinary('RETR ' + filename + '.aes', f.write)
        ftp.quit()
        with open(temp_file, 'r') as f:
            ciphertext = f.read()
        password = input("Ingrese la contraseña para descifrar el archivo: ")
        plaintext = decrypt(ciphertext, password)
        output_file = os.path.join(os.path.dirname(output_path), filename)
        with open(output_file, 'w') as f:
            f.write(plaintext)
        os.remove(temp_file)
    except Exception as e:
        print(f"Error al descifrar el archivo: {e}")
        raise e
    return True

def main():
    ftp_user = input("Ingrese el usuario FTP: ")
    ftp_psswd = input("Ingrese la contraseña FTP: ")
    while True:
        choice = input("¿Desea subir (U) o descargar (D) un archivo? (U/D): ").strip().upper()
        if choice == 'U' or choice == 'u':
            input_path = input("Ingrese la ruta del archivo a subir: ")
            if encrypt_file(input_path, ftp_user, ftp_psswd):
                print("Archivo cifrado y subido exitosamente.")
            return            
        elif choice == 'D' or choice == 'd':
            filename = input("Ingrese el nombre del archivo a descargar (sin extensión .aes): ")
            output_path = input("Ingrese la ruta donde guardar el archivo descifrado: ")
            if decrypt_file(filename, ftp_user, ftp_psswd, output_path):
                print("Archivo descargado y descifrado exitosamente.")
            return
        else:
            print("Opción no válida. Por favor, ingrese U para subir o D para descargar.")