# Crear una conexion
import mysql.connector
from mysql.connector import Error
from cryptography.fernet import Fernet  # Cifrado
from datetime import datetime, timedelta


def crear_conexion():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',  # Cambia esto por tu usuario de MySQL
            password='',  # Cambia esto por tu clave de MySQL
            database='libreria'
        )
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None


# Codigo propio
# Crear base de datos
def crear_base_datos(usuario, clave):
    try:
        # Conexión al servidor MySQL
        conexion = mysql.connector.connect(
            host='localhost',  # Cambia esto si tu servidor MySQL no está en localhost (no deberia pero por si acaso).
            user=usuario,
            password=clave  # Reemplaza con tu contraseña de MySQL
        )

        cursor = conexion.cursor()

        sql = 'CREATE DATABASE IF NOT EXISTS libreria'

        cursor.execute(sql)

        conexion.close()
        cursor.close()

    except Error as e:
        print(f"Error al conectar o crear la base de datos: {e}")


# Cifrado y descifrado
# Clave: b'xkD4i1kU9DIA3eIXSWZYR8Cgg-I3iHb63RhKRN7_eeI='  El que toque esto lo matamos a co;azo'

def cifrado(texto):
    clave_cifrado = b'xkD4i1kU9DIA3eIXSWZYR8Cgg-I3iHb63RhKRN7_eeI='  # Esto debe permanecer inmutable, no cambiar.
    texto = str(texto)
    cifrador = Fernet(clave_cifrado)
    texto_cifrado = cifrador.encrypt(texto.encode())
    return texto_cifrado  # El contenido se retorna en bits

def descifrado(texto):
    clave_cifrado = b'xkD4i1kU9DIA3eIXSWZYR8Cgg-I3iHb63RhKRN7_eeI='  # Esto debe permanecer inmutable, no cambiar.
    cifrador = Fernet(clave_cifrado)
    texto_descifrado = cifrador.decrypt(texto)
    return texto_descifrado.decode()


# Crear ID
def obtener_id(tabla):
    conexion = crear_conexion()

    if tabla == 'bookshelf':
        columna = 'id_libro'
    else:
        columna = 'id_usuario'

    if conexion:
        cursor = conexion.cursor()
        sql = f"""
        SELECT COUNT({columna}) AS total_elementos FROM {tabla}
        """

        cursor.execute(sql)
        resultado = cursor.fetchone()[0]

        if resultado is None:
            resultado = 1

        id = hex(resultado + 1)[2:]

        sql = f"""
            SELECT {columna} from {tabla}
        """

        cursor.execute(sql)
        ids = cursor.fetchone()[0]
        while True:
            if not id in ids:
                return id
            else:
                id = str(int(id) + 1)


# Codigo de pruebas Paolo
def crear_estante():
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        sql = """
        CREATE TABLE IF NOT EXISTS bookshelf (
            id_libro VARCHAR(50),
            titulo VARCHAR(100),
            editorial VARCHAR(100),
            edicion VARCHAR(100),
            editor VARCHAR(100),
            autor VARCHAR(100),
            idioma VARCHAR(50),
            fecha_de_publicacion VARCHAR(10),
            categoria VARCHAR(50),
            genero VARCHAR(50),
            disponibilidad VARCHAR(50),
            enlace BLOB,
            PRIMARY KEY (id_libro)
        )"""
        cursor.execute(sql)
        conexion.commit()
        conexion.close()


def registrar_libro(titulo, editorial, edicion, editor, autor, idioma, fecha_de_publicacion, categoria, genero,
                  disponibilidad, enlace):
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        sql = f"""
        INSERT INTO bookshelf 
        (id_libro, titulo, editorial, edicion, editor, autor, idioma, fecha_de_publicacion, categoria, genero, disponibilidad, enlace) 
        VALUES ('{obtener_id('bookshelf')}','{titulo}', '{editorial}', '{edicion}', '{editor}', '{autor}', '{idioma}', '{fecha_de_publicacion}', '{categoria}', '{genero}', '{disponibilidad}', %s)
        """
        enlace_cifrado = cifrado(enlace)
        cursor.execute(sql, (enlace_cifrado,))
        conexion.commit()
        conexion.close()


def revisar_libro(id_libro):
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        sql = f"SELECT * FROM bookshelf WHERE id_libro = '{id_libro}'"
        cursor.execute(sql)
        resultado = cursor.fetchone()
        return resultado is not None


def elimina_libro(id_libro):
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        sql = f"DELETE FROM bookshelf WHERE id_libro = '{id_libro}'"
        cursor.execute(sql)
        conexion.commit()


def alterar_libro(columna, nuevo_valor, valor_actual):
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        sql = f"UPDATE bookshelf SET {columna} = '{nuevo_valor}' WHERE {columna} = '{valor_actual}'"
        cursor.execute(sql)
        conexion.commit()


# Codigo de pruebas Luis
def registrar_suscripcion(usuario, clave, rango, fecha_nacimiento, correo, sexo):
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()

        # Calcular la fecha final
        fecha_final = datetime.now() + timedelta(days=30)
        fecha_final = fecha_final.strftime('%d/%m/%Y')

        # Cifrar el dato de clave
        clave_cifrada = cifrado(clave)  # Genera el dato en formato binario

        # Construir la consulta SQL con clave cifrada como parámetro
        sql = f"""
        INSERT INTO suscripciones (id_usuario, usuario, clave, rango, fecha_final, fecha_nacimiento, correo, sexo) 
        VALUES ('{obtener_id('suscripciones')}', '{usuario}', %s, '{rango}', '{fecha_final}', '{fecha_nacimiento}', '{correo}', '{sexo}')
        """

        # Ejecutar la consulta con clave cifrada como parámetro
        cursor.execute(sql, (clave_cifrada,))

        # Confirmar los cambios en la base de datos
        conexion.commit()

        # Cerrar cursor y conexión
        cursor.close()
        conexion.close()



def crear_tabla_usuarios():
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()

        # Crear la tabla si no existe
        sql = """
        CREATE TABLE IF NOT EXISTS suscripciones (
            id_usuario VARCHAR(50) NOT NULL,
            usuario VARCHAR(50),
            clave BLOB NOT NULL,
            rango VARCHAR(1) NOT NULL,
            fecha_final VARCHAR(10) NOT NULL,
            fecha_nacimiento VARCHAR(10) NOT NULL,
            correo VARCHAR(255),
            sexo VARCHAR(1),
            PRIMARY KEY (id_usuario)
        )
        """

        # Ejecutar la consulta
        cursor.execute(sql)
        conexion.commit()
        cursor.close()
        conexion.close()


def verificar_usuario(usuario):
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        sql = f"""
        SELECT usuario, clave FROM suscripciones WHERE usuario = '{usuario}'
        """

        cursor.execute(sql)
        resultado = cursor.fetchone()

        if resultado is not None:
            return resultado[0], descifrado(resultado[1]), True # Usuario, clave, verificador de que existe
        else:
            return 'None', 'None', False # Resultado en caso de que el usuario no exista


# Crear base de datos
crear_base_datos('root', '')

# Crear tablas
crear_estante()
crear_tabla_usuarios()