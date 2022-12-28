from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import *



views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/state')
@login_required
def state():
    return render_template("state.html", user=current_user)

@views.route('/verify',methods=['GET','POST'])
@login_required
def verify():
    if request.method =='POST': 
            cardNmb = request.form.get("cardNumber")
            user_name = request.form.get("user_name")
            exp_date = request.form.get("exp_date")
            sec_code = request.form.get("code")

            if len(cardNmb) < 8:
                flash('Broj kartice nije validan!',category='error')
            elif len(user_name) < 1:
                flash('Korisnicko ime nije uneto!',category='error')
            elif len(exp_date) < 1:
                flash('Datum isteka kartice nije unet!',category='error')    
            elif len(sec_code) < 1:
                flash('Sigurnosni kod kartice nije unet!',category='error')  
            else:
                new_card = CreditCard(cardNumber = cardNmb, name = user_name,date = exp_date, code = sec_code,user_id = current_user.id)
                current_user.verified = True
                db.session.add(new_card)
                db.session.commit()
                return redirect(url_for('views.home'))

    return render_template("verify.html", user=current_user)

@views.route('/payment',methods=['GET','POST'])
@login_required
def payment():
    if request.method =='POST': 
        ammount = int(request.form.get("ammount"))
        
        for creditCard in current_user.creditCard:
            if creditCard.user_id == current_user.id and creditCard.state >= ammount:
                creditCard.state = creditCard.state - ammount

                for state in current_user.state: 
                        if state.currency == "RSD" and state.user_id == current_user.id:
                            state.ammount = ammount + state.ammount

                db.session.commit()
                flash('Uspesno uplacen novac!',category='success')
            else:
                flash('Kartica nema toliko novca!',category='error')
        
        return redirect(url_for('views.payment'))
    
    
    return render_template("payment.html", user=current_user)
