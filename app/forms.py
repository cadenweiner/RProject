from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, PasswordField, BooleanField, FloatField 
from wtforms.validators import  ValidationError, DataRequired, EqualTo, Length, Email, NumberRange
from app.models import Dish, Beverage, Ingredient, beverageIngredients, dishIngredients, User, Manager
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput

#ingredient_choices = [(i.id, i.name) for i in Ingredient.query.all()]

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address =  TextAreaField('Address', [Length(min=0, max=200)])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('The username already exists! Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('The email already exists! Please use a different email address.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class DeleteForm(FlaskForm): 
    delete = SubmitField('Delete')
def get_dish_ingredients():
    return Ingredient.query.filter(Ingredient.ingredientType.in_([2, 3]))
def dish_choices():
    return Dish.query

def get_drink_ingredients():
    return Ingredient.query.filter(Ingredient.ingredientType.in_([1, 3]))
#beverage_choices = [(b.id, b.name) for b in Beverage.query.order_by(Beverage.name.desc())]
def beverage_choices():
    return Beverage.query    
class DishCreationForm(FlaskForm):
    dish = StringField('Dish', validators=[DataRequired(), Length(min=0, max=30)])
    ingredients = QuerySelectMultipleField('Ingredients', query_factory = get_dish_ingredients, get_label='name',
                                  widget=ListWidget(prefix_label=False), option_widget=CheckboxInput() )
    dishCost = FloatField('Cost', validators=[DataRequired(), NumberRange(min = 0, max=100000, message="Invalid Cost")])
    dishSalesCost = FloatField('SalesCost', validators=[DataRequired(), NumberRange(min = 0, max=1000000, message="Invalid Cost")])
    submit = SubmitField('Create')

class BeverageCreationForm(FlaskForm):
    beverage = StringField('Beverage', validators=[DataRequired(), Length(min=0, max=30)])
    ingredients = QuerySelectMultipleField('Ingredients', query_factory = get_drink_ingredients, get_label='name',
                              widget=ListWidget(prefix_label=False), option_widget=CheckboxInput() )
    beverageCost = FloatField('Cost',validators=[DataRequired(), NumberRange(min = 0, max=100000, message="Invalid Cost")])
    beverageSalesCost = FloatField('SalesCost', validators=[DataRequired(), NumberRange(min = 0, max=1000000, message="Invalid Cost")])
    submit = SubmitField('Create')

class NewIngredientForm(FlaskForm):
    ingredientName = StringField('Ingredient Name', validators=[DataRequired(), Length(min=0, max=30)])
    ingredientType = SelectField('Ingredient Type', choices = [(1,'For Drinks'), (2,'For Foods'), (3,'For Either')])
    ingredientCost = FloatField('Cost', validators=[DataRequired(), NumberRange(min = 0, max=10000, message="Invalid Cost")])
    ingredientSalesCost = FloatField('SalesCost', validators=[NumberRange(min = -.01, max=100000, message="Invalid Cost")])
    submit = SubmitField('Create')


#beverage_choices = [(b.id, b.name) for b in Beverage.query.order_by(Beverage.name.desc())]
class DishOrderForm(FlaskForm): #a list of the dishes is presented
#     #list all dishes and their costs and you can choose from them
#     #use a multiple select field
    dish = QuerySelectField('dishes', query_factory = dish_choices, get_label='name')
    
    ingredients = QuerySelectMultipleField('ingredients', query_factory = get_dish_ingredients, get_label='name',
                                  widget=ListWidget(prefix_label=False), option_widget=CheckboxInput() )
    submit = SubmitField('Order')




class BeverageOrderForm(FlaskForm): #a list of the dishes is presented
#     #list all dishes and their costs and you can choose from them
#     #use a multiple select field
    beverage = QuerySelectField('beverages', query_factory = beverage_choices, get_label='name')
    
    ingredients = QuerySelectMultipleField('ingredients', query_factory = get_drink_ingredients, get_label='name',
                                  widget=ListWidget(prefix_label=False), option_widget=CheckboxInput() )
    submit = SubmitField('Order')