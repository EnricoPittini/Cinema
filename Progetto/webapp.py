from flask import Flask,render_template,redirect,url_for,request
from database import *
from flask_login import LoginManager,UserMixin,login_required,login_user,logout_user,current_user

app = Flask(__name__)

class InvalidLoginException(Exception): #Eccezione definite da me per gestire meglio gli errori
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

    #override del metodo che ritorna l'id dell'utente
    def get_id(self):
        return self.email

    #metodo che ritorna True se l'utente e' un gestore, False altrimenti
    def isGestore(self):
        return self.gestore

@login_manager.user_loader ######### Exception
def load_user(user_email):
    user=user_email_query(user_email)
    return User( user["email"] , user["pwd"],user["nomeUtente"],user["annoNascita"],user["sesso"],user["provincia"],user["gestore"],user["annoAssunzione"])


####################################### ROUTES PER ACCEDERE O PER CREARE NUOVO ACCOUNT

#route principale
@app.route("/")
def home():
    if(current_user.is_authenticated):
        return redirect(url_for("private",email=current_user.get_id()))
    return render_template("home.html")

#route per il login dell'utente
@app.route("/login")
def login():
    if(current_user.is_authenticated):
        return redirect(url_for("private",email=current_user.get_id()))
    return render_template("login.html")

#route per elaborare i dati del login
@app.route("/login/Proc",methods=['POST'])
def loginProc():
    try:
        email=request.form["email"]
        pwd=request.form["pwd"]
        usr=user_email_query(email) #Ritorna l'utente con quell'email
        if(usr["pwd"]==pwd):
            user=load_user(email)
            login_user(user)
            return redirect(url_for("private",email=email))
        else:
            raise InvalidLoginException
    except (EmptyResultException,InvalidLoginException):
        return render_template("erroreRisultato.html",message="email o password non corrette!")

#route dell'area privata del cliente
@app.route("/private/<email>")
@login_required
def private(email):
    try:
        usr=user_email_query(email) #Ritorna l'utente con quell'email

        posti=posti_cliente_query(email) #Ritorna i posti acquistati da questo utente, relativi a proiezioni future

        if(len(posti)==0):
            return render_template("private.html",nome=usr["nomeUtente"])
        return render_template("private.html",nome=usr["nomeUtente"],posti=posti)
    except (ResultException,EmptyResultException):
        return render_template("erroreRisultato.html",message="email o password non corrette!")

#route per effettuare il logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

#route per creare un nuovo cliente
@app.route("/registrazione")
def registrazione():
    if(current_user.is_authenticated):
        return redirect(url_for("private",email=current_user.get_id()))
    return render_template("registrazione.html")

#route per elaborare i dati del form di registrazione
@app.route("/registrazione/Proc",methods=['POST'])
def registrazioneProc():
    email=request.form["email"]
    pwd=request.form["pwd"]
    userName=request.form["userName"]
    prov=request.form["prov"]
    annoNascita=request.form["annoNascita"]
    sesso=request.form["sesso"]
    try:
        aggiungi_utente_query(email,pwd,userName,annoNascita,sesso,prov)#funzione che crea un nuovo utente (E' un cliente)
        user=load_user(email)
        login_user(user)
        return redirect(url_for("private",email=email))
    except (ResultException,EmptyResultException):  ##########altra exception
        return render_template("erroreRisultato.html",message="i dati inseriti non sono corretti!")


############################################################ROUTES PER LA RICERCA DI FILM

#route principale della ricerca
@app.route("/ricerca")
def ricerca():
    return render_template("ricerca.html")

#route per ricercare un film tramite titolo
@app.route("/ricerca/perTitolo")
def ricercaPerTitolo():
    return render_template("ricercaPerTitolo.html")

#route dove si mostrano i film trovati con quel titolo
@app.route("/ricerca/perTitolo/films" , methods=["POST"])
def ricercaPerTitoloFilms():
    titolo = request.form["titolo"]
    try:
        res=film_titolo_query(titolo) #funzione che ritorna i film con quel titolo
        return render_template("filmRicercati.html",listaFIlm=res,titolo=titolo)
    except (ResultException,EmptyResultException):
        return render_template("erroreRisultato.html",message="La ricerca non ha prodotto alcun risultato")

#route per ricercare film per genere
@app.route("/ricerca/perGenere")
def ricercaPerGenere():
    res=generi_query() #funzione che ritorna tutti i possibili generi
    return render_template("ricercaPerGenere.html",listaGeneri=res)

#route dove si mostrano i film con quel genere
@app.route("/ricerca/perGenere/<genereFilm>")
def ricercaPerGenereFilms(genereFilm):
    try:
        res=film_genere_query(genereFilm) #funzione che ritorna tutti i film con quel genere
        return render_template("filmRicercati.html",listaFIlm=res,genere=genereFilm)
    except (ResultException,EmptyResultException):
        return render_template("erroreRisultato.html",message="Non ci sono film con genere "+genereFilm)


#route dove si mostrano le proiezioni future del film selezionato
#In questa route si arriva sia dalla ricerca per titolo che dalla ricerca per genere (e' il punto di incontro)
@app.route("/films/<id_film>")
def mostraProiezioniFilm(id_film):
    try:
        res=proiezioni_film_query(id_film) #funzione che ritorna la lista di proiezioni future di quel film

        titolo=titolo_film_query(id_film) #funzione che ritorna il titolo del film. Cio' serve per mostrarlo nella pagina html

        return render_template("proiezioniFilm.html",listaProiezioni=res,film=titolo)
    except (ResultException,EmptyResultException):
        return render_template("erroreRisultato.html",message="Non ci sono proiezioni per questo film")

#route dove si mostrano i posti liberi della proiezione selezionata
@app.route("/proiezioni/<id_proiezione>")
def mostraPostiProiezione(id_proiezione):
    if(not current_user.is_authenticated):
        return render_template("nonAutenticato.html")
    try:
        proiezFilm=orarioFilm_proiezione_query(id_proiezione) #funzione che ritorna il titolo, l'orario e la sala di questa proiezione
                                                              #Sono tutti dati che mi servono per mostrarli nella pagina html

        res=postiLiberi_proiezione_query(id_proiezione) #ritorna la lista di posti liberi di questa proiezione

        return render_template("postiProiezione.html",listaPostiLiberi=res,id_pro=id_proiezione,proiezFilm=proiezFilm)
    except EmptyResultException:
        return render_template("erroreRisultato.html",message="Non ci sono posti liberi")
    except ResultException:
        return render_template("erroreRisultato.html",message="La proiezione non e' piu' attualmente disponibile")

#route dove si effettua l'acquisto del posto selezionato
@app.route("/proiezioni/<id_proiezione>/<posto>")
@login_required
def confermaAcquistoPosto(id_proiezione,posto):
    try:
        proiezFilm=orarioFilm_proiezione_query(id_proiezione) #funzione che ritorna il titolo, l'orario e la sala di questa proiezione
                                                              #Sono tutti dati che mi servono per mostrarli nella pagina html

        compra_biglietto_query(posto,id_proiezione,current_user.get_id()) #funzione che crea un nuovo biglietto, con quel posto per quella proiezione e per quell'utente

        return render_template("acquistoPosto.html",id_pro=id_proiezione,posto=posto,proiezFilm=proiezFilm)
    except (ResultException,EmptyResultException):
        return render_template("erroreRisultato.html",message="Si e' verificato un errore nell'acquistare il posto")
