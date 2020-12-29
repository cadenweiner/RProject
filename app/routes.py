from __future__ import print_function
import sys
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_sqlalchemy import sqlalchemy
from flask_login import current_user, login_user, logout_user, login_required

from app import app,db

from app.forms import RegistrationForm, LoginForm, DeleteForm, DishCreationForm, BeverageCreationForm, NewIngredientForm, DishOrderForm, BeverageOrderForm
from app.models import Dish, Beverage, Ingredient, beverageIngredients, dishIngredients, Manager


@app.before_first_request
def initDB(*args, **kwargs):
    db.create_all()
    if Ingredient.query.count() == 0:
        ingredients = [{'name': 'Tequila', 'price': 1.5, 'salesPrice': 3, 'ingredientType':3}, {'name': 'Chicken', 'price': 2, 'salesPrice':4 , 'ingredientType':2 }, {'name': 'Sake', 'price': 4, 'salesPrice':6.5 , 'ingredientType':1 }]#{'name': , 'price': , 'salesPrice': , 'ingredientType': }
        for i in ingredients:
            db.session.add(Ingredient(name=i['name'], price=i['price'], salesPrice=i['salesPrice'], ingredientType=i['ingredientType']))
        db.session.commit()
    if Beverage.query.count() == 0:
        beverages = [{'name': 'Tequila', 'price': 1.5, 'salesPrice': 3}, {'name': 'Chicken', 'price': 2, 'salesPrice':4}, {'name': 'Sake', 'price': 4, 'salesPrice':6.5}]#{'name': , 'price': , 'salesPrice': , 'ingredientType': }
        for b in beverages:
            db.session.add(Beverage(name=b['name'], price=b['price'], salesPrice=b['salesPrice']))
        db.session.commit()        

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.add(current_user)
        db.session.commit()

@app.route('/', methods=['GET', 'Post'])
@app.route('/menu', methods=['GET', 'POST'])
def menu():
    ingredients = Ingredient.query.all()
    return render_template('menu.html', ingredients = ingredients)

@app.route('/login', methods=['GET', 'POST'])
def login(): 
    if current_user.is_authenticated:
        return redirect(url_for('menu'))
    form = LoginForm()
    if form.validate_on_submit():
        manager = Manager.query.filter_by(username=form.username.data).first()
        if manager is None or not manager.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(manager, remember=form.remember_me.data)
        return redirect(url_for('menu'))
    return render_template('login.html', title='Sign In', form=form)



@app.route('/register', methods=['GET', 'POST'])
def register(): 
    form = RegistrationForm()
    if form.validate_on_submit():
        manager = Manager(username=form.username.data, email=form.email.data, firstname=form.firstname.data,lastname=form.lastname.data, address=form.address.data )
        manager.set_password(form.password.data)
        db.session.add(manager)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('menu'))
    return render_template('registerCustomer.html', title='Register', form=form)

@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('menu'))



#create a menu that can be seen by anyone
#add security for login
@app.route('/drinkorder', methods=['GET', 'POST'])# need a way to keep track of an order. Add to users cart? And also add to Managers cart?
def orderdrink():
    form = BeverageOrderForm()
    if form.validate_on_submit():
    
        flash('Congratulations, you ordered a beverage!')
        return redirect(url_for('orderdrink'))
    return render_template('beverageorder.html', title='OrderDrink', form=form)   

@app.route('/foodorder', methods=['GET', 'POST'])# need a way to keep track of an order. Add to users cart? And also add to Managers cart? Order number. Way to mark order fufilled.
def orderdish():
    form = DishOrderForm()
    if form.validate_on_submit():
    
        flash('Congratulations, you ordered a Meal!')
        return redirect(url_for('orderdish'))
    return render_template('dishorder.html', title='OrderDish', form=form)   


#add security for log in
@app.route('/createdrink', methods=['GET', 'POST'])
def createdrink():
    form = BeverageCreationForm()
    if form.validate_on_submit():
        drink = Beverage(name = form.beverage.data, price = form.beverageCost.data, salesPrice = form.beverageSalesCost.data, ingredients = form.ingredients.data)
        db.session.add(drink)
        db.session.commit()
        flash('Congratulations, you created a new beverage!')
        return redirect(url_for('createdrink'))
    return render_template('beveragecreate.html', title='CreateDrink', form=form)   

@app.route('/createdish', methods=['GET', 'POST'])
def createdish():
    form = DishCreationForm()
    if form.validate_on_submit():
        dish = Dish(name = form.dish.data, price = form.dishCost.data, salesPrice = form.dishSalesCost.data, ingredients = form.ingredients.data)
        db.session.add(dish)
        db.session.commit()
        flash('Congratulations, you created a new Meal!')
        return redirect(url_for('createdish'))
    return render_template('dishcreate.html', title='CreateDish', form=form)   

@app.route('/newingredient', methods=['GET', 'POST'])
def createingredient():
    form = NewIngredientForm()
    if form.validate_on_submit():
        ingredient = Ingredient(name = form.ingredientName.data, price = form.ingredientCost.data, salesPrice = form.ingredientSalesCost.data, ingredientType = form.ingredientType.data)
        db.session.add(ingredient)
        db.session.commit()
        flash('Congratulations, you added a new Ingredient!')
        return redirect(url_for('createingredient'))
    return render_template('createingredients.html', title='CreateIngredient', form=form)   

