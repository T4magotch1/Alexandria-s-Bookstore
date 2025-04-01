from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
from cryptography.fernet import Fernet  # Cifrado
from datetime import datetime, timedelta


# Base de datos
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


def crear_tabla_compras():
    conexion = crear_conexion()
    if conexion:

        cursor = conexion.cursor()
        sql = """
        CREATE TABLE IF NOT EXISTS compras (
            id_compra INT AUTO_INCREMENT PRIMARY KEY,
            id_usuario INT NOT NULL,
            id_libro INT NOT NULL,
            fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
            FOREIGN KEY (id_libro) REFERENCES libros(id_libro)
        );
        """
        cursor.execute(sql)
        conexion.commit()
        conexion.close()


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


def obtener_id(tabla):
    conexion = crear_conexion()  # Asume que esta función está definida previamente

    if conexion:

        # Validar tabla y columna
        if tabla == 'bookshelf':
            columna = 'id_libro'
        elif tabla == 'suscripciones':
            columna = 'id_usuario'

        try:
            cursor = conexion.cursor()

            # Obtener el número total de elementos
            sql = f"SELECT COUNT({columna}) AS total_elementos FROM {tabla}"
            cursor.execute(sql)
            resultado = cursor.fetchone()[0] or 0  # Si es None, asignar 0

            # Generar un nuevo ID en hexadecimal
            nuevo_id = hex(resultado + 1)[2:]

            # Obtener todos los IDs existentes
            sql = f"SELECT {columna} FROM {tabla}"
            cursor.execute(sql)
            ids = [fila[0] for fila in cursor.fetchall()]  # Obtener todos los IDs en una lista

            # Garantizar que el nuevo ID sea único
            while nuevo_id in ids:
                nuevo_id = hex(int(nuevo_id, 16) + 1)[2:]  # Incrementar el ID hexadecimal

            conexion.close()

            return nuevo_id

        except Exception as e:
            print(f"Error al obtener ID: {e}")


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


def registrar_suscripcion(usuario, nombre, apellido, clave, rango, fecha_nacimiento, correo):
    try:
        # Crear la conexión con la base de datos
        conexion = crear_conexion()  # Se asume que esta función está correctamente definida
        if not conexion:
            raise Exception("No se pudo establecer la conexión con la base de datos.")

        cursor = conexion.cursor()

        # Calcular la fecha final (30 días desde hoy)
        fecha_final = (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')

        # Cifrar la clave
        clave_cifrada = cifrado(clave)  # Se asume que esta función devuelve una clave cifrada segura

        # Validar el formato de la fecha de nacimiento
        try:
            fecha_nacimiento_obj = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
            fecha_nacimiento = fecha_nacimiento_obj.strftime('%d/%m/%Y')  # Convertir al formato de la base de datos
        except ValueError:
            raise ValueError("El formato de la fecha de nacimiento debe ser DD/MM/YYYY.")

        # Obtener un ID único para el usuario
        id_usuario = obtener_id('suscripciones')  # Se asume que esta función está definida correctamente

        # Construir la consulta parametrizada para evitar inyección SQL
        sql = """
        INSERT INTO suscripciones (
            id_usuario, usuario, nombre, apellido, clave, rango, fecha_final, fecha_nacimiento, correo
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (id_usuario, usuario, nombre, apellido, clave_cifrada, rango, fecha_final, fecha_nacimiento, correo)

        # Ejecutar la consulta
        cursor.execute(sql, valores)

        # Confirmar los cambios
        conexion.commit()
        print("Suscripción registrada correctamente.")

    except Exception as e:
        # Imprimir el error y revertir cambios en caso de excepción
        if 'conexion' in locals():
            conexion.rollback()
        print(f"Error al registrar la suscripción: {e}")
        raise

    finally:
        # Asegurarse de cerrar el cursor y la conexión
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
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
            nombre VARCHAR(20),
            apellido VARCHAR(20),
            clave BLOB NOT NULL,
            rango VARCHAR(1) NOT NULL,
            fecha_final VARCHAR(10) NOT NULL,
            fecha_nacimiento VARCHAR(10) NOT NULL,
            correo VARCHAR(255),
            PRIMARY KEY (id_usuario)
        )
        """

        # Ejecutar la consulta
        cursor.execute(sql)
        conexion.commit()
        cursor.close()
        conexion.close()


def verificar_usuario(usuario):
    # Crear la conexión con la base de datos
    conexion = crear_conexion()  # Asume que esta función está definida correctamente

    try:
        cursor = conexion.cursor()

        # Consulta parametrizada para evitar inyección SQL
        sql = """
        SELECT usuario, clave 
        FROM suscripciones 
        WHERE usuario = %s
        """

        # Ejecutar la consulta con el nombre de usuario como parámetro
        cursor.execute(sql, (usuario,))
        resultado = cursor.fetchone()

        if resultado is not None:
            usuario_encontrado = resultado[0]
            clave_descifrada = descifrado(resultado[1])  # Se asume que esta función está definida correctamente
            return usuario_encontrado, clave_descifrada  # Usuario encontrado, clave descifrada
        else:
            return None, None

    except Exception as e:
        print(f"Error al verificar el usuario: {e}")


def verificar_correo(correo):
    # Crear la conexión con la base de datos
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()

            # Consulta parametrizada para evitar inyección SQL
            sql = """
            SELECT usuario, clave 
            FROM suscripciones 
            WHERE correo = %s
            """

            # Ejecutar la consulta con el correo como parámetro
            cursor.execute(sql, (correo,))
            resultado = cursor.fetchone()

            if resultado is not None:
                usuario = resultado[0]
                clave_descifrada = descifrado(resultado[1])  # Asume que 'descifrado' está definido correctamente

                conexion.close()

                return usuario, clave_descifrada  # Retornar usuario y clave descifrada
            else:
                return None, None  # Caso en que el correo no exista

        except Exception as e:
            print(f"Error al verificar el correo: {e}")


# Frontend
app = Flask(__name__)
user_data = {'email': None, 'password': None}


@app.route('/')
def home():
    # Redirige automáticamente al formulario de login
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global user_data  # Usar la variable global
    if request.method == 'POST':
        # Redirigir a la página de inicio tras procesar el login
        return redirect(url_for('pagina_inicio'))
    return render_template('login.html')



@app.route('/procesar_login', methods=['POST'])
def procesar_login():
    global user_data  # Usar la variable global
    usuario = False
    clave = False
    # Guardar los datos del formulario en la variable global
    user_data['email'] = request.form['email']
    user_data['password'] = request.form['pswd']
    usuario, clave = verificar_correo(user_data['email'])
    if clave == user_data['password']:
        return redirect(url_for('pagina_inicio'))
    else:
        return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            # Obtener los datos del formulario
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            username = request.form.get('username')
            birthdate = request.form.get('birthdate')
            email = request.form.get('email')
            password = request.form.get('pswd')
            confirm_password = request.form.get('confirm_pswd')

            # Validación de campos vacíos
            if not all([firstname, lastname, username, birthdate, email, password, confirm_password]):
                print('Faltaron datos.')
                return render_template('signup.html')

            # Validación de contraseña (deben coincidir)
            if password != confirm_password:
                print('Las claves no coinciden.')
                return render_template('signup.html')

            # Validación básica: revisa si el nombre de usuario o correo ya están registrados
            usuario, clave = verificar_usuario(username)
            usuario1, clave1 = verificar_correo(email)

            if usuario is not None or usuario1 is not None:
                print('Ya existe el usuario.')
                return render_template('signup.html')

            print(f'La fecha es: {birthdate}')
            registrar_suscripcion(username, firstname, lastname, password, '0', birthdate, email)
            return redirect(url_for('home'))  # Redirigir al login después del registro

        except Exception as e:
            return render_template('signup.html')

    # Renderizar la página de registro (GET)
    return render_template('signup.html')



@app.route('/pagina_inicio')
def pagina_inicio():
    return render_template('pagina_inicio.html')


@app.route('/carrito_de_compra')
def carrito_de_compra():
    return render_template('carrito_de_compra.html')


@app.route('/otra_pagina')
def otra_pagina():
    return render_template('otra_pagina.html')


@app.route('/pagina_academicos')
def pagina_academicos():
    return render_template('pagina_academicos.html')


@app.route('/pagina_manuales')
def pagina_manuales():
    return render_template('pagina_manuales.html')


@app.route('/pagina_novela')
def pagina_novela():
    return render_template('pagina_novela.html')


@app.route('/pagina_partituras')
def pagina_partituras():
    return render_template('pagina_partituras.html')


@app.route('/pagina_atlas')
def pagina_atlas():
    return render_template('pagina_atlas.html')


@app.route('/pagina_todo')
def pagina_todo():
    return render_template('pagina_todo.html')


if __name__ == '__main__':
    crear_base_datos('root', '')
    crear_estante()
    crear_tabla_usuarios()
    crear_tabla_compras()
    app.run(debug=True)
