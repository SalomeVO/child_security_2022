"""
Controller para la aplicacion CHILD SECURITY
Plataforma online - hibrida y escalable a otros dispositivos
"""

from flask import Flask, render_template, request, redirect, url_for, session
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from datetime import date
import re

#Iniializamos la app
app = Flask(__name__)

#Configuramos la llave secreta de seguridad
app.secret_key = 'child_sec'

#Conexion a la bd
app.config['MYSQL_DATABASE_HOST'] = 'childsecurity.mysql.pythonanywhere-services.com'
app.config['MYSQL_DATABASE_USER'] = 'childsecurity'
app.config['MYSQL_DATABASE_PASSWORD'] = 'enero2022'
app.config['MYSQL_DATABASE_DB'] = 'childsecurity$child_sec_db'

#Creamos un cursor para recorrer la bd
mysql = MySQL(app, cursorclass=DictCursor)

#Manejador del error 404 not found en flask
@app.errorhandler(404)
def not_found(e):
    data = {
        'titulo' : 'ChildSecurity'
    }
    return render_template('404.html', data=data), 404

#Vista de la pagina de inicio, login o register
@app.route('/', methods=['GET', 'POST'])
def login():
    data = {
        'titulo': 'Child Security - Inicia Sesion'
    }
    #Mensaje que se mostrara si obtenemos algun error
    msg = ''
    #Guardamos el request en una variable para posteriormento consultarlo
    req = request.form
    #Revisamos si el user y pass existen en la consulta post generada
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        #Almacenamos en variables para poder acceder mas facil
        username = req.get("email")
        password = req.get("password")
        #Revisamos si los datos de la cuenta existen en nuestra bd
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (username, password))
        #Fetch para asociar todo en un solo registro y lo guardamos
        account = cursor.fetchone()
        #Si la cuenta existe en la tabla de nuestra bd
        if account:
            #Creamos datos de session
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['name'] = account['name']
            session['surname'] = account['surname']
            session['email'] = account['email']
            session['f_reg'] = account['fecha_reg']
            session['profile_pic'] = account['profile_pic']
            #Formateamos el mensaje de error
            msg = ""
            #Redireccionamos a la pagina principal
            return redirect('/dashboard')
        else:
            #Si el usuario/password son incorrectos
            msg = 'Los datos ingresados son incorrectos'
    return render_template('login.html' , data=data, msg=msg)

#Vista de registro de usuarios nuevos
@app.route('/registrar', methods=['GET', 'POST'])
def register():
    data = {
        'titulo' : 'Child Security - Registrate'
    }
    #Mensaje a mostrar por cualquier error
    msg = ''
    #Almacenamos la fecha de este instante
    today = date.today()
    f_reg = today.strftime("%Y/%m/%d")
    foto = 'https://i.ibb.co/Y04Ky6V/Child-Security.png'
    conn = mysql.connect()

    #Guardamos la peticion (request)
    req = request.form
    #Corroboramos el user y password
    if request.method == 'POST' and 'name' in request.form and 'surname' in request.form and 'username' in request.form and 'email' in request.form and 'password' in request.form:
        #Guardamos las variables para tener mejor acceso
        params = {
            'nombre' : req.get("name"),
            'apellido' : req.get("surname"),
            'username' : req.get("username"),
            'email' : req.get("email"),
            'password' : req.get("password"),
            'f_reg' : f_reg,
            'foto_perfil' : foto
        }
        #Revisamos si los datos de la cuenta existen en la base de datos
        cursor = conn.cursor()
        query = 'INSERT into users (username, name, surname, email, fecha_reg, profile_pic, password) values(%(username)s, %(nombre)s, %(apellido)s, %(email)s, %(f_reg)s, %(foto_perfil)s, %(password)s)'
        #Ejecutamos la sentencia
        cursor.execute(query, params)
        #Ejecutamos un commit (para que se ejecute la query)
        conn.commit()
        #Redirigimod al dashboard principal con el usuario loggeado
        #Creamos datos de session
        session['loggedin'] = True
        session['username'] = params['username']
        session['name'] = params['nombre']
        session['surname'] = params['apellido']
        session['email'] = params['email']
        session['f_reg'] = params['f_reg']
        session['profile_pic'] = params['foto_perfil']
        return redirect('/dashboard')
    else:
        #Si el usuario/contrasenia son incorrectos
        msg = 'Uno de los datos ingresados no es correcto...'
    #Renderizamos el form de registrar con la variable mensaje (si hubiese)
    return render_template('register.html', data=data, msg=msg)

#Validamos en la vista principal de la app para protegerla de usuarios no autenticados
@app.route('/dashboard')
def index():
    data = {
        'titulo' : 'Child Security'
    }
    #Si la variable de session loggedin existe en session
    if 'loggedin' in session:
        #El usuario tiene session activa, renderizamos el dashboard
        return render_template('dashboard.html', data=data, username=session['username'], profilepic=session['profile_pic'], nombre=session['name'], apellido=session['surname'])
    return redirect(url_for('/'))
#Validamos en la vista principal de la app para protegerla de usuarios no autenticados
@app.route('/dashboard-wearables')
def wearables():
    data = {
        'titulo' : 'Child Security'
    }
    #Si la variable de session loggedin existe en session
    if 'loggedin' in session:
        #El usuario tiene session activa, renderizamos el dashboard
        #Revisamos si los datos de la cuenta existen en nuestra bd
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT registered_wearables.id, registered_wearables.wearable_activation_code, registered_wearables.active_status, users.name, users.surname FROM registered_wearables INNER JOIN users ON registered_wearables.user_id = users.id WHERE registered_wearables.user_id = %s' , (session['id']))
        #Fetch para asociar todo en un solo registro y lo guardamos
        account = cursor.fetchall()
        return render_template('wearables.html', data=data, info=account, username=session['username'], profilepic=session['profile_pic'], nombre=session['name'], apellido=session['surname'])
    return redirect(url_for('/'))



#Ruta para poder llevar a cabo el logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
