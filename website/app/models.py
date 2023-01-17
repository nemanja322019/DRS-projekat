from . import db
from flask_login import UserMixin



class CreditCard(db.Model):
    cardNumber = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(150))
    date = db.Column(db.String(150))
    code = db.Column(db.Integer)
    state = db.Column(db.Integer)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    
class State(db.Model):
    ammount = db.Column(db.Float)
    currency = db.Column(db.String(3))
    id=db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    adress = db.Column(db.String(150))
    city = db.Column(db.String(150))
    country = db.Column(db.String(150))
    phNumber = db.Column(db.Integer, unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    verified = db.Column(db.Boolean,default= False)
    state = db.relationship('State')
    creditCard = db.relationship('CreditCard')
    transaction = db.relationship('Transaction')

class Currency(db.Model):
    id=db.Column(db.String(3),primary_key=True)
    conversionRate=db.Column(db.Float)

class Transaction(db.Model):
    prim_key = db.Column(db.Integer,primary_key= True)
    id = db.Column(db.Integer)
    type = db.Column(db.String(50))
    state = db.Column(db.String(10))
    ammount = db.Column(db.Integer)
    currency= db.Column(db.String(3))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
