from flask import Blueprint, render_template, request, flash, redirect, url_for, Flask, copy_current_request_context
from flask_login import login_required, current_user, login_user
from .models import *
import requests
import random
import threading
import time  

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

################################################################################################
@views.route('/user-transaction',methods=['GET','POST'])
@login_required
def user_transaction():
    @copy_current_request_context
    def Thread2(ammount, email, currency, conversionRate):
        ammount = float(ammount)
        user = User.query.filter_by(email=email).first()
        new_Transaction=Transaction(id=random.randint(0,101),type="user-transaction",state='U obradi',ammount=ammount*conversionRate, user_id=current_user.id, currency=currency)
        db.session.add(new_Transaction)
        db.session.commit()
        check=False
        time.sleep(10)
        if user:
            for state in user.state: 
                if state.currency == currency and state.user_id == user.id:

                    for creditCard in current_user.creditCard:
                        if creditCard.user_id == current_user.id and (creditCard.state >= ammount):
                            creditCard.state = creditCard.state - ammount
                        else:
                            new_Transaction.state = 'Odbijeno'
                            db.session.commit()
                            return

                    state.ammount = ammount*conversionRate + state.ammount
                    
                    check=True
                    new_Transaction.state = 'Obradjeno'
                    db.session.commit()
                
            if not check:
                for creditCard in current_user.creditCard:
                        if creditCard.user_id == current_user.id and (creditCard.state >= ammount):
                            creditCard.state = creditCard.state - ammount
                        else:
                            new_Transaction.state = 'Odbijeno'
                            db.session.commit()
                            return
                new_State=State(currency=currency,ammount=ammount*conversionRate,user_id = user.id)
                db.session.add(new_State)
                new_Transaction.state = 'Obradjeno'
                db.session.commit()
        else:  
            new_Transaction.state = 'Odbijeno'
            db.session.commit()
            return


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

        if len(email) < 1:
            flash('Polje email je prazno',category="error")
        elif len(ammount) < 1:
            flash('Polje iznos je prazno',category="error")
        elif email == current_user.email:
            flash('Uneli ste vas email',category="error")
        else:
            flash('Ovo ce da potraje par minuta',category="success")
            thread2 = threading.Thread(target=Thread2,args=(ammount, email, currency, conversionRate))
            thread2.start()
            
    
    return render_template("user_transaction.html", user=current_user,dictionaryCurrency=dictionaryCurrency)
################################################################################################################


@views.route('/unregistered-transactions',methods=['GET','POST'])
@login_required
def unregistered_transactions():
    @copy_current_request_context
    def Thread1(ammount, cardNumber):
                creditCard = CreditCard.query.filter_by(cardNumber=cardNumber).first()
                ammount = float(ammount)

                new_Transaction=Transaction(id=random.randint(0,101),type="unregistered-transaction",state='U obradi',ammount=ammount, user_id=current_user.id, currency="RSD")
                db.session.add(new_Transaction)       
                db.session.commit()
                time.sleep(10)
                if creditCard:
                    for currentCreditCard in current_user.creditCard:
                        if currentCreditCard.user_id == current_user.id and (currentCreditCard.state >= ammount):

                            currentCreditCard.state = currentCreditCard.state - ammount
                            creditCard.state = creditCard.state + ammount
                            print(creditCard.state)
                            
                            new_Transaction.state = 'Obradjeno'
                            db.session.commit()

                        else:
                            new_Transaction.state = 'Odbijeno'
                            db.session.commit()
                else:
                    new_Transaction.state = 'Odbijeno'
                    db.session.commit()

    if request.method =='POST':
        cardNumber = request.form.get('cardNumber')
        ammount = request.form.get("ammount")
        if len(cardNumber) < 1:
            flash('Polje broj kartice je prazno',category="error")
        elif len(ammount) < 1:
            flash('Polje kolicina je prazno',category="error")
        else:
            flash('Ovo ce da potraje par minuta',category="success")
            thread1 = threading.Thread(target=Thread1,args=(ammount,cardNumber))
            thread1.start()
           
            
    
    return render_template("unregistered_transactions.html", user=current_user)
    


@views.route('/transactions',methods=['GET','POST'])
@login_required
def transactions():
    transactions=Transaction.query.filter_by(user_id=current_user.id).all()
    if request.method =='POST':
        sort=request.form.get("sort")
        id=request.form.get("id")
        type=request.form.get("type")
        state=request.form.get("state")
        ammount=request.form.get("ammount")
        currency=request.form.get("currency")
        
        
    
        match sort:
            case "kolicinaOpadajuce":
                transactions=Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.ammount.desc())
            case "kolicinaRastuce":
                transactions=Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.ammount.asc())
            case "idOpadajuce":
                transactions=Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.id.desc())
            case "idRastuce":
                transactions=Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.id.asc())
        

        #transactions=list(transactions)


        if len(id)>=1:
            id=int(id)
            transactions=Transaction.query.filter_by(user_id=current_user.id,id=id)
        if len(type)>=1:
            type=str(type)
            transactions=Transaction.query.filter_by(user_id=current_user.id,type=type)
        if len(state)>=1:
            state=str(state)
            transactions=Transaction.query.filter_by(user_id=current_user.id,state=state)
        if len(ammount)>=1:
            ammount=float(ammount)
            transactions=Transaction.query.filter_by(user_id=current_user.id,ammount=ammount)
        if len(currency)>=1:
            currency=str(currency)
            transactions=Transaction.query.filter_by(user_id=current_user.id,currency=currency)

        
    return render_template("transactions.html", user=current_user, transactions=transactions)