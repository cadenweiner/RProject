from __future__ import print_function
import sys
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_sqlalchemy import sqlalchemy
from flask_login import current_user, login_user, logout_user, login_required

from app import app,db

from app.forms import RegistrationForm, LoginForm, DeleteForm, DishCreationForm, BeverageCreationForm, NewIngredientForm, DishOrderForm, BeverageOrderForm, CompletionForm, get_drink_ingredients, get_dish_ingredients
from app.models import Dish, Beverage, Ingredient, beverageIngredients, dishIngredients, Manager, Item, User, Order


@app.before_first_request
def initDB(*args, **kwargs):
    db.create_all()
    if Ingredient.query.count() == 0:
        ingredients = [{'name': 'Tequila', 'price': 1.5, 'salesPrice': 3, 'ingredientType':3}, {'name': 'Chicken', 'price': 2, 'salesPrice':4 , 'ingredientType':2 }, {'name': 'Sake', 'price': 4, 'salesPrice':6.5 , 'ingredientType':1 }]#{'name': , 'price': , 'salesPrice': , 'ingredientType': }
        for i in ingredients:
            db.session.add(Ingredient(name=i['name'], price=i['price'], salesPrice=i['salesPrice'], ingredientType=i['ingredientType']))
        db.session.commit()
    if Beverage.query.count() == 0:
        beverages = [{'name': 'Tequila', 'price': 1.5, 'salesPrice': 3}, {'name': 'Lemon Juice', 'price': 2, 'salesPrice':4}, {'name': 'Sake', 'price': 4, 'salesPrice':6.5}]#{'name': , 'price': , 'salesPrice': , 'ingredientType': }
        for b in beverages:
            db.session.add(Beverage(name=b['name'], price=b['price'], salesPrice=b['salesPrice']))
        db.session.commit()     
    if Dish.query.count() == 0:
        dishes = [{'name': 'Hamburger', 'price': 1.5, 'salesPrice': 3}, {'name': 'Pasta', 'price': 2, 'salesPrice':4}, {'name': 'Steak', 'price': 4, 'salesPrice':6.5}]#{'name': , 'price': , 'salesPrice': , 'ingredientType': }
        for d in dishes:
            db.session.add(Dish(name=d['name'], price=d['price'], salesPrice=d['salesPrice']))
        db.session.commit()             


@app.route('/', methods=['GET', 'Post'])
@app.route('/menu', methods=['GET', 'POST'])
def menu():
    ingredients = Ingredient.query.all()
    dishes = Dish.query.all()
    beverages = Beverage.query.all()
    return render_template('menu.html',dishes = dishes, beverages = beverages, ingredients = ingredients)

@app.route('/login', methods=['GET', 'POST'])
def login(): 
    if current_user.is_authenticated:
        return redirect(url_for('menu'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('menu'))
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
        return redirect(url_for('menu'))
    return render_template('registerCustomer.html', title='Register', form=form)

@login_required
@app.route('/logout')
def logout():

    logout_user()
    return redirect(url_for('menu'))



#create a menu that can be seen by anyone
#add security for login
@login_required
@app.route('/drinkorder/<name>', methods=['GET', 'POST'])# need a way to keep track of an order. Add to users cart? And also add to Managers cart?
def orderdrink(name):
    #pass in a list of all of the drinks to the rendered template#create a box for each item that contains a beverage form.     #take the item in as an input#like the delete functionality for smile.     # no need for the  query select field
    if Order.query.filter_by(user_id = current_user.id).count() == 0: # they already have an existing order
        order = Order(user_id = current_user.id).first() #need to create an order
        db.session.add(order)
        db.session.commit()
    else: 
        order = Order.query.filter_by(user_id = current_user.id).first()
    items = Item.query.filter_by(order_id = order.cart_id).all()
    order.cart_items = items
    order.user_id = current_user.id
    db.session.commit()
    drink = Beverage.query.filter_by(name = name).first()
    item = Item(order_id = order.cart_id, name = name, price = drink.price, salesPrice = drink.salesPrice, itemType = 'drink')
        #item.name = form.beverage.data
    db.session.add(item)
    db.session.add(order)
    db.session.commit()
    flash('Congratulations, you ordered a beverage!')
    return redirect(url_for('list_drinks'))
      
@login_required
@app.route('/drinklist', methods=['GET', 'POST'])# need a way to keep track of an order. Add to users cart? And also add to Managers cart? Order number. Way to mark order fufilled.
def list_drinks():
    form = BeverageOrderForm()
    beverages = Beverage.query.all()
    ingredients = get_drink_ingredients()
    return render_template('beverageorder.html', title='Order Drink', form=form, beverages = beverages, ingredients = ingredients) 
    

@login_required
@app.route('/dishorder/<name>', methods=['GET', 'POST'])# need a way to keep track of an order. Add to users cart? And also add to Managers cart? Order number. Way to mark order fufilled.
def orderdish(name):
#pass in a list of all of the drinks to the rendered template#create a box for each item that contains a beverage form.     #take the item in as an input#like the delete functionality for smile.     # no need for the  query select field
    if Order.query.filter_by(user_id = current_user.id).count() == 0: # they already have an existing order
        order = Order(user_id = current_user.id).first() #need to create an order
        db.session.add(order)
        db.session.commit()
        flash("order created")
    else: 
        order = Order.query.filter_by(user_id = current_user.id).first()

    items = Item.query.filter_by(order_id = order.cart_id).all()
    order.cart_items = items
    order.user_id = current_user.id
    db.session.commit()
    dish = Dish.query.filter_by(name = name).first()
    item = Item(order_id = order.cart_id, name = name, price = dish.price, salesPrice = dish.salesPrice, itemType = 'dish')
    db.session.add(item)
    db.session.commit()
    flash('Congratulations, you ordered a dish!')
    return redirect(url_for('list_dishes'))
      
@login_required
@app.route('/dishlist', methods=['GET', 'POST'])# need a way to keep track of an order. Add to users cart? And also add to Managers cart? Order number. Way to mark order fufilled.
def list_dishes():
    form = DishOrderForm()
    dishes = Dish.query.all()
    ingredients = get_dish_ingredients()
    return render_template('dishorder.html', title='Order Dish', form=form, dishes = dishes, ingredients = ingredients) 
    

#add security for log in. if statements to verify they are the manager
@login_required
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

@login_required
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

@login_required
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



@login_required
@app.route('/list_order', methods=['GET', 'POST'])
def list_order():
    
    if current_user.is_manager: #manager
        orders = Order.query.all()
        return render_template('view_orders.html', orders = orders)
    else: #student
        order = Order.query.filter_by(user_id = current_user.id).first()
        items = Item.query.filter_by(order_id = order.cart_id)
        dform = DeleteForm()
        form = CompletionForm()
        return render_template('checkout.html', order = order, items = items, form = form, dform = dform)
                
@login_required
@app.route('/place_order/<order_id>', methods=['GET', 'POST'])
def place_order(order_id):
    
    order = Order.filter_by(order_id = order_id)
    if order.user_id == current_user.id:
        order.order_fufilled = True
        flash("The order has been placed")
    else : 
        flash("The order was not placed")
        return redirect(url_for(list_order))
    render_template('menu')

    

@login_required
@app.route('/remove_item/<name>', methods=['GET', 'POST', 'DELETE'])
def remove_item(name):
    item = Item.query.get(name)
    
    for i in item.ingredients:
        item.ingredients.remove(i)

    db.session.commit()
    db.session.delete(item)
    db.session.commit()
    flash('Removed the Item')
    return redirect(url_for('list_order'))


@login_required
@app.route('/fufill_order/<order_id>', methods=['GET', 'POST'])
def fufill_order():
    
    return redirect(url_for('list_order'))


