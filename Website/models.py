from . import db
from flask_login import UserMixin

class CreditCard(db.Model):
    cardNumber = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(150))
    date = db.Column(db.String(150))
    code = db.Column(db.Integer)
    state = db.Column(db.Integer,default=10000)
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
    state = db.Column(db.Integer,default = 0)
    creditCard = db.relationship('CreditCard')
   
