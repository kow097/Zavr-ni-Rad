from flask import Flask, render_template, request, redirect, url_for, session
#from wtforms import Form, StringField, PasswordField, validators
from flask_mysqldb import MySQL
#import bcrypt
import MySQLdb.cursors
import re
#from datetime import datetime 

app = Flask(__name__, template_folder = 'templates')
app.secret_key = 'sigurnikljuc123'


#MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '5vk3jhuh'
app.config['MYSQL_DB'] = 'webapp'
mysql = MySQL(app)


#test konekcije
try:
    with app.app_context():
        conn = mysql.connect
        print('USPJESNO SPOJENO NA BAZU')
except Exception as e:
    print(f'Error: {e}')


#startup ruta
@app.route('/')
def start():
    return render_template('login.html')

##############   APP RUTE   ##############
#login/register/logout
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE (username, password) = (%s, %s)', (username, password,))
        account = cursor.fetchone()

        if account:
            #session['loggedin'] = True
            session['id'] = account['username']
            return redirect(url_for('home'))
            
        else:
            message = 'Račun ne postoji'
            return render_template('login.html', message = message)
    else:
        if 'id' in session:
            return redirect(url_for('home'))
        #return redirect(url_for('login'))
        return render_template('login.html')

@app.route('/logout')
def logout():
    #session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username',None)
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        #hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username, ))
        account = cursor.fetchone()

        if not username or not password:
            message = 'Molimo popunite formu!'
        elif account:
            message = 'Račun već postoji!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            message = 'Korisničko ime mora sadržavati samo slova i brojeve!'
        else:
            cursor.execute ("INSERT INTO users (username,password) VALUES (%s,%s)",(username,password))
            mysql.connection.commit()

            #return render_template('home.html', user = user)
            return redirect(url_for('home'))
        
    elif request.method == 'POST':
        message = 'NEVALJA!'
    return render_template('register.html', message = message)

#home/add_meal/add_food
@app.route('/home')
def home():
    if 'id' in session:
        user = session['id']
        return render_template('home.html', user = user)
    else:
        return render_template('login.html')

@app.route('/add_meal')
def add_meal():
    if 'id' in session:
        user = session['id']

        #lista hrane u select-u
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT food_name FROM food')
        food_name_list = cursor.fetchall()

        return render_template('add_meal.html', user = user, food_name_list = food_name_list)
    else:
        return render_template('login.html')

@app.route('/add_food')
def add_food():
    if 'id' in session:
        user = session['id']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM food')
        food_list = cursor.fetchall()

        return render_template('add_food.html', user = user, food_list = food_list)
    else:
        return render_template('login.html')

@app.route('/add_new_food', methods=['GET','POST'])
def add_new_food():
    if request.method == 'POST':
        food_name = request.form['food_name']
        proteins = int(request.form['proteins'])
        carbs = int(request.form['carbs'])
        fats = int(request.form['fats'])

        calories = proteins*4 + carbs*4 + fats*9
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute ("INSERT INTO food (food_name,proteins,carbs,fats,calories) VALUES (%s,%s,%s,%s,%s)",(food_name,proteins,carbs,fats,calories))
        mysql.connection.commit()

    return redirect(url_for('add_food'))

@app.route('/delete_food/<food_id>')
def delete_food(food_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute ("DELETE FROM food WHERE id = {}".format(food_id))
    mysql.connection.commit()
    return redirect(url_for('add_food'))


if __name__ == '__main__':
    app.run(debug=True)


#dodati message = message u redner template: ('xy.html', message = message)
#https://www.geeksforgeeks.org/login-and-registration-project-using-flask-and-mysql/