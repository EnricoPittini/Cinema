from flask import Flask,render_template,redirect,url_for,request
from database import *
from flask_login import LoginManager,UserMixin,login_required,login_user,logout_user,current_user

app = Flask(__name__)

class InvalidLoginException(Exception):#Eccezione definite da me per gestire meglio gli errori
    pass

app.run(debug=True)
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

#route per il login dell'utente
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
    except (EmptyResultException,InvalidLoginException):  ##########altra exception
        return render_template("invalidLogin.html")

#route dell'area privata del cliente
@app.route("/private/<email>")
@login_required
def private(email):
    try:
        usr=user_email_query(email) #Ritorna l'utente con quell'email
        posti=posti_cliente_query(email) #Ritorna i posti acquistati da questo utente, relativi a proiezioni future
                                         #Oltre ai posti ci sono anche l'orario, il titolo , la sala e la durata della proiezione relativa a questi posti
        print(posti)
        if(current_user.isGestore()):
            return render_template("privateGestore.html",nome=usr["nomeUtente"])
        elif(len(posti)==0):
            return render_template("private.html",nome=usr["nomeUtente"])
        else:
            return render_template("private.html",nome=usr["nomeUtente"],posti=posti)
    except EmptyResultException:
        return render_template("invalidLogin.html")

#route per effettuare il logout
@app.route('/logout')
@login_required # richiede autenticazione
def logout():
    logout_user() # chiamata a flask -login
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
        aggiungi_utente_query(email,pwd,userName,annoNascita,sesso,prov) #funzione che crea un nuovo utente (E' un cliente)
        user=load_user(email)
        login_user(user)
        return redirect(url_for("private",email=email))
    except (ResultException,EmptyResultException):   ##########altra exception
        return render_template("invalidRegistration.html")

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
    except EmptyResultException:
        return render_template("erroreRisultato.html",message="La ricerca non ha prodotto alcun risultato",percorsoPrec=request.path)

#route dove si mostrano le proiezioni future del film selezionato
#In questa route si arriva sia dalla ricerca per titolo che dalla ricerca per genere (e' il punto di incontro)
@app.route("/films/<id_film>")
def mostraProiezioniFilm(id_film):
    try:
        res=proiezioni_film_query(id_film) #funzione che ritorna la lista di proiezioni future di quel film
        #titolo=titolo_film_query(id_film) #funzione che ritorna il titolo del film. Cio' serve per mostrarlo nella pagina html
        return render_template("proiezioniFilm.html",listaProiezioni=res,titolo=res[0]["titolo"],durata=res[0]["minuti"])
    except EmptyResultException:
        return render_template("erroreRisultato.html",message="Non ci sono proiezioni per questo film",percorsoPrec=request.path)

#route dove si mostrano i posti liberi della proiezione selezionata
@app.route("/proiezioni/<id_proiezione>")
def mostraPostiProiezione(id_proiezione):
    if(not current_user.is_authenticated):
        return render_template("nonAutenticato.html")
    try:
        proiezFilm=infoProiezione_query(id_proiezione) #funzione che ritorna il titolo, l'orario e la sala di questa proiezione
                                                              #Sono tutti dati che mi servono per mostrarli nella pagina html
        res=postiLiberi_proiezione_query(id_proiezione) #ritorna la lista di posti occupati di questa proiezione
        numPosti,numFile=numPostiFile_salaProiezione_query(id_proiezione)
        print(numPosti,numFile)
        #res=[x for x in res]
        res=[x for x in range(0,numPosti) if x not in res]
        print(numFile,numPosti/numFile)
        return render_template("postiProiezione.html",listaPostiLiberi=res,id_pro=id_proiezione,proiezFilm=proiezFilm,f=numFile,c=numPosti/numFile)
    except EmptyResultException:
        return render_template("erroreRisultato.html",message="Non ci sono posti liberi",percorsoPrec=request.path)
    except ResultException:
        return render_template("erroreRisultato.html",message="La proiezione non e' attualmente disponibile",percorsoPrec=request.path)

#route dove si effettua l'acquisto del posto selezionato
@app.route("/proiezioni/<id_proiezione>/<posto>")
@login_required
def confermaAcquistoPosto(id_proiezione,posto):
    try:
        proiezFilm=infoProiezione_query(id_proiezione) #funzione che ritorna il titolo, l'orario e la sala di questa proiezione
                                                              #Sono tutti dati che mi servono per mostrarli nella pagina html
        compra_biglietto_query(posto,id_proiezione,current_user.get_id()) #funzione che crea un nuovo biglietto, con quel posto per quella proiezione e per quell'utente
        return render_template("acquistoPosto.html",id_pro=id_proiezione,posto=posto,proiezFilm=proiezFilm)
    except (ResultException,EmptyResultException):
        return render_template("erroreRisultato.html",message="Si e' verificato un errore nell'acquistare il posto",percorsoPrec=request.path)

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
    except EmptyResultException:
        return render_template("erroreRisultato.html",message="Non ci sono film con genere "+genereFilm,percorsoPrec=request.path)

########################################################################
#PARTE gestore
########################################################################

@app.route("/statistiche")
@login_required
def statistiche():
    return render_template("statistiche.html")

@app.route("/statistiche/perTitolo",methods=['GET','POST'])
@login_required
def statisticheTitolo():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione")
    else:
        if(request.method == 'POST'):
            try:
                res=statisticheTitolo_query(request.form["titolo"])
                return render_template("risultatoStatistiche.html",titolo=request.form["titolo"],stats=res,films=film_statistiche_query(request.form["titolo"]),percorso=0,descrizione="titolo")
            except EmptyResultException:
                return render_template("erroreRisultato.html",message="Non ci sono film con il nome digitato o simili")
        else:
            return render_template("statistichePerTitolo.html")

@app.route("/statistiche/perGenere",methods=['GET','POST'])
@login_required
def statisticheGenere():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione")
    else:
        try:
            if(request.method == 'POST'):
                res=statisticheGenere_query(request.form["genere"])
                return render_template("risultatoStatistiche.html",genere=request.form["genere"],stats=res,films=generi_statistiche_query(request.form["genere"]),percorso=1,descrizione="genere")
        except EmptyResultException:
            return render_template("erroreRisultato.html",message="Non ci sono film con il genere selezionato")
        else:
            return render_template("statistichePerGenere.html",generi=generi_query())

@app.route("/statistiche/perProvincia",methods=['GET','POST'])
@login_required
def statisticheProvincia():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione")
    else:
        if(request.method == 'POST'):
            try:
                res=statisticheProvincia_query(request.form["provincia"])
                return render_template("risultatoStatistiche.html",provincia=request.form["provincia"],stats=res,utenti=utenti_province_query(request.form["provincia"]),percorso=2,descrizione="provincia")
            except EmptyResultException:
                return render_template("erroreRisultato.html",message="Non esistono utenti appartenenti a questa provincia")
        else:
            return render_template("statistichePerProvincia.html",province=province_query())

@app.route("/creaGestore",methods=['GET','POST'])
@login_required
def creaGestore():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione")
    else:
        if(request.method == 'POST'):
            try:
                email=request.form["email"]
                pwd=request.form["pwd"]
                userName=request.form["userName"]
                prov=request.form["prov"]
                annoNascita=request.form["annoNascita"]
                sesso=request.form["sesso"]
                aggiungi_utente_gestore_query(email,pwd,userName,annoNascita,sesso,prov)
                return render_template("registrazione.html")
            except ResultException:
                return render_template("erroreRisultato.html",message="Non e' stato possibile creare un account gestore")
        else:
            return render_template("registrazione.html")

@app.route("/amministra")
@login_required
def amministra():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione")
    else:
        return render_template("amministra.html")

@app.route("/creaFilm",methods=['GET','POST'])
@login_required
def creaFilm():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione")
    else:
        if(request.method == 'POST'):
            try:
                titolo=request.form["titolo"]
                anno=request.form["anno"]
                regista=request.form["regista"]
                minuti=request.form["minuti"]
                genere=request.form.getlist('generi')
                aggiungi_film_query(titolo,anno,regista,genere,minuti)
                return render_template("creaFilm.html",genere=generi_query(),titolo=titolo)
            except ResultException:
                return render_template("erroreRisultato.html",message="Non e' stato possibile inserire un film con questi valori")
        else:
            return render_template("creaFilm.html",genere=generi_query())

@app.route("/creaSala",methods=['GET','POST'])
@login_required
def creaSala():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione")
    else:
        if(request.method == 'POST'):
            posti=request.form["posti"]
            nsala=aggiungi_sala_query(posti)
            return render_template("creaSala.html",nsala=nsala,method="POST")
        else:
            return render_template("creaSala.html")


@app.route("/gestisciSala",methods=['GET','POST'])
@login_required
def gestisciSala():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione")
    else:
        if(request.method == 'POST'):
            #creazione lista sale disponibili
            list=[int(i) for i in request.form.getlist("mycheckbox")]
            gestisci_sale_query(list)
            return render_template("gestisciSale.html",sale=sale_query())
        else:
            sale=sale_query()
            return render_template("gestisciSale.html",sale=sale_query())

@app.route("/aggiungiProiezione",methods=['GET','POST'])
@login_required
def aggiungiProiezione():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione")
    else:
        if(request.method == 'POST'):
            try:
                film=request.form["film"]
                sala=request.form["sale"]
                orario=request.form["orario"]
                prezzo=request.form["prezzo"]
                aggiungi_proiezione_query(film,sala,orario,prezzo)
                return render_template("aggiungiProiezione.html",listafilm=film_query(),listasale=sale_query())
            except ResultException:
                return render_template("erroreRisultato.html",message="Non e' stato possibile inserire una proiezione con questi valori")
        else:
            return render_template("aggiungiProiezione.html",listafilm=film_query(),listasale=sale_query())

@app.route("/eliminaProiezioneFutura")
@login_required
def eliminaProiezioneFutura():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione")
    else:
        return render_template("eliminaProiezione.html",proiezioni=proiezioni_future_query())

@app.route("/eliminaProiezioneFutura/<proiezione>")
def eliminaProiezioneFuturaProc(proiezione):
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione")
    else:
        delete_proiezione_query(proiezione)
        return url_for("eliminaProiezioneFutura")
