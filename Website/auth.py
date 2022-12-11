from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)

@auth.route('/login',methods=['GET','POST'])
@auth.route('/login')
def login():
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return "<p>Logout</p>"

@auth.route('/sign-up',methods=['GET','POST'])
@auth.route('/sign-up')
def sign_up():
    if request.method =='POST':
        name = request.form.get('name')
        last_name = request.form.get('last-name')
        adress = request.form.get('adress')
        city = request.form.get('city')
        country = request.form.get('country')
        phNumber = request.form.get('phNumber')
        email = request.form.get('email')
        password = request.form.get('pasword')

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
        elif len(email) < 1:
            flash('Polje emal je prazno',category="error")
        elif  int(phNumber) == False or len(phNumber) < 1:
            flash('Polje broj telefona je prazno',category="error")
        elif len(password) < 1:
            flash('Polje lozika je prazno',category="error")
        else:
            flash('Uspeno registrovanje',category="success")
    

    
    return render_template("sign_up.html")