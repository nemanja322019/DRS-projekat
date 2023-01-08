from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'qweqweqwe'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User,Currency

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    
    
    return app

def create_database(app):
    if not path.exists('instance/' + DB_NAME):

        from .models import CreditCard

        with app.app_context():
            db.create_all()
            new_card1 = CreditCard(cardNumber = 11111111, name = "Vladimir",date = "12/12/2023", code = 111,state = 10000,user_id = None)
            new_card2 = CreditCard(cardNumber = 22222222, name = "Nemanja",date = "12/11/2023", code = 222,state = 10000,user_id = None)
            new_card3 = CreditCard(cardNumber = 33333333, name = "Miljko",date = "12/10/2023", code = 333,state = 10000,user_id = None)
            new_card4 = CreditCard(cardNumber = 44444444, name = "Aleksandar",date = "12/09/2023", code = 444,state = 10000,user_id = None)
            new_card5 = CreditCard(cardNumber = 55555555, name = "Irena",date = "12/09/2023", code = 555,state = 10000,user_id = None)
            db.session.add(new_card1)
            db.session.add(new_card2)
            db.session.add(new_card3)
            db.session.add(new_card4)
            db.session.add(new_card5)
            db.session.commit()
            print("Created database!")