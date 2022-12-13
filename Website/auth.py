from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import *
from werkzeug .security import generate_password_hash, check_password_hash
from flask_login import login_user,login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password):
                flash('Uspesno logovanje!',category='success')
                login_user(user,remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Pogresna lozinka!',category='error')
        else:
            flash('Email ne postoji!',category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up',methods=['GET','POST'])
def sign_up():
    if request.method =='POST':
        name = request.form.get('name')
        last_name = request.form.get('last-name')
        adress = request.form.get('adress')
        city = request.form.get('city')
        country = request.form.get('country')
        phNumber = request.form.get('phNumber')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email vec postoji!',category='error')
        elif len(name) < 1:
            flash('Polje ime je prazno',category="error")
        elif len(last_name) < 1:
            flash('Polje prezime je prazno',category="error")
        elif len(adress) < 1:
            flash('Polje adresa je prazno',category="error")
        elif len(city) < 1:
            flash('Polje grad je prazno',category="error")
        elif len(country) < 1:
            flash('Polje drzava je prazno',category="error")
        elif len(email) < 1:
            flash('Polje email je prazno',category="error")
        elif  int(phNumber) == False or len(phNumber) < 1:
            flash('Polje broj telefona je prazno',category="error")
        elif len(password) < 1:
            flash('Polje lozinka je prazno',category="error")
        else:
            new_user =  User(name=name, last_name=last_name, adress=adress,city=city,country=country,phNumber=phNumber,email=email,password = generate_password_hash(password,method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user,remember=True)
            flash('Uspesno registrovanje',category="success")
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

@auth.route('/edit-profile',methods=['GET','POST'])
def edit_profile():
    if request.method =='POST':
        name = request.form.get('name')
        last_name = request.form.get('last-name')
        adress = request.form.get('adress')
        city = request.form.get('city')
        country = request.form.get('country')
        phNumber = request.form.get('phNumber')
        email = current_user.email
        password = request.form.get('password')

        if len(name) < 1:
            flash('Polje ime je prazno',category="error")
        elif len(last_name) < 1:
            flash('Polje prezime je prazno',category="error")
        elif len(adress) < 1:
            flash('Polje adresa je prazno',category="error")
        elif len(city) < 1:
            flash('Polje grad je prazno',category="error")
        elif len(country) < 1:
            flash('Polje drzava je prazno',category="error")
        elif  int(phNumber) == False or len(phNumber) < 1:
            flash('Polje broj telefona je prazno',category="error")
        elif len(password) < 1:
            flash('Polje lozinka je prazno',category="error")
        else:
            user = User.query.filter_by(email=email).first()
            user.name = name
            user.last_name = last_name
            user.adress = adress
            user.city = city
            user.country = country
            user.phNumber = phNumber
            user.password = generate_password_hash(password,method='sha256')
            db.session.commit()

            login_user(user,remember=True)
            flash('Uspesna izmena',category="success")
            return redirect(url_for('views.home'))

    return render_template("edit_profile.html",user = current_user)