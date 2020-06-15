from flask import Flask,render_template,redirect,url_for,request
from database import *
from flask_login import LoginManager,UserMixin,login_required,login_user,logout_user,current_user

app = Flask(__name__)

class InvalidLoginException(Exception):
    pass

app.config['SECRET_KEY'] = 'ubersecret'
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    # costruttore di classe
    def __init__(self , email , pwd, nomeUtente, annoNascita, sesso, prov, gestore, annoAssunzione):
        self.email = email
        self.pwd = pwd
        self.nomeUtente = nomeUtente
        self.annoNascita = annoNascita
        self.sesso = sesso
        self.prov=prov
        self.gestore=gestore
        self.annoAssunzione=annoAssunzione

    def get_id(self):
        return self.email

    def isGestore(self):
        return self.gestore

@login_manager.user_loader ######### Exception
def load_user(user_email):
    user=user_email_query(user_email)
    return User( user["email"] , user["pwd"],user["nomeUtente"],user["annoNascita"],user["sesso"],user["provincia"],user["gestore"],user["annoAssunzione"])


################################
@app.route("/")
def home():
    if(current_user.is_authenticated):
        return redirect(url_for("private",email=current_user.get_id()))
    return render_template("home.html")

@app.route("/login")
def login():
    if(current_user.is_authenticated):
        return redirect(url_for("private",email=current_user.get_id()))
    return render_template("login.html")

@app.route("/login/Proc",methods=['POST'])
def loginProc():
    try:
        email=request.form["email"]
        pwd=request.form["pwd"]
        usr=user_email_query(email)
        if(usr["pwd"]==pwd):
            user=load_user(email)
            login_user(user)
            return redirect(url_for("private",email=email))
        else:
            raise InvalidLoginException
    except (EmptyResultException,InvalidLoginException):  ##########altra exception
        return render_template("invalidLogin.html")

@app.route("/private/<email>")
@login_required
def private(email):
    try:
        usr=user_email_query(email)
        posti=posti_cliente_query(email)
        if(len(posti)==0):
            return render_template("private.html",nome=usr["nomeUtente"])
        return render_template("private.html",nome=usr["nomeUtente"],posti=posti)
    except EmptyResultException:
        return render_template("invalidLogin.html")

@app.route('/logout')
@login_required # richiede autenticazione
def logout():
    logout_user() # chiamata a flask -login
    return redirect(url_for('home'))

@app.route("/registrazione")
def registrazione():
    if(current_user.is_authenticated):
        return redirect(url_for("private",email=current_user.get_id()))
    return render_template("registrazione.html")

@app.route("/registrazione/Proc",methods=['POST'])
def registrazioneProc():
    email=request.form["email"]
    pwd=request.form["pwd"]
    userName=request.form["userName"]
    prov=request.form["prov"]
    annoNascita=request.form["annoNascita"]
    sesso=request.form["sesso"]
    try:
        aggiungi_utente_query(email,pwd,userName,annoNascita,sesso,prov)
        user=load_user(email)
        login_user(user)
        return redirect(url_for("private",email=email))
    except ResultException,EmptyResultException:  ##########altra exception
        return render_template("invalidRegistration.html")

########################################################################

@app.route("/ricerca")
def ricerca():
    return render_template("ricerca.html")

@app.route("/ricerca/perTitolo")
def ricercaPerTitolo():
    return render_template("ricercaPerTitolo.html")

@app.route("/ricerca/perTitolo/films" , methods=["POST"])
def ricercaPerTitoloFilms():
    titolo = request.form["titolo"]
    try:
        res=film_titolo_query(titolo)
        return render_template("filmRicercati.html",listaFIlm=res,titolo=titolo)
    except EmptyResultException:
        return render_template("erroreRisultato.html",message="La ricerca non ha prodotto alcun risultato")

@app.route("/films/<id_film>")
def mostraProiezioniFilm(id_film):
    try:
        res=proiezioni_film_query(id_film)
        titolo=titolo_film_query(id_film)
        return render_template("proiezioniFilm.html",listaProiezioni=res,film=titolo)
    except EmptyResultException:
        return render_template("erroreRisultato.html",message="Non ci sono proiezioni per questo film")

@app.route("/proiezioni/<id_proiezione>")
def mostraPostiProiezione(id_proiezione):
    if(not current_user.is_authenticated):
        return render_template("nonAutenticato.html")
    try:
        proiezFilm=orarioFilm_proiezione_query(id_proiezione)
        res=postiLiberi_proiezione_query(id_proiezione)
        return render_template("postiProiezione.html",listaPostiLiberi=res,id_pro=id_proiezione,proiezFilm=proiezFilm)
    except EmptyResultException:
        return render_template("erroreRisultato.html",message="Non ci sono posti liberi")
    except ResultException:
        return render_template("erroreRisultato.html",message="La proiezione non e' piu' attualmente disponibile")

@app.route("/proiezioni/<id_proiezione>/<posto>")
@login_required
def confermaAcquistoPosto(id_proiezione,posto):
    try:
        proiezFilm=orarioFilm_proiezione_query(id_proiezione)
        compra_biglietto_query(posto,id_proiezione,current_user.get_id())
        return render_template("acquistoPosto.html",id_pro=id_proiezione,posto=posto,proiezFilm=proiezFilm)
    except (ResultException,EmptyResultException):
        return render_template("erroreRisultato.html",message="Si e' verificato un errore nell'acquistare il posto")


@app.route("/ricerca/perGenere")
def ricercaPerGenere():
    res=generi_query()
    return render_template("ricercaPerGenere.html",listaGeneri=res)

@app.route("/ricerca/perGenere/<genereFilm>")
def ricercaPerGenereFilms(genereFilm):
    try:
        res=film_genere_query(genereFilm)
        return render_template("filmRicercati.html",listaFIlm=res,genere=genereFilm)
    except EmptyResultException:
        return render_template("erroreRisultato.html",message="Non ci sono film con genere "+genereFilm)
