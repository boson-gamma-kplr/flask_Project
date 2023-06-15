import sys
sys.path.extend([".","./application"])

import json
import flask
from flask import Flask, request, url_for
import flask_login
from flask_login import login_required, LoginManager
from flask_bootstrap import Bootstrap5
from datetime import datetime
from sqlalchemy import func

from models import User, IncomeExpenses, session


login_manager = LoginManager()

app = Flask(__name__)

app.config["DEBUG"]=True

bootstrap = Bootstrap5(app)

login_manager.init_app(app)

app.secret_key = 'this is my secret key'

@login_manager.user_loader
def user_loader(email):
    return session.query(User).get(email)

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    
    user = session.query(User).get(email)
    if user==None:
        return
    
    if request.form.get('password') == user.password:
        user.is_authenticated = True
        return user
        
    user.is_authenticated = False
    return

@login_manager.unauthorized_handler
def unauthorized_handler():
    return flask.redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@flask_login.login_required
def index():
    if flask.request.method =='POST':
        if "add" in flask.request.form:
            return flask.redirect(url_for('add'))
        elif "logout" in flask.request.form:
            flask_login.logout_user()
            return flask.redirect(url_for('index'))
        elif "delete" in flask.request.form:
            return flask.redirect(url_for('delete'))
        elif "profile" in flask.request.form:
            return flask.redirect(url_for('profile'))
        elif "dashboard" in flask.request.form:
            return flask.redirect(url_for('dashboard'))
    try:
        response = session.query(IncomeExpenses).order_by(IncomeExpenses.date.desc()).all()
        liste_json = [json.loads(str(e)) for e in response]
        return flask.render_template("index.html", username = flask_login.current_user.username, incomeExpenses= json.dumps(liste_json,separators=[",",":"],indent=4))
    except Exception as e:
        return flask.render_template("index.html", username = flask_login.current_user.username, incomeExpenses= e)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        try:
            email = flask.request.form['email']
            password = flask.request.form['password']
            allUsers = session.query(User).all()
            remember_me = 'remember_me' in flask.request.form
            for user in allUsers:
                if email == user.email and password == user.password:
                    flask_login.login_user(user, remember = remember_me)
                    return flask.redirect(flask.url_for('index'))
            return flask.render_template('login.html', is_logged_in="email or password incorrect")
        except Exception as e:
            return flask.render_template('login.html', is_logged_in=e)
    
    return flask.render_template('login.html',is_logged_in='')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if flask.request.method == 'POST':
        try:
            session.add(User(id=request.form["email"],email=request.form["email"],username=request.form["username"], password=request.form["password"]))
            session.commit()
            return flask.redirect(url_for('index'))
        except Exception as e:
            session.rollback()
            return flask.render_template('signup.html',warning_text=e)

    return flask.render_template('signup.html',warning_text="")


@app.route('/add', methods=['GET', 'POST'])
@flask_login.login_required
def add():
    if flask.request.method == 'POST':   
        session.add(IncomeExpenses(id=None ,type=request.form["type"], date=request.form["date"],category=request.form["category"],amount=request.form["amount"]))
        session.commit()

    return flask.render_template('add.html',date_of_today=str(datetime.now()))

@app.route('/delete', methods=['GET', 'POST'])
@flask_login.login_required
def delete():
    if flask.request.method == 'POST':
        session.delete(session.query(IncomeExpenses).get(flask.request.form["id"]))
        session.commit()

    return flask.render_template('delete.html')

@app.route('/profile')
@flask_login.login_required
def profile():
    profile = json.dumps(json.loads(str(flask_login.current_user)),separators=[",",":"],indent=4)
    return flask.render_template('profile.html',user_profile=profile)

@app.route('/dashboard')
@login_required
def dashboard():
    session.rollback()

    # Requête de comparaison de revenus et dépenses
    income_vs_expense = session.query(
        IncomeExpenses.type,
        func.sum(IncomeExpenses.amount)
    ).group_by(IncomeExpenses.type).all()

    # Requête de comparaison de catégories
    category_comparison = session.query(
        IncomeExpenses.category,
        IncomeExpenses.type,
        func.sum(IncomeExpenses.amount)
    ).group_by(IncomeExpenses.category,IncomeExpenses.type).all()

  # Requête de dépenses par date
    dates = session.query(
        func.date(IncomeExpenses.date),
        IncomeExpenses.type,
        func.sum(IncomeExpenses.amount)
    ).group_by(func.date(IncomeExpenses.date), IncomeExpenses.type).order_by(func.date(IncomeExpenses.date)).all()


    return flask.render_template('dashboard.html',title='dashboard',
                                 income_vs_expense=income_vs_expense,
                                 category_comparison=category_comparison,
                                 dates=dates)