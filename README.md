# ISIS3311_Lab2_Cifrado

En este repositorio se encuentra el archivo [cifrado.py](cifrado.py) que contiene una aplicación basada en CLI que guarda archivos cifrados en el servidor FTP del caso de laboratorio y permite descargarlos descifrándolos. A continuación se explica el funcionamiento y generalidades de la aplicación.
## ¿Cómo usar la aplicación?
La aplicación usa CLI interface para su ejecución, al correr el archivo de python usando `python cifrado.py` la aplicación solicitará inicialmente las credenciales del servidor FTP alojado en la IP **192.201.10.21** con el puerto 21 abierto para el intercambio de datos FTP. Después de ingresar las credenciales la aplicación preguntará si se desea cargar un archivo (U) o descargarlo (D).
### Cargar un archivo
Para cargar un archivo la aplicación preguntará la ruta al archivo a subir junto con una contraseña para el cifrado, para posteriormente cifrar el archivo y subirlo al servidor, si este proceso fue exitoso recibirá un mensaje de éxito en la consola, de otra forma se detendrá la ejecución.
### Descargar un archivo
Para la descarga de un archivo la aplicación solicitará el nombre del archivo a descargar, una ruta para guardar localmente el archivo descifrado y la contraseña con la que fue cifrada el archivo. Si el proceso fue exitoso se obtendrá un mensaje de éxito en consola.
## Funcionamiento general de la aplicación
El código de la aplicación contiene 5 funciones generales para el funcionamiento de la aplicación, las cuales se describen a continuación:
### `derive_key`
Esta función recibe una contraseña por parámetro y opcionalmente una *sal* y genera un clave hash usando la función `PBKDF2HMAC` de la librería `cryptography`, esta función retorna la clave de la contraseña junto con la *sal* usada para generarla.
### `encrypt`
Esta función recibe un string de texto plano y una contraseña para cifrar el texto. Inicialmente genera la clave a partir de la contraseña usando la función `derive_key` además genera bits random de *iv*, posteriormente instancia un objeto `AESGCM` de la librería `cryptography` usando la clave generada. Con este objeto y el *iv* encripta el texto plano, para finalmente retornar la sal, el iv y el texto cifrado en orden.
### `decrypt`
Esta función recibe un texto cifrado y una contraseña como parámetro para decifrar, inicialmente convierte el texto cifrado a base 64 para descifrarlo, obtiene la sal y el iv desde el texto y usando estos datos junto con la contraseña usa la función `derive_key` con la sal extraida. Finalmente instancia un objeto `AESCGM` para desencriptar el texto usando la clave generada, si esta clave no es correcta se lanza una excepción. La función retorna el texto descifrado.
### `encrypt_file`
Esta función recibe una ruta de un archivo, además de credenciales ftp, inicialmente lee el archivo de la ruta como texto plano, solicita una contraseña para cifrar al usuario y utliza la función `encrypt` para cifrar el archivo. Posteriormente agrega el tecto cifrado a un archivo con extensión `.aes`, abre una conexión FTP y sube el archivo cifrado. Retorna `True` si el proceso fue exitoso, lanza una excepción de lo contrario.
### `decrypt_file`
Este archivo recibe el nombre de un archivo, unas credenciales del servidor FTP y una ruta de salida. Inicialmente abre una conexión FTP con el servidor y descarga el archivo solicitado aún cifrado en un archivo temporal. Posteriormente lee el archivo cifrado, solicita la contraseña de cifrado al usuario y descifra el archivo usando la función `decrypt`, finalmente escribe el texto descifrado en la ruta de salida y elimina el archivo temporal. Retorna `True` si el proceso fue exitoso, lanza una excepción de lo contrario.
### `main`
Esta función maneja la interacción con el usuario, solicita las credenciales FTP, si se desea carga o descarga de archivos, las rutas de estos y ejecuta las funciones dependiendo del proceso.