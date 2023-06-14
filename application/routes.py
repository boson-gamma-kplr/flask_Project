import sys
sys.path.extend([".","./application"])

import flask
from flask import Flask, request,redirect, url_for,jsonify
import flask_login
from flask_login import LoginManager, login_required
from django.utils.http import url_has_allowed_host_and_scheme

import wtforms.form 
from models import User, IncomeExpenses, session
import json

login_manager = LoginManager()

app = Flask(__name__)
login_manager.init_app(app)

app.secret_key = 'this is my secret key'

# Our mock database.
users = {'foo@bar.tld': {'pw': 'secret'}}


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['pw'] == users[email]['pw']

    return user


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

@app.route('/', methods=['GET', 'POST'])
def index():
    if flask_login.current_user.is_anonymous:
        return flask.redirect(url_for('login'))
    else:
        if flask.request.method =='POST':
            if "add" in flask.request.form:
                return flask.redirect(url_for('add'))
            elif "logout" in flask.request.form:
                return flask.redirect(url_for('logout'))
        
        response = session.query(IncomeExpenses).order_by(IncomeExpenses.date.desc()).all()
        return flask.render_template('index.html', username = "", incomeExpenses=response)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        email = flask.request.form['email']
        password = flask.request.form['password']
        allUsers = session.query(User).all()
        for user in allUsers:
            if email == user.email and password == user.password:
                flask_login.login_user(user,remember = True)
                return flask.redirect(flask.url_for('index'))
        return 'Bad login'
    
    return flask.render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if flask.request.method == 'POST':
        session.add(User(id=request.form["email"],email=request.form["email"],username=request.form["username"], password=request.form["password"]))
        session.commit()
        return flask.redirect(url_for('index'))

    return flask.render_template('signup.html')


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return '''<a href="/">Index</a>
    <br>
    <p>Logged out</p>'''

@app.route('/add', methods=['GET', 'POST'])
@flask_login.login_required
def add():
    if flask.request.method == 'POST':   
        session.add(IncomeExpenses(id=request.form["id"] ,type=request.form["type"], date=request.form["date"]))
        session.commit()

    return flask.render_template('add.html')