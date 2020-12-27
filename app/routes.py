from __future__ import print_function
import sys
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_sqlalchemy import sqlalchemy
from flask_login import current_user, login_user, logout_user, login_required

from app import app,db

from app.forms import RegistrationForm, LoginForm, DeleteForm
from app.models import Dish, Beverage, Ingredient, beverageIngredients, dishIngredients, User, Manager


@app.before_first_request
def initDB(*args, **kwargs):
    db.create_all()
    if Ingredient.query.count() == 0:
        ingredients = [{'name': 'Tequila', 'price': 1.5, 'salesPrice': 3, 'ingredientType':3}, {'name': 'Chicken', 'price': 2, 'salesPrice':4 , 'ingredientType':2 }, {'name': 'Sake', 'price': 4, 'salesPrice':6.5 , 'ingredientType':1 }]#{'name': , 'price': , 'salesPrice': , 'ingredientType': }
        for i in ingredients:
            db.session.add(Ingredient(name=i['name'], price=i['price'], salesPrice=i['salesPrice'], ingredientType=i['ingredientType']))
        db.session.commit()


@app.route('/', methods=['GET', 'Post'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    ingredients = Ingredient.query.all()
    return render_template('index.html', ingredients = ingredients)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.add(current_user)
        db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login(): 
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)



@app.route('/register', methods=['GET', 'POST'])
def register(): 
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, firstname=form.firstname.data,lastname=form.lastname.data, address=form.address.data )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('index'))
    return render_template('registerCustomer.html', title='Register', form=form)

@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
