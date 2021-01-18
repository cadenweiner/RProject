from datetime import datetime

from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash



@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# this is the assosiation table between two many to many tables. 
dishIngredients = db.Table('dishIngredients',
    db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id')), 
    db.Column('dish_id', db.Integer, db.ForeignKey('dish.id'))
)   
# this is the assosiation table between two many to many tables. 
beverageIngredients = db.Table('beverageIngredients',
    db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id')), 
    db.Column('beverage_id', db.Integer, db.ForeignKey('beverage.id'))
)   
# this is the assosiation table between two many to many tables. 
itemIngredients = db.Table('itemIngredients',
    db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id')), 
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'))
)   

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    price = db.Column(db.Float)
    salesPrice = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    ingredients = db.relationship ('Ingredient', secondary = dishIngredients, 
                            primaryjoin=(dishIngredients.c.dish_id == id),
                            backref=db.backref('dishIngredients', lazy='dynamic'), lazy='dynamic') 

class Beverage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique = True)
    price = db.Column(db.Float)
    salesPrice = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    ingredients = db.relationship ('Ingredient', secondary = beverageIngredients, 
                            primaryjoin=(beverageIngredients.c.beverage_id == id),
                            backref=db.backref('beverageIngredients', lazy='dynamic'), lazy='dynamic') 

class Ingredient(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150))
    price = db.Column(db.Float)
    salesPrice = db.Column(db.Float)
    ingredientType = db.Column(db.Integer)#1 = drink ingredient, #2 = food ingredient, #3 = food or drink ingredient
    drinks = db.relationship ('Beverage', secondary = beverageIngredients, 
                            primaryjoin=(beverageIngredients.c.ingredient_id == id),
                            backref=db.backref('beverageIngredients', lazy='dynamic'), lazy='dynamic') 
    meals = db.relationship ('Dish', secondary = dishIngredients, 
                            primaryjoin=(dishIngredients.c.ingredient_id == id),
                            backref=db.backref('dishIngredients', lazy='dynamic'), lazy='dynamic')
    items = db.relationship ('Item', secondary = itemIngredients, 
                            primaryjoin=(itemIngredients.c.ingredient_id == id),
                            backref=db.backref('itemIngredients', lazy='dynamic'), lazy='dynamic') 
    def __repr__(self):
        return '{}-{}'.format(self.id,self.name)

class User(UserMixin, db.Model): #default user is a customer
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    address = db.Column(db.String(200))
    email = db.Column(db.String(120), index=True, unique=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_manager = db.Column(db.Boolean, default = False) #no way to register as a manager except for from website for security
    order = db.relationship('Order', backref='user_orders', lazy = 'dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return '{}-{}'.format(self.id,self.username)
#can have a history of orders. 

#need a cart table to keep track of a current order
class Manager(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key = True) #student's user.id
    shop_name = db.Column(db.String(150))
    user = db.relationship("User", backref="user", uselist=False)

class Order(db.Model):
    cart_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cart_items = db.relationship('Item', backref='cart_items', lazy = 'dynamic')     
    order_fufilled = db.Column(db.Boolean, default = False)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.cart_id'))
    name = db.Column(db.String(150))
    price = db.Column(db.Float)
    salesPrice = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    itemType = db.Column(db.String(50)) #Dish or Beverage
    ingredients = db.relationship ('Ingredient', secondary = itemIngredients, 
                            primaryjoin=(itemIngredients.c.item_id == id),
                            backref=db.backref('itemIngredients', lazy='dynamic'), lazy='dynamic') 
