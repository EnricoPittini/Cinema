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
@app.route("/login",methods=["GET",'POST'])
def login():
    if(current_user.is_authenticated): #utente gia' autenticato
        return redirect(url_for("private",email=current_user.get_id()))

    if request.method == "POST": #arrivo dal form di login
        try:
            email=request.form["email"] #email e password digitate dall'utente
            pwd=request.form["pwd"]
            usr=user_email_query(email) #Ritorna l'utente con quell'email
            if(usr["pwd"]==pwd): #Controllo che sia tutto corretto
                user=load_user(email)
                login_user(user)
                return redirect(url_for("private",email=email))
            else:
                raise InvalidLoginException
        except (EmptyResultException,InvalidLoginException):
            return render_template("erroreRisultato.html",message="Errore login",percorsoPrec=request.referrer)
        except:
            return render_template("erroreRisultato.html",message="Oops, qualcosa e' andato storto",percorsoPrec=request.referrer)
    else:
        return render_template("login.html") #form per il login

#route dell'area privata del cliente
@app.route("/private/<email>")
@login_required #Necessaria autenticazione
def private(email):
    try:

        usr=user_email_query(email) #Ritorna l'utente con quell'email
        posti=posti_cliente_query(email) #Ritorna i posti acquistati da questo utente, relativi a proiezioni future
                                         #Oltre ai posti ci sono anche l'orario, il titolo e la sala della proiezione relativa a questi posti
        if(current_user.isGestore()):
            return render_template("privateGestore.html",nome=usr["nomeUtente"])
        if(len(posti)==0):
            return render_template("private.html",nome=usr["nomeUtente"])
        else:
            return render_template("private.html",nome=usr["nomeUtente"],posti=posti)
    except (ResultException,EmptyResultException):
        return render_template("erroreRisultato.html",message="Errore login",percorsoPrec=request.referrer)
    except:
        return render_template("erroreRisultato.html",message="Oops, qualcosa e' andato storto",percorsoPrec=request.referrer)

#route per effettuare il logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

#route per creare un nuovo cliente (registrazione)
@app.route("/registrazione",methods=["GET",'POST'])
def registrazione():
    if(current_user.is_authenticated): #controllo se e' gia' autenticato
        return redirect(url_for("private",email=current_user.get_id()))

    if request.method == "POST": #arrivo dal form
        email=request.form["email"] #dati del form
        pwd=request.form["pwd"]
        userName=request.form["userName"]
        prov=request.form["prov"]
        annoNascita=request.form["annoNascita"]
        sesso=request.form["sesso"]
        try:
            aggiungi_utente_query(email,pwd,userName,annoNascita,sesso,prov) #funzione che crea un nuovo utente (E' un cliente)
            user=load_user(email)
            login_user(user)
            return redirect(url_for("private",email=email)) #reindirizza all'area privata
        except (ResultException,EmptyResultException):
            return render_template("erroreRisultato.html",message="Errore registrazione",percorsoPrec=request.referrer)
        except:
            return render_template("erroreRisultato.html",message="Oops, qualcosa e' andato storto",percorsoPrec=request.referrer)
    else:
        return render_template("registrazione.html")#form di registrazione

############################################################ ROUTES PER LA RICERCA DI FILM

#route principale della ricerca
@app.route("/ricerca")
def ricerca():
    if current_user.is_authenticated and current_user.isGestore(): #controllo che non sia un gestore
        return render_template("erroreRisultato.html",message="Devi essere un cliente per eseguire questa operazione",percorsoPrec=request.referrer)
    filmGettonati=filmGettonati_query() #funzione che ritorna i film ordinati in senso decrescente per numero di biglietti acquistati
    if(len(filmGettonati)>0):
        filmGettonati=filmGettonati[0:5] #5 film piu' gettonati
        return render_template("ricerca.html",filmGettonati=filmGettonati)
    return render_template("ricerca.html")

#route che mostra tutti i film in programmazione
@app.route("/ricerca/inProgrammazione")
def filmInProgrammazione():
    if current_user.is_authenticated and current_user.isGestore(): #controllo che non sia un gestore
        return render_template("erroreRisultato.html",message="Devi essere un cliente per eseguire questa operazione",percorsoPrec=request.referrer)
    films=filmInProgrammazione_query() #funzione che ritorna tutti i film con proiezioni future
    if(len(films)>0):
        return render_template("filmRicercati.html",listaFilm=films)
    return render_template("erroreRisultato.html",message="Non ci sono film in programmazione",percorsoPrec=request.referrer)

#route per la ricerca per giorno
@app.route("/ricerca/perGiorno", methods=["GET","POST"])
def ricercaPerGiorno():
    if current_user.is_authenticated and current_user.isGestore(): #controllo che non sia un gestore
        return render_template("erroreRisultato.html",message="Devi essere un cliente per eseguire questa operazione",percorsoPrec=request.referrer)

    if request.method == "POST": #arriva dal form
        orario = request.form["orario"] #orario di input dell'utente
        try:
            res=proiezioni_giorno_query(orario) #funzione che ritorna le proiezioni in questo giorno
            return render_template("proiezioniFilm.html",listaProiezioni=res)
        except (ResultException,EmptyResultException):
            return render_template("erroreRisultato.html",message="La ricerca non ha prodotto alcun risultato",percorsoPrec=request.referrer)
        except:
            return render_template("erroreRisultato.html",message="Oops, qualcosa e' andato storto",percorsoPrec=request.referrer)
    else:
        return render_template("ricercaPerGiorno.html") #pagina con il form

#route per la ricerca per titolo
@app.route("/ricerca/perTitolo" , methods=["GET","POST"])
def ricercaPerTitoloFilms():
    if current_user.is_authenticated and current_user.isGestore(): #controllo che non sia un gestore
        return render_template("erroreRisultato.html",message="Devi essere un cliente per eseguire questa operazione",percorsoPrec=request.referrer)

    if request.method == "POST": #form
        titolo = request.form["titolo"] #titolo di input dell'utente
        try:
            res=film_titolo_query(titolo) #funzione che ritorna i film con quel titolo
            return render_template("filmRicercati.html",listaFilm=res,titolo=titolo,percorsoPrec="/ricerca/perTitolo")
        except EmptyResultException:
            return render_template("erroreRisultato.html",message="La ricerca non ha prodotto alcun risultato",percorsoPrec=request.referrer)
        except:
            return render_template("erroreRisultato.html",message="Oops, qualcosa e' andato storto",percorsoPrec=request.referrer)
    else:
        return render_template("ricercaPerTitolo.html") #pagina con il form

#route per ricercare film per genere
@app.route("/ricerca/perGenere")
def ricercaPerGenere():
    if current_user.is_authenticated and current_user.isGestore(): #controlla che non sia un gestore
        return render_template("erroreRisultato.html",message="Devi essere un cliente per eseguire questa operazione",percorsoPrec=request.referrer)
    res=generi_query() #funzione che ritorna tutti i possibili generi
    return render_template("ricercaPerGenere.html",listaGeneri=res)

#route dove si mostrano i film con quel genere
@app.route("/ricerca/perGenere/<genereFilm>")
def ricercaPerGenereFilms(genereFilm):
    if current_user.is_authenticated and current_user.isGestore(): #controlla che non sia un gestore
        return render_template("erroreRisultato.html",message="Devi essere un cliente per eseguire questa operazione",percorsoPrec=request.referrer)
    try:
        res=film_genere_query(genereFilm) #funzione che ritorna tutti i film con quel genere
        return render_template("filmRicercati.html",listaFilm=res,genere=genereFilm,percorsoPrec="/ricerca/perGenere")
    except ResultException,EmptyResultException:
        return render_template("erroreRisultato.html",message="Non ci sono film con genere "+genereFilm,percorsoPrec=request.referrer)
    except:
        return render_template("erroreRisultato.html",message="Oops, qualcosa e' andato storto",percorsoPrec=request.referrer)

#route dove si mostrano le proiezioni future del film selezionato
#In questa route si arriva sia dalla ricerca per tutti i film in programmazione sia dalla ricerca per titolo sia dalla ricerca per genere
@app.route("/films/<id_film>")
def mostraProiezioniFilm(id_film):
    if current_user.is_authenticated and current_user.isGestore(): #controlla che non sia un gestore
        return render_template("erroreRisultato.html",message="Devi essere un cliente per eseguire questa operazione",percorsoPrec=request.referrer)
    try:
        res=proiezioni_film_query(id_film) #funzione che ritorna la lista di proiezioni future di quel film

        return render_template("proiezioniFilm.html",listaProiezioni=res)
    except (ResultException,EmptyResultException):
        return render_template("erroreRisultato.html",message="Non ci sono proiezioni per questo film",percorsoPrec=request.referrer)
    except:
        return render_template("erroreRisultato.html",message="Oops, qualcosa e' andato storto",percorsoPrec=request.referrer)

#route dove si mostrano i posti liberi della proiezione selezionata
@app.route("/proiezioni/<id_proiezione>")
def mostraPostiProiezione(id_proiezione):
    if(not current_user.is_authenticated): #Se e' un utente anonimo, si obbliga ad autenticarsi
        return render_template("nonAutenticato.html")
    elif( current_user.isGestore()): #controllo che non sia un gestore
        return render_template("erroreRisultato.html",message="Devi essere un cliente per eseguire questa operazione",percorsoPrec=request.referrer)
    try:
        proiezFilm=infoProiezione_query(id_proiezione) #funzione che ritorna il titolo, l'orario , la sala , la durata e il prezzo di questa proiezione
                                                        #Sono tutti dati che mi servono per mostrarli nella pagina html

        res=postiOccupati_proiezione_query(id_proiezione) #ritorna la lista di posti occupati di questa proiezione
        numPosti,numFile=numPostiFile_salaProiezione_query(id_proiezione) #numPosti e numFile della sala della proiezione
        res=[x for x in range(0,numPosti) if x not in res] #costruisco la lista di posti liberi dalla lista di posti occupati
        return render_template("postiProiezione.html",listaPostiLiberi=res,id_pro=id_proiezione,proiezFilm=proiezFilm,f=numFile,c=numPosti/numFile,percorsoPrec=url_for("mostraProiezioniFilm",id_film=proiezFilm["idFilm"]))
    except EmptyResultException:
        return render_template("erroreRisultato.html",message="Non ci sono posti liberi",percorsoPrec=request.referrer)
    except ResultException:
        return render_template("erroreRisultato.html",message="La proiezione non e' attualmente disponibile",percorsoPrec=request.referrer)
    except:
        return render_template("erroreRisultato.html",message="Oops, qualcosa e' andato storto",percorsoPrec=request.referrer)

#route dove si effettua l'acquisto del posto selezionato
@app.route("/proiezioni/<id_proiezione>/<posto>")
@login_required #necessaria autenticazione
def confermaAcquistoPosto(id_proiezione,posto):
    if current_user.isGestore(): #controllo che non sia un gestore
        return render_template("erroreRisultato.html",message="Devi essere un cliente per eseguire questa operazione",percorsoPrec=request.referrer)
    try:
        proiezFilm=infoProiezione_query(id_proiezione) #funzione che ritorna il titolo, l'orario e la sala di questa proiezione
                                                             #Sono tutti dati che mi servono per mostrarli nella pagina html

        compra_biglietto_query(posto,id_proiezione,current_user.get_id()) #funzione che crea un nuovo biglietto, con quel posto per quella proiezione e per quell'utente
        return render_template("acquistoPosto.html",id_pro=id_proiezione,posto=posto,proiezFilm=proiezFilm)
    except (ResultException,EmptyResultException):
        return render_template("erroreRisultato.html",message="Si e' verificato un errore nell'acquistare il posto",percorsoPrec=request.referrer)
    except:
        return render_template("erroreRisultato.html",message="Oops, qualcosa e' andato storto",percorsoPrec=request.referrer)

########################################################################
#PARTE gestore
########################################################################

################### STATISTICHE

#route dove si mostrano le varie tipologie di statistiche
@app.route("/statistiche")
@login_required
def statistiche():
    return render_template("statistiche.html")

#route interna a statistiche, dove si puo effettuare la ricerca per titolo
@app.route("/statistiche/perTitolo",methods=['GET','POST'])
@login_required
def statisticheTitolo():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione",percorsoPrec=request.referrer)
    else:
        if(request.method == 'POST'):
            try:
                res=statisticheTitolo_query(request.form["titolo"])
                return render_template("risultatoStatistiche.html",titolo=request.form["titolo"],stats=res,films=film_statistiche_query(request.form["titolo"]),percorso=0,descrizione="titolo")
            except EmptyResultException:
                return render_template("erroreRisultato.html",message="Non ci sono film con il nome digitato o simili",percorsoPrec=request.referrer)
        else:
            return render_template("statistichePerTitolo.html")

#route interna a statistiche, dove si puo effettuare la ricerca scegliendo un genere
@app.route("/statistiche/perGenere",methods=['GET','POST'])
@login_required
def statisticheGenere():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione",percorsoPrec=request.referrer)
    else:
        try:
            if(request.method == 'POST'):
                res=statisticheGenere_query(request.form["genere"])
                return render_template("risultatoStatistiche.html",genere=request.form["genere"],stats=res,films=generi_statistiche_query(request.form["genere"]),percorso=1,descrizione="genere")
        except EmptyResultException:
            return render_template("erroreRisultato.html",message="Non ci sono film con il genere selezionato",percorsoPrec=request.referrer)
        else:
            return render_template("statistichePerGenere.html",generi=generi_query())

#route interna a statistiche, dove si puo effettuare la ricerca scegliendo una provincia
@app.route("/statistiche/perProvincia",methods=['GET','POST'])
@login_required
def statisticheProvincia():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione",percorsoPrec=request.referrer)
    else:
        if(request.method == 'POST'):
            try:
                res=statisticheProvincia_query(request.form["provincia"])
                return render_template("risultatoStatistiche.html",provincia=request.form["provincia"],stats=res,utenti=utenti_province_query(request.form["provincia"]),percorso=2,descrizione="provincia")
            except EmptyResultException:
                return render_template("erroreRisultato.html",message="Non esistono utenti appartenenti a questa provincia",percorsoPrec=request.referrer)
        else:
            return render_template("statistichePerProvincia.html",province=province_query())

################### CREA GESTORE

#route in cui viene effettuata la creazione di un gestore
@app.route("/creaGestore",methods=['GET','POST'])
@login_required
def creaGestore():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione",percorsoPrec=request.referrer)
    else:
        if(request.method == 'POST'):
            try:
                email=request.form["email"]
                pwd=request.form["pwd"]
                userName=request.form["userName"]
                prov=request.form["prov"]
                annoNascita=request.form["annoNascita"]
                sesso=request.form["sesso"]
                #richiamo la funzione definita in database.py per la crazione dell'utente gestore
                aggiungi_utente_gestore_query(email,pwd,userName,annoNascita,sesso,prov)
                return render_template("registrazioneGestore.html",utente=request.form["userName"])
            except ResultException:
                return render_template("erroreRisultato.html",message="Non e' stato possibile creare un account gestore con queste credenziali.",percorsoPrec=request.referrer)
        else:
            return render_template("registrazioneGestore.html")

################### AMMINISTRA

#route in cui vengono mostrate tutte le operazioni che puo svolgere un amministratore sul db
@app.route("/amministra")
@login_required
def amministra():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione",percorsoPrec=request.referrer)
    else:
        return render_template("amministra.html")

#route che permette la creazione di film all'interno del db
@app.route("/creaFilm",methods=['GET','POST'])
@login_required
def creaFilm():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione",percorsoPrec=request.referrer)
    else:
        generi=["Animazione","Avventura","Azione","Biografico","Catastrofico","Commedia","Documentario","Drammatico","Giallo","Pornografico","Erotico","Fantascienza","Fantasy","Guerra","Horror","Musical","Noir","Sentimentale","Storico","Thriller","Western"]
        if(request.method == 'POST'):
            try:
                titolo=request.form["titolo"]
                anno=request.form["anno"]
                regista=request.form["regista"]
                minuti=request.form["minuti"]
                if(minuti<1 or anno<1970):
                    return render_template("erroreRisultato.html",message="La durata di un film deve essere maggiore o uguale a 1 e l'anno deve essere maggiore di 1970.",percorsoPrec=request.referrer)
                else:
                    genere=request.form.getlist('generi')
                    aggiungi_film_query(titolo,anno,regista,genere,minuti)
                    return render_template("creaFilm.html",genere=generi,titolo=titolo)
            except ResultException:
                return render_template("erroreRisultato.html",message="Non e' stato possibile inserire un film con questi valori",percorsoPrec=request.referrer)
        else:
            return render_template("creaFilm.html",genere=generi)

#route che permette la creazione di una sala, stabilendo posti e numero di file
@app.route("/creaSala",methods=['GET','POST'])
@login_required
def creaSala():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione",percorsoPrec=request.referrer)
    else:
        if(request.method == 'POST'):
            try:
                posti=request.form["posti"]
                file=request.form["file"]
                #se i valori di nposti o nfile sono <0 allora ritorno un'eccezione
                if(int(posti)<10 or (int(file)<1) or (int(posti)%int(file)!=0)):
                    return render_template("erroreRisultato.html",message="Creare una sala a queste condizioni: numero dei posti>0, numero delle file>1 e posti%file deve essere 0",percorsoPrec=request.referrer)
                else:
                    nsala=aggiungi_sala_query(posti,file)
                    return render_template("creaSala.html",nsala=nsala,method="POST")
            except ResultException:
                return render_template("erroreRisultato.html",message="Non e' stato possibile inserire una sala con questi valori",percorsoPrec=request.referrer)
        else:
            return render_template("creaSala.html")

#route nella quale vengono mostrate tutte le sale, con le relative disponibilita attuali
@app.route("/gestisciSala",methods=['GET','POST'])
@login_required
def gestisciSala():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione",percorsoPrec=request.referrer)
    else:
        if(request.method == 'POST'):
            #creazione lista sale disponibili
            list=[int(i) for i in request.form.getlist("mycheckbox")]
            gestisci_sale_query(list)
            return render_template("gestisciSale.html",sale=sale_query(),listasaledisponibili=list)
        else:
            sale=sale_query()
            return render_template("gestisciSale.html",sale=sale_query())

#route per aggiungere una proiezione, specificando un giorno e un'ora
@app.route("/aggiungiProiezione",methods=['GET','POST'])
@login_required
def aggiungiProiezione():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione",percorsoPrec=request.referrer)
    else:
        if(request.method == 'POST'):
            try:
                film=request.form["film"]
                sala=request.form["sale"]
                orario=request.form["orario"]
                prezzo=request.form["prezzo"]
                listafilm=aggiungi_proiezione_query(film,sala,orario,prezzo)
                if(listafilm is not None and len(listafilm)>0):
                    return render_template("erroreRisultato.html",message="Impossibile completare l'operazione: proiezioni gia' presenti durante lo stesso orario.",percorsoPrec=request.referrer)
                else:
                    titolo=titolo_film_query(film)
                    return render_template("aggiungiProiezione.html",listafilm=film_query(),listasale=sale_disponibili_query(),film=titolo,sala=sala,orario=orario)
            except ResultException:
                return render_template("erroreRisultato.html",message="Impossibile effettuare l'operazione al momento",percorsoPrec=request.referrer)
        else:
            return render_template("aggiungiProiezione.html",listafilm=film_query(),listasale=sale_disponibili_query())

#route per eliminare le proieioni future delle sale dispinibili
@app.route("/eliminaProiezioneFutura",methods=['GET','POST'])
@login_required
def eliminaProiezioneFutura():
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione",percorsoPrec=request.referrer)
    else:
        if(request.method == 'POST'):
            return render_template("eliminaProiezione.html",proiezioni=proiezioni_future_query())
        return render_template("eliminaProiezione.html",proiezioni=proiezioni_future_query())

#route che prende un parametro 'proiezione' ed effettua l'eliminazione di quella proiezione e dei relativi biglietti associati
@app.route("/eliminaProiezioneFutura/<proiezione>")
def eliminaProiezioneFuturaProc(proiezione):
    if current_user.isGestore() is False:
        return render_template("erroreRisultato.html",message="Devi essere un gestore per eseguire questa operazione",percorsoPrec=request.referrer)
    else:
        delete_proiezione_query(proiezione)
        return redirect(url_for("eliminaProiezioneFutura"))
