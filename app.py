from flask import Flask, render_template, request, redirect, url_for, session
#from wtforms import Form, StringField, PasswordField, validators
from flask_mysqldb import MySQL
#import bcrypt
import MySQLdb.cursors
import re
#from datetime import datetime 
from flask_sqlalchemy import SQLAlchemy

#from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__, template_folder = 'templates')
app.secret_key = 'sigurnikljuc123'

#app.debug = True
#toolbar = DebugToolbarExtension(app)

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

    def __repr__(self):
        return f"Meal('{self.date}')"

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    proteins = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fats = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Food('{self.name}')"

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
#try:
#    with app.app_context():
#        conn = mysql.connect
#        print('USPJESNO SPOJENO NA BAZU')
#except Exception as e:
#    print(f'Error: {e}')


#startup route
@app.route('/')
def start():
    return render_template('login.html')

##############   APP RUTE   ##############
#login/register/logout
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST' and ('username' not in request.form or 'password' not in request.form):
        message = 'Popunite formu'
        return render_template('login.html', message=message)

    elif request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        account = User.query.filter_by(username=username, password=password).first()

        if account:
            #session['loggedin'] = True
            session['username'] = account.username
            return redirect(url_for('home'))

        else:
            message = 'Račun već postoji!'
            return render_template('login.html')
    else:
        if 'username' in session:
            return redirect(url_for('home'))
        #return redirect(url_for('login'))
        return render_template('login.html')

@app.route('/logout')
def logout():
    #session.pop('loggedin', None)
    #session.pop('id', None)
    session.pop('username')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        account = User.query.filter_by(username=username).first()

        if not username or not password:
            message = 'Popunite formu!'
        elif account:
            message = 'Račun već postoji!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            message = 'Korisničko ime mora sdržavati samo slova i brojeve!'
        else:
            new_account = User(username=username, password=password)
            db.session.add(new_account)
            db.session.commit()

            return redirect(url_for('home'))
        
    return render_template('register.html', message = message)


#home/add_meal/add_food
@app.route('/home')
def home():
    message = ''
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=session['username']).first()
        #meals = Meal.query.filter_by(user_id=user.id).all()

        meals = Meal.query.filter_by(user_id=user.id).order_by(Meal.date.desc()).all()

        meal_sums = []

        for meal in meals:
            proteins = 0
            carbs = 0
            fats = 0
            calories = 0

            for food in meal.foods:
                proteins += food.proteins
                carbs = food.carbs
                fats += food.fats
                calories += food.calories

            meal_sums.append({
                'meal_sums' : meal,
                'proteins' : proteins,
                'carbs' : carbs,
                'fats' : fats,
                'calories' : calories
            })
        if 'message' in session:
            message = session['message']
            session.pop('message', None)
        return render_template('home.html', user=username, meal_sums=meal_sums, message = message)
    else:
        return render_template('login.html')

@app.route('/meals/<int:meal_id>', methods=['POST'])
def delete_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    db.session.delete(meal)
    db.session.commit()
    print('uspjesno obrisan meal')
    return redirect(url_for('home'))

@app.route('/preview_meal/<int:meal_id>', methods=['POST'])
def preview_meal(meal_id):
    if 'username' in session:
        username = session['username']
        meal = Meal.query.get_or_404(meal_id)
        date = Meal.query.filter_by(id=meal_id).first().date
        food_in_meal = meal.foods
        total_calories = sum([food.calories for food in food_in_meal])
        food_name_list = Food.query.with_entities(Food.name).all()

        return render_template('preview_meal.html', user = username, food_in_meal = food_in_meal, date = date, total_calories = total_calories, food_name_list=food_name_list, meal=meal)
    else:
        return render_template('login.html')

@app.route('/add_food_existing_meal/<int:meal_id>', methods=['GET', 'POST'])
def add_food_existing_meal(meal_id):
    if request.method == 'POST':
        food_name = request.form['food']
        food = Food.query.filter_by(name=food_name).first()
        meal = Meal.query.get_or_404(meal_id) 
        meal.foods.append(food)
        db.session.commit()
        return redirect(url_for('preview_meal', meal_id=meal_id))

@app.route('/delete_food_existing_meal/<int:meal_id>', methods=['POST'])
def delete_food_existing_meal(meal_id):
    if 'username' in session:
        meal = Meal.query.get_or_404(meal_id)
        food_id = request.form.get('food_id')
        food = Food.query.get_or_404(food_id)
        meal.foods.remove(food)
        db.session.commit()
        return redirect(url_for('preview_meal', meal_id=meal_id))
    else:
        return render_template('login.html')

@app.route('/add_new_meal', methods=['GET', 'POST'])
def add_new_meal():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if request.method == 'POST' and 'datum' in request.form:
            date = request.form['datum']
            if date:
                meal = Meal(date=date, user_id=user.id)
                db.session.add(meal)
                db.session.commit()
                return redirect(url_for('add_food_for_meal'))
            else:
                message = 'Unesite Datum!'
                session['message'] = message
                return redirect(url_for('home', message=message))
    else:
        return render_template('login.html')

@app.route('/add_food_for_meal', methods=['GET', 'POST'])
def add_food_for_meal():
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=session['username']).first()

        latest_meal = Meal.query.filter_by(user_id=user.id).order_by(Meal.id.desc()).first()
        latest_date = latest_meal.date

        #lista hrane u select-u
        food_name_list = Food.query.with_entities(Food.name).all()

        #meal = Meal.query.filter_by(date=date).first()
        #meal = Meal.query.filter_by(user_id=user.id, date=date).first()
        #meal = Meal.query.order_by(Meal.id.desc()).first()
        
        meal = Meal.query.filter_by(user_id=user.id).order_by(Meal.id.desc()).first()
        food_in_meal = meal.foods
        total_calories = sum([food.calories for food in food_in_meal])

        return render_template('add_food_for_meal.html', user = username, food_name_list = food_name_list, food_in_meal=food_in_meal, total_calories=total_calories, date=latest_date)
    else:
        return render_template('login.html')



@app.route('/add_food_in_meal', methods=['GET', 'POST'])
def add_food_in_meal():
    if request.method == 'POST':
        food_name = request.form['food']
        food = Food.query.filter_by(name=food_name).first()
        meal = Meal.query.order_by(Meal.id.desc()).first() #posljenji meal koji je dodan u bazi
        meal.foods.append(food) # dodaje hranu u meal
        db.session.commit()
        return redirect(url_for('add_food_for_meal'))
        

@app.route('/delete_food_from_meal/<food_name>/<datum>', methods=['POST'])
def delete_food_from_meal(food_name,datum):
    if 'username' in session:
        
        username = session['username']
        user = User.query.filter_by(username=username).first()
        date = request.form.get('datum', None)

        meal = Meal.query.filter_by(date=date, user_id=user.id).first()
        food = Food.query.filter_by(name=food_name).first()
        meal.foods.remove(food)
        db.session.commit()
    return redirect(url_for('add_food_for_meal'))

@app.route('/add_food')
def add_food():
    if 'username' in session:
        user = session['username']

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

#fixati css za preview
#fixati error koji se pojavi kada dodajemo novi food item u postojeći meal GET(405)
#fixati da se moze dodati vise istih food itema u isti meal

