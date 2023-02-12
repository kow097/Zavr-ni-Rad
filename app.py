from flask import Flask, render_template, request, redirect, url_for, session
#from wtforms import Form, StringField, PasswordField, validators
from flask_mysqldb import MySQL
#import bcrypt
import MySQLdb.cursors
import re
#from datetime import datetime 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder = 'templates')
app.secret_key = 'sigurnikljuc123'

# Configure the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:5vk3jhuh@localhost/calorietracker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define a model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    meals = db.relationship('Meal', backref='user', lazy=True)

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    foods = db.relationship('Food', secondary='meal_food', backref='meals', lazy=True)

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    proteins = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fats = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Float, nullable=False)

meal_food = db.Table('meal_food',
    db.Column('meal_id', db.Integer, db.ForeignKey('meal.id'), primary_key=True),
    db.Column('food_id', db.Integer, db.ForeignKey('food.id'), primary_key=True))


# Create the database tables
with app.app_context():
    db.create_all()

#MySQL config
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = '5vk3jhuh'
# app.config['MYSQL_DB'] = 'webapp'
# mysql = MySQL(app)


#test konekcije
try:
    with app.app_context():
        conn = mysql.connect
        print('USPJESNO SPOJENO NA BAZU')
except Exception as e:
    print(f'Error: {e}')


#startup route
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

        account = User.query.filter_by(username=username, password=password).first()

        if account:
            #session['loggedin'] = True
            session['id'] = account.username
            return redirect(url_for('home'))
            
        else:
            message = 'Account does not exist'
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
        password = request.form['password']

        account = User.query.filter_by(username=username).first()

        if not username or not password:
            message = 'Please fill in the form!'
        elif account:
            message = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            message = 'Username must contain only letters and numbers!'
        else:
            new_account = User(username=username, password=password)
            db.session.add(new_account)
            db.session.commit()

            return redirect(url_for('home'))
        
    elif request.method == 'POST':
        message = 'INVALID!'
    return render_template('register.html', message = message)


#home/add_meal/add_food
@app.route('/home')
def home():
    if 'id' in session:
        user = session['id']
        return render_template('home.html', user = user)
    else:
        return render_template('login.html')



@app.route('/add_food_for_meal')
def add_food_for_meal():
    if 'id' in session:
        user = session['id']

        #lista hrane u select-u
        food_name_list = Food.query.with_entities(Food.name).all()
        #food_name_list = [food[0] for food in food_name_list]

        return render_template('add_food_for_meal.html', user = user, food_name_list = food_name_list)
    else:
        return render_template('login.html')

@app.route('/add_food')
def add_food():
    if 'id' in session:
        user = session['id']

        food_list = Food.query.all()

        return render_template('add_food.html', user = user, food_list = food_list)
    else:
        return render_template('login.html')

@app.route('/add_new_food', methods=['GET','POST'])
def add_new_food():
    if request.method == 'POST':
        food_name = request.form['food_name']
        proteins = float(request.form['proteins'])
        carbs = float(request.form['carbs'])
        fats = float(request.form['fats'])

        calories = proteins*4 + carbs*4 + fats*9
        
        food = Food(name=food_name, proteins=proteins, carbs=carbs, fats=fats, calories=calories)
        db.session.add(food)
        db.session.commit()

    return redirect(url_for('add_food'))

@app.route('/delete_food/<food_id>')
def delete_food(food_id):
    food = Food.query.get(food_id)
    db.session.delete(food)
    db.session.commit()
    return redirect(url_for('add_food'))



if __name__ == '__main__':
    app.run(debug=True)



#dodati message = message u redner template: ('xy.html', message = message)
#https://www.geeksforgeeks.org/login-and-registration-project-using-flask-and-mysql/