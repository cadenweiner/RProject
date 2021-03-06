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
    if User.query.count() == 0:
        #customer 1
        user = User(username = "Caden", firstname = "Caden", lastname = "Weiner", address = "Home", email = "cadenweiner67@gmail.com")
        user.set_password("123")
        db.session.add(user)
        db.session.commit()
        #customer 2
        user = User(username = "Null", firstname = "Null", lastname = "0", address = "Home", email = "caden.weiner@wsu.edu")
        user.set_password("123")
        db.session.add(user)
        db.session.commit()
    if Manager.query.count() == 0:
        #manager
        muser = User(username = "Manager Lycoris", firstname = "Lycoris", lastname = "Raidata", address = "Home", email = "lycoris.raidata@wsu.edu", is_manager = True)
        muser.set_password("123")
        db.session.add(muser)
        db.session.commit()
        manager = Manager(user_id = muser.id, shop_name = "Angel's Tears")
        db.session.add(manager)
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
    if not current_user.is_manager: 
    
        #pass in a list of all of the drinks to the rendered template#create a box for each item that contains a beverage form.     #take the item in as an input#like the delete functionality for smile.     # no need for the  query select field
        if Order.query.filter_by(user_id = current_user.id).count() == 0: # they already have an existing order
            order = Order(user_id = current_user.id, username = current_user.username) #need to create an order
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
    else: 
        return render_template('not_authorized.html')
      
@login_required
@app.route('/drinklist', methods=['GET', 'POST'])# need a way to keep track of an order. Add to users cart? And also add to Managers cart? Order number. Way to mark order fufilled.
def list_drinks():
    if not current_user.is_manager: 
        form = BeverageOrderForm()
        beverages = Beverage.query.all()
        ingredients = get_drink_ingredients()
        return render_template('beverageorder.html', title='Order Drink', form=form, beverages = beverages, ingredients = ingredients) 
    else: 
        return render_template('not_authorized.html')

@login_required
@app.route('/dishorder/<name>', methods=['GET', 'POST'])# need a way to keep track of an order. Add to users cart? And also add to Managers cart? Order number. Way to mark order fufilled.
def orderdish(name):
#pass in a list of all of the drinks to the rendered template#create a box for each item that contains a beverage form.     #take the item in as an input#like the delete functionality for smile.     # no need for the  query select field
    if not current_user.is_manager: 
        if Order.query.filter_by(user_id = current_user.id).count() == 0: # they already have an existing order
            order = Order(user_id = current_user.id, username = current_user.username) #need to create an order
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
    else: 
        return render_template('not_authorized.html')

      
@login_required
@app.route('/dishlist', methods=['GET', 'POST'])# need a way to keep track of an order. Add to users cart? And also add to Managers cart? Order number. Way to mark order fufilled.
def list_dishes():
    if not current_user.is_manager: 
        form = DishOrderForm()
        dishes = Dish.query.all()
        ingredients = get_dish_ingredients()
        return render_template('dishorder.html', title='Order Dish', form=form, dishes = dishes, ingredients = ingredients) 
    else: 
        return render_template('not_authorized.html')


#add security for log in. if statements to verify they are the manager
@login_required
@app.route('/createdrink', methods=['GET', 'POST'])
def createdrink():
    if current_user.is_manager:
        form = BeverageCreationForm()
        if form.validate_on_submit():
            drink = Beverage(name = form.beverage.data, price = form.beverageCost.data, salesPrice = form.beverageSalesCost.data, ingredients = form.ingredients.data)
            db.session.add(drink)
            db.session.commit()
            flash('Congratulations, you created a new beverage!')
            return redirect(url_for('createdrink'))
        return render_template('beveragecreate.html', title='CreateDrink', form=form)   
    else: 
        return render_template('not_authorized.html')

@login_required
@app.route('/createdish', methods=['GET', 'POST'])
def createdish():
    if current_user.is_manager:
        form = DishCreationForm()
        if form.validate_on_submit():
            dish = Dish(name = form.dish.data, price = form.dishCost.data, salesPrice = form.dishSalesCost.data, ingredients = form.ingredients.data)
            db.session.add(dish)
            db.session.commit()
            flash('Congratulations, you created a new Meal!')
            return redirect(url_for('createdish'))
        return render_template('dishcreate.html', title='CreateDish', form=form)   
    else: 
        return render_template('not_authorized.html')

@login_required
@app.route('/newingredient', methods=['GET', 'POST'])
def createingredient():
    if current_user.is_manager:
        form = NewIngredientForm()
        if form.validate_on_submit():
            ingredient = Ingredient(name = form.ingredientName.data, price = form.ingredientCost.data, salesPrice = form.ingredientSalesCost.data, ingredientType = form.ingredientType.data)
            db.session.add(ingredient)
            db.session.commit()
            flash('Congratulations, you added a new Ingredient!')
            return redirect(url_for('createingredient'))
        return render_template('createingredients.html', title='CreateIngredient', form=form)   
    else: 
        return render_template('not_authorized.html')



@login_required
@app.route('/list_order', methods=['GET', 'POST'])
def list_order():
    
    if current_user.is_manager: #manager
        orders = Order.query.all()
        flash("View Orders")
        form = CompletionForm()
        return render_template('view_orders.html', orders = orders, form = form)
    else: #student
#need an if statement, if there is no order create a new one for the user
        if Order.query.filter_by(user_id = current_user.id).count() == 0: # the user does not have an order
            order = Order(user_id = current_user.id, username = current_user.username)
            db.session.add(order)
            db.session.commit()
        else: # they already have an order
            order = Order.query.filter_by(user_id = current_user.id).first()

        if order.order_fufilled == True: # if order is fufilled then the student can't order it again
            flash('You do not currently have an order')
            #start new order button: sets the order_fufilled to false
            #when the manager completes the order, procedes to delete all items in the cart
            return redirect(url_for('menu'))
        flash("The order has been fufilled {}".format(order.order_fufilled))
        items = Item.query.filter_by(order_id = order.cart_id)
        dform = DeleteForm()
        form = CompletionForm()
        return render_template('checkout.html', order = order, items = items, form = form, dform = dform)
                
@login_required
@app.route('/place_order/<order_id>', methods=['GET', 'POST'])
def place_order(order_id):
    if not current_user.is_manager:
        order = Order.query.filter_by(cart_id = order_id).first()
        #need to check if the order is empty or not first
        if order.user_id == current_user.id:
            order.order_fufilled = True # order is placed don't let them order it again
            db.session.commit()
            return redirect(url_for('menu'))
        else : 
            flash("The order was not placed because it was not your order")
            return redirect(url_for('list_order'))
    else: 
        return render_template('not_authorized.html')

#we need another variable to see if the manager has made the order. Ready for pickup?
    

@login_required
@app.route('/remove_item/<item_id>', methods=['GET', 'POST', 'DELETE'])
def remove_item(item_id):
    if not current_user.is_manager:
        item = Item.query.get(item_id) #must use id, or another unique identifier
    
        for i in item.ingredients:
            item.ingredients.remove(i)

        db.session.commit()
        db.session.delete(item)
        db.session.commit()
        flash('Removed the Item')
        return redirect(url_for('list_order'))
    else: 
        return render_template('not_authorized.html')

@login_required
@app.route('/fufill_order/<cart_id>', methods=['GET', 'POST'])
def fufill_order(cart_id):
    if current_user.is_manager:
        #delete the completed order and email the user
        #
        #Flask Email
        #tell them that their order is completed
        #Delete order, its not needed anymore
        order = Order.query.get(cart_id)
        for item in order.cart_items: 
            for ingredient in item.ingredients: 
                item.ingredients.remove(ingredient) # remove the ingredient from the items ingredients
            db.session.commit()
            db.session.delete(item)
            db.session.commit()#removes the item

        #user = User.query.filter_by(id = order.user_id).first()# this is the user to be emailed
        
        #send_password_order_completed_email(user)# sends the email that their order is completed
        #currently giving a run connect error first. I have tried to deal with this however I have not been taught email functionality. I will have to research at a different time



        #removes all of the items in the order
        db.session.commit()
        db.session.delete(order)
        db.session.commit()#removes the order after all its items and the items ingredients are removed

        #allows the manager to continue viewing orders
        return redirect(url_for('list_order')) # only managers can complete an order
    else: 
        return render_template('not_authorized.html')



#Let an order change their information