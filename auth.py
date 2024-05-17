from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from flask_login import login_user, logout_user, login_required, current_user
from __init__ import db

from forms import RegistrationForm, LoginForm


####################################################################
auth = Blueprint('auth', __name__) # create a Blueprint object that 
                                   # we name 'auth'

####################################################################
@auth.route('/login', methods=['GET', 'POST']) # define login page path
def login(): # define login page fucntion
    form = LoginForm(request.form)
    if request.method=='POST': # if the request is a GET we return the login page
        user = User.query.filter_by(username=form.username.data).first()
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, form.password.data):
            flash('Wrong credentials!')
            return redirect(url_for('auth.login', form=form)) # if the user doesn't exist or password is wrong, reload the page
        # if the above check passes, then we know the user has the right credentials
        login_user(user)
        return redirect(url_for('main.profile'))
    else: # if the request is POST the we check if the user exist and with te right password
        return render_template('login.html', form=form)

####################################################################
@auth.route('/signup', methods=['GET', 'POST'])# we define the sign up path
def signup(): # define the sign up function
    form = RegistrationForm(request.form)
    if request.method=="POST" and form.validate(): # if the request is POST, then we check if the email doesn't already exist and then we save data
        user = User.query.filter_by(email=form.email.data).first() # if this returns a user, then the email already exists in database
        if user: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email address already exists')
            return redirect(url_for('auth.signup', form=form))
        new_user = User(email=form.email.data, name=form.name.data,  
            password=generate_password_hash(form.password.data, method='pbkdf2:sha256'), username=form.username.data,
            occupation=form.occupation.data, country=form.country.data) #
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    else:
        return render_template('signup.html', form=form)

####################################################################
@auth.route('/logout') # define logout path
def logout(): #define the logout function
    logout_user()
    return redirect(url_for('main.index'))