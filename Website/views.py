from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import *
import requests


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
            sec_code = request.form.get("code")

            if len(cardNmb) < 8:
                flash('Broj kartice nije validan!',category='error')  
            elif len(sec_code) < 1:
                flash('Sigurnosni kod kartice nije unet!',category='error')  
            else:
                sec_code = int(sec_code)
                url = 'https://api.exchangerate.host/latest?base=RSD'
                response = requests.get(url)
                data = response.json()
                conversionRate=data['rates']["USD"]

                card = CreditCard.query.filter_by(cardNumber=cardNmb).first()
                if card:
                    if card.code == sec_code: 
                        card.user_id = current_user.id
                        card.state = card.state - 1/conversionRate
                        current_user.verified = True
                        db.session.commit()
                        return redirect(url_for('views.home'))
                    else:
                        flash('Nije dobar sigurnosni kod!',category='error')
                        return redirect(url_for('views.verify'))
                else:
                    flash('Ne postoji kartica sa tim brojem!',category='error')
                    return redirect(url_for('views.verify'))

            

    return render_template("verify.html", user=current_user)

@views.route('/payment',methods=['GET','POST'])
@login_required
def payment():
    

    url = 'https://api.exchangerate.host/latest?base=RSD'
    response = requests.get(url)
    data = response.json()
    dictionaryCurrency={}
    
    for key in data['rates']:
        currency=Currency.query.filter_by(id=key).first()
        dictionaryCurrency[key]=data['rates'][key]
        
        if(currency):
            currency.conversionRate=data['rates'][key]
        else:
            new_Currency=Currency(id=key,conversionRate=data['rates'][key])
            db.session.add(new_Currency)
            db.session.commit()
    
    if request.method =='POST': 
        ammount = request.form.get("ammount")
        
        currency= str(request.form.get("currency"))
        
        conversionRate=dictionaryCurrency[currency]
        
        check=False
        if len(ammount) < 1:
            flash('Unesite iznos',category='error')
        else:
            ammount = float(ammount)
            for creditCard in current_user.creditCard:
                if creditCard.user_id == current_user.id and (creditCard.state >= ammount):
                    creditCard.state = creditCard.state - ammount
                    
                    for state in current_user.state: 
                        
                        if state.currency == currency and state.user_id == current_user.id:
                            state.ammount = ammount*conversionRate + state.ammount
                            check=True
                            db.session.commit()
                            flash('Uspesno uplacen novac!',category='success')
                            
                else:
                    check=True
                    flash('Kartica nema toliko novca!',category='error')
            
            if not check:
                        new_State=State(currency=currency,ammount=ammount*conversionRate,user_id = current_user.id)
                        db.session.add(new_State)
                        db.session.commit()
                        flash('Uspesno uplacen novac!',category='success')
            return redirect(url_for('views.payment'))
    
    
    return render_template("payment.html", user=current_user,dictionaryCurrency=dictionaryCurrency)


@views.route('/user-transaction',methods=['GET','POST'])
@login_required
def user_transaction():
    url = 'https://api.exchangerate.host/latest?base=RSD'
    response = requests.get(url)
    data = response.json()
    dictionaryCurrency={}
    
    for key in data['rates']:
        currency=Currency.query.filter_by(id=key).first()
        dictionaryCurrency[key]=data['rates'][key]
        
        if(currency):
            currency.conversionRate=data['rates'][key]
        else:
            new_Currency=Currency(id=key,conversionRate=data['rates'][key])
            db.session.add(new_Currency)
            db.session.commit()

    if request.method =='POST': 
        email = request.form.get('email')
        ammount = request.form.get("ammount")
        currency= str(request.form.get("currency"))
        conversionRate=dictionaryCurrency[currency]

        user = User.query.filter_by(email=email).first()

        check=False

        if len(email) < 1:
            flash('Polje email je prazno',category="error")
        elif len(ammount) < 1:
            flash('Polje iznos je prazno',category="error")
        elif email == current_user.email:
            flash('Uneli ste vas email',category="error")
        else:
            ammount = float(ammount)
            if user:
                for state in user.state: 
                    if state.currency == currency and state.user_id == user.id:

                        for creditCard in current_user.creditCard:
                            if creditCard.user_id == current_user.id and (creditCard.state >= ammount):
                                creditCard.state = creditCard.state - ammount
                            else:
                                flash('Korisnik nema toliko novca na kartici',category="error")
                                return redirect(url_for('views.user_transaction'))

                        state.ammount = ammount*conversionRate + state.ammount
                        
                        check=True
                        db.session.commit()
                        flash('Uspesno uplacen novac!',category='success')
                    
                if not check:
                    for creditCard in current_user.creditCard:
                            if creditCard.user_id == current_user.id and (creditCard.state >= ammount):
                                creditCard.state = creditCard.state - ammount
                            else:
                                flash('Korisnik nema toliko novca na kartici',category="error")
                                return redirect(url_for('views.user_transaction'))
                    new_State=State(currency=currency,ammount=ammount*conversionRate,user_id = user.id)
                    db.session.add(new_State)
                    db.session.commit()
                    flash('Uspesno uplacen novac!',category='success')
            else:  
                flash('Korisnik sa tim email-om ne postoji',category="error")
                return redirect(url_for('views.user_transaction'))
            
    
    return render_template("user_transaction.html", user=current_user,dictionaryCurrency=dictionaryCurrency)