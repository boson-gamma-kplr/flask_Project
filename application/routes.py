import sys
sys.path.extend([".","./application"])

import flask
from flask import Flask, request,redirect, url_for
import flask_login
from flask_login import LoginManager, login_required
from django.utils.http import url_has_allowed_host_and_scheme

import wtforms.form 
from models import User

login_manager = LoginManager()

app = Flask(__name__)
login_manager.init_app(app)

# @login_manager.user_loader
# def load_user(user_id):
#     return User.get(user_id)

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     # Here we use a class of some kind to represent and validate our
#     # client-side form data. For example, WTForms is a library that will
#     # handle this for us, and we use a custom LoginForm to validate.
#     form = wtforms.form.LoginForm()
#     if form.validate_on_submit():
#         # Login and validate the user.
#         # user should be an instance of your `User` class
#         #!!!!!!!!!!!!!!!!! check this later !!!!!!!!!!!!!!!!!!!!!!
#         user = User.get(0)
#         wtforms.form.login_user(user)

#         flask.flash('Logged in successfully.')

#         next = flask.request.args.get('next')
#         # url_has_allowed_host_and_scheme should check if the url is safe
#         # for redirects, meaning it matches the request host.
#         # See Django's url_has_allowed_host_and_scheme for an example.
#         if not url_has_allowed_host_and_scheme(next, request.host):
#             return flask.abort(400)

#         return flask.redirect(next or flask.url_for('index'))
#     return flask.render_template('login.html', form=form)

# @app.route('/')
# @login_required
# def index():
#     """root page"""

#     return flask.render_template('index.html')


# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     return redirect(somewhere)

# @login_manager.unauthorized_handler     # In unauthorized_handler we have a callback URL 
# def unauthorized_callback():            # In call back url we can specify where we want to 
#        return redirect(url_for('login'))



#!!!!!!!!!!!!!!!!!!!!!!!
app.secret_key = 'super secret string'  # Change this!

# Our mock database.
users = {'foo@bar.tld': {'pw': 'secret'}}

class FlaskLoginUser(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = FlaskLoginUser()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = FlaskLoginUser()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['pw'] == users[email]['pw']

    return user


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

@app.route('/')
def index():
    if flask_login.current_user.is_anonymous:
        return 'Hello anonymous user'
    else:
        return f'Hello {flask_login.current_user.id}'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'></input>
                <input type='password' name='pw' id='pw' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form>
               '''

    email = flask.request.form['email']
    if flask.request.form['pw'] == users[email]['pw']:
        user = FlaskLoginUser()
        user.id = email
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('protected'))

    return 'Bad login'

@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'