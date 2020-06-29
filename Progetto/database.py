from sqlalchemy import create_engine,MetaData,Table,Column,String,Integer,ForeignKey,DateTime,Float,Boolean,CheckConstraint,select,and_,PrimaryKeyConstraint,bindparam,func,asc,desc, distinct
from datetime import datetime
#from exceptions import EmptyResultException
############################################## Eccezioni definite da me per gestire meglio gli errori
class EmptyResultException(Exception):
    pass

class ResultException(Exception):
    pass
###################################################
engine=create_engine("postgres://enrico:alessandro@localhost:5432/cinema")
metadata=MetaData()
utenti=Table("Utenti",metadata,Column("email",String,primary_key=True)
                              ,Column("nomeUtente",String,nullable=False)
                              ,Column("pwd",String,nullable=False)
                              ,Column("annoNascita",Integer)
                              ,Column("sesso",String,CheckConstraint("sesso='M' OR sesso='F'"))
                              ,Column("provincia",String)
                              ,Column("gestore",Boolean,nullable=False)
                              ,Column("annoAssunzione",Integer))
film=Table("Film",metadata,Column("idFilm",Integer,primary_key=True)
                          ,Column("titolo",String,nullable=False)
                          ,Column("anno",Integer,CheckConstraint("anno>=1970"),nullable=False)
                          ,Column("regista",String,nullable=False)
                          ,Column("minuti",Integer,CheckConstraint("minuti>=1"),nullable=False))
generi=Table("GeneriFilm",metadata,Column("genere",String)
                                  ,Column("film",Integer,ForeignKey("Film.idFilm"),nullable=False)
                                  ,PrimaryKeyConstraint("genere","film"))
sale=Table("Sale",metadata,Column("idSala",Integer,primary_key=True)
                          ,Column("numPosti",Integer,CheckConstraint("\"numPosti\">=10"),nullable=False)
                          ,Column("disponibile",Boolean,nullable=False))
proiezioni=Table("Proiezioni",metadata,Column("idProiezione",Integer,primary_key=True)
                                      ,Column("orario",DateTime,CheckConstraint("orario >= '1970-01-01'::date"),nullable=False)
                                      ,Column("prezzo",Float,CheckConstraint("prezzo>=0.0"),nullable=False)
                                      ,Column("film",Integer,ForeignKey("Film.idFilm"),nullable=False)
                                      ,Column("sala",Integer,ForeignKey("Sale.idSala"),nullable=False))
biglietti=Table("Biglietti",metadata,Column("posto",Integer,CheckConstraint("posto>=0"),nullable=False)
                                    ,Column("proiezione",Integer,ForeignKey("Proiezioni.idProiezione"),nullable=False)
                                    ,Column("cliente",String,ForeignKey("Utenti.email"),nullable=False)
                                    ,PrimaryKeyConstraint("posto","proiezione"))


metadata.create_all(engine)

#conn=engine.connect()
#ins=utenti.insert()
#res=conn.execute(select([utenti]))
#for r in res.fetchall():
#    print(r)
#conn.execute(ins,{"email":"pittinienrico@hotmail.it","nomeUtente":"Enrico","pwd":"tarallo99","annoNascita":1999,"sesso":"M","provincia":"Treviso","gestore":False})
#ins=film.insert()
#conn.execute(ins,[{"idFilm":1,"titolo":"Memento","anno":2000,"regista":"Christopher Nolan","minuti":114},
#                  {"idFilm":2,"titolo":"Inception","anno":2010,"regista":"Christopher Nolan","minuti":148},
#                  {"idFilm":3,"titolo":"Insomnia","anno":2002,"regista":"Christopher Nolan","minuti":118},
#                  {"idFilm":4,"titolo":"The Prestige","anno":2006,"regista":"Christopher Nolan","minuti":130},
#                  {"idFilm":5,"titolo":"Una notte da leoni","anno":2009,"regista":"Todd Phillips","minuti":108},
#                  {"idFilm":6,"titolo":"Una notte da leoni 2","anno":2011,"regista":"Todd Phillips","minuti":102},
#                  {"idFilm":7,"titolo":"Una notte da leoni 3","anno":2013,"regista":"Todd Phillips","minuti":100},
#                  {"idFilm":8,"titolo":"Joker","anno":2019,"regista":"Todd Phillips","minuti":122},
#                  {"idFilm":9,"titolo":"Avatar","anno":2010,"regista":"James Cameron","minuti":162},
#                  {"idFilm":10,"titolo":"Titanic","anno":1997,"regista":"James Cameron","minuti":195},
#                  {"idFilm":11,"titolo":"Avenegers: Infinity War","anno":2018,"regista":"Anthony e Joe Russo","minuti":149},
#                  {"idFilm":12,"titolo":"Avenegers: Endgame","anno":2019,"regista":"Anthony e Joe Russo","minuti":181},
#                  {"idFilm":13,"titolo":"Captain America: Civil War","anno":2016,"regista":"Anthony e Joe Russo","minuti":147},
#                  {"idFilm":14,"titolo":"Shutter Island","anno":2010,"regista":"Martin Scorsese","minuti":138}])
#ins=generi.insert()
#conn.execute(ins,[{"genere":"Drammatico","film":1},
#                  {"genere":"Thriller","film":1},
#                  {"genere":"Giallo","film":1},
#                  {"genere":"Thriller","film":2},
#                  {"genere":"Drammatico","film":2},
#                  {"genere":"Azione","film":3},
#                  {"genere":"Fantascienza","film":3},
#                  {"genere":"Thriller","film":3},
#                  {"genere":"Avventura","film":3},
#                  {"genere":"Thriller","film":4},
#                  {"genere":"Drammatico","film":4},
#                  {"genere":"Fantascienza","film":4},
#                  {"genere":"Commedia","film":5},
#                  {"genere":"Commedia","film":6},
#                  {"genere":"Commedia","film":7},
#                  {"genere":"Drammatico","film":8},
#                  {"genere":"Thriller","film":8},
#                  {"genere":"Noir","film":8},
#                  {"genere":"Fantascienza","film":9},
#                  {"genere":"Azione","film":9},
#                  {"genere":"Avventura","film":9},
#                  {"genere":"Drammatico","film":10},
#                  {"genere":"Sentimentale","film":10},
#                  {"genere":"Storico","film":10},
#                  {"genere":"Azione","film":10},
#                  {"genere":"Catastrofico","film":10},
#                  {"genere":"Fantascienza","film":11},
#                  {"genere":"Azione","film":11},
#                  {"genere":"Avventura","film":11},
#                  {"genere":"Fantascienza","film":12},
#                  {"genere":"Azione","film":12},
#                  {"genere":"Avventura","film":12},
#                  {"genere":"Azione","film":13},
#                  {"genere":"Avventura","film":13},
#                  {"genere":"Thriller","film":14},
#                  {"genere":"Noir","film":14}])
#ins=sale.insert()
#conn.execute(ins,[{"idSala":1,"numPosti":50,"disponibile":True},
#                  {"idSala":2,"numPosti":25,"disponibile":True},
#                  {"idSala":3,"numPosti":25,"disponibile":False},
#                  {"idSala":4,"numPosti":75,"disponibile":True},
#                  {"idSala":5,"numPosti":100,"disponibile":True}])
#ins=proiezioni.insert()
#conn.execute(ins,[#{"orario":datetime(2017,10,4,21,30),"prezzo":9.5,"film":1,"sala":1},
                  #{"orario":datetime(2018,6,17,16,45),"prezzo":10.0,"film":1,"sala":2},
                  #{"orario":datetime(2017,12,7,00,00),"prezzo":8.5,"film":1,"sala":1},
                  #{"orario":datetime(2018,3,24,22,30),"prezzo":9.5,"film":1,"sala":3},
                  #{"orario":datetime(2019,8,14,19,30),"prezzo":9.,"film":2,"sala":3},
                  #{"orario":datetime(2020,10,4,21,30),"prezzo":9.5,"film":2,"sala":4},
                  #{"orario":datetime(2020,7,15,20,15),"prezzo":9.5,"film":2,"sala":4},
                  #{"orario":datetime(2017,10,4,21,30),"prezzo":9.5,"film":2,"sala":5},
                  #{"orario":datetime(2019,4,15,21,30),"prezzo":10.5,"film":2,"sala":1},
                  #{"orario":datetime(2020,6,27,15,30),"prezzo":7.5,"film":3,"sala":2},
                  #{"orario":datetime(2020,11,4,21,30),"prezzo":9.5,"film":3,"sala":5},
                  #{"orario":datetime(2017,1,1,21,30),"prezzo":9.0,"film":3,"sala":5},
                  #{"orario":datetime(2019,5,5,21,30),"prezzo":9.5,"film":4,"sala":4},
                  #{"orario":datetime(2018,5,4,21,30),"prezzo":9.5,"film":4,"sala":3},
                  #{"orario":datetime(2016,5,4,21,30),"prezzo":9.5,"film":4,"sala":2},
                  #{"orario":datetime(2020,4,4,21,30),"prezzo":9.5,"film":4,"sala":1},
                  #{"orario":datetime(2020,7,4,21,30),"prezzo":9.5,"film":5,"sala":1},
                  #{"orario":datetime(2020,7,1,21,30),"prezzo":9.0,"film":5,"sala":2},
                  #{"orario":datetime(2014,10,4,21,30),"prezzo":9.5,"film":5,"sala":3},
                  #{"orario":datetime(2013,10,4,21,30),"prezzo":9.5,"film":5,"sala":3},
                  #{"orario":datetime(2013,11,4,21,30),"prezzo":9.5,"film":5,"sala":4},
                 #### #{"orario":datetime(2017,10,4,21,30),"prezzo":9.5,"film":6,"sala":1},
                  #{"orario":datetime(2017,10,4,21,30),"prezzo":9.5,"film":6,"sala":1},
                  #{"orario":datetime(2017,10,4,21,30),"prezzo":9.5,"film":6,"sala":1},
                  #{"orario":datetime(2017,10,4,21,30),"prezzo":9.5,"film":7,"sala":1},
                  #{"orario":datetime(2017,10,4,21,30),"prezzo":9.5,"film":7,"sala":1},
                  #{"orario":datetime(2017,10,4,21,30),"prezzo":9.5,"film":7,"sala":1},
                  #{"orario":datetime(2017,10,4,21,30),"prezzo":9.5,"film":7,"sala":1},
                  #{"orario":datetime(2017,10,4,21,30),"prezzo":9.5,"film":1,"sala":1},
                  ####{"orario":datetime(2019,4,15,20,30),"prezzo":10.5,"film":2,"sala":1},
                  #{"orario":datetime(2019,5,10,23,30),"prezzo":9.5,"film":6,"sala":2}])


#conn.close()




######################################### Query per login e registrazione

#Ritorna l'utente con questa email
def user_email_query(usr_email):
    conn = engine.connect()
    s=select([utenti]).where(utenti.c.email==bindparam("email"))
    rs = conn.execute(s,email=usr_email)
    user = rs.fetchall()
    conn.close()
    if(len(user)==0): #Errore : risultato vuoto
        raise EmptyResultException
    return user[0]

#Crea un nuovo utente (cliente) con questi dati
def aggiungi_utente_query(email,pwd,nomeUtente,annoNascita,sesso,provincia):
    if("maschio"==sesso):
        sesso="M"
    elif("femmina"==sesso):
        sesso="F"
    else : #Errore
        raise ResultException

    #E' necessaria una transazione, perche' devo effettura in successione una lettura ed una scrittura nel database. L'eventuale concorrenza di questa operazione
    #potrebbe generare problemi (lost update, fantasmi)
    conn=engine.connect()
    trans=conn.begin()
    try:
        s=select([utenti]).where(utenti.c.email==bindparam("eml"))
        res=conn.execute(s,eml=email)
        res=res.fetchall()
        if(len(res)!=0):
            print(len(res))
            raise ResultException
        ins=utenti.insert()
        conn.execute(ins,[{"email":email,"nomeUtente":nomeUtente,"pwd":pwd,"annoNascita":annoNascita,"sesso":sesso,"provincia":provincia,"gestore":False}])
        trans.commit()
        conn.close()
    except: #Errore
        trans.rollback()
        conn.close()
        raise ResultException

#Ritorna i posti comprati dal cliente con questa email. Questi posti sono relativi a proiezioni future
#Oltre ai posti, ritorna anche l'orario,il titolo e la sala della proiezione relativa
def posti_cliente_query(email):
    conn=engine.connect()
    s=select([biglietti.c.posto,proiezioni.c.orario,film.c.titolo,proiezioni.c.sala]).where(and_(biglietti.c.cliente==bindparam("email"),
                proiezioni.c.idProiezione==biglietti.c.proiezione,film.c.idFilm==proiezioni.c.film,proiezioni.c.orario>datetime.now())).order_by(proiezioni.c.orario,biglietti.c.posto)

    res=conn.execute(s,email=email)
    res=res.fetchall()
    return res



############################################# Query ricerca film

def filmGettonati_query():
    conn=engine.connect()
    s=select([film]).where(and_(proiezioni.c.film==film.c.idFilm,proiezioni.c.orario>datetime.now(),
            biglietti.c.proiezione==proiezioni.c.idProiezione)).group_by(film.c.idFilm).order_by(desc(func.count()))
    res=conn.execute(s)
    res=res.fetchall()
    conn.close()
    return res


def filmInProgrammazione_query():
    conn=engine.connect()
    s=select([film]).where(and_(proiezioni.c.film==film.c.idFilm,proiezioni.c.orario>datetime.now())).distinct().order_by(film.c.titolo)
    res=conn.execute(s)
    res=res.fetchall()
    conn.close()
    return res

def proiezioni_giorno_query(date):
    anno=date[0:4]
    mese=date[5:7]
    giorno=date[8:10]
    oraIn=datetime(int(anno),int(mese),int(giorno),0,0)
    oraFin=datetime(int(anno),int(mese),int(giorno),23,59)
    print(oraIn)
    print(oraFin)
    if oraFin<datetime.now():
        raise ResultException

    conn=engine.connect()
    s=select([proiezioni,film.c.titolo,film.c.minuti]).where(and_(proiezioni.c.orario>oraIn,proiezioni.c.orario<oraFin,
                                        film.c.idFilm==proiezioni.c.film)).order_by(proiezioni.c.orario)
    res=conn.execute(s)
    res=res.fetchall()
    conn.close()
    if(len(res)<=0):
        raise EmptyResultException
    return res

#ritorna il titolo del film con questo id
def titolo_film_query(idFilm):
    conn=engine.connect()
    s=select([film.c.titolo]).where(film.c.idFilm==bindparam("film"))
    res=conn.execute(s,film=idFilm)
    res=res.fetchall()
    if(len(res)==0): #Errore : risultato vuoto
        conn.close()
        raise EmptyResultException
    conn.close()
    return res[0]["titolo"]

#ritorna l'orario, il titolo del film, la sala, il prezzo e la durata della proiezione con questo id
def infoProiezione_query(id_proiezione):
    conn=engine.connect()
    s=select([proiezioni.c.orario,film.c.titolo,proiezioni.c.sala,proiezioni.c.prezzo,film.c.minuti]).where(and_(proiezioni.c.idProiezione==bindparam("proiez"),proiezioni.c.film==film.c.idFilm))
    res=conn.execute(s,proiez=id_proiezione)
    res=res.fetchall()
    if(len(res)==0):
        conn.close()
        raise EmptyResultException
    conn.close()
    return res[0]

#Ritorna le proiezioni future del film con id id_film
def proiezioni_film_query(id_film):
    conn=engine.connect()
    s=select([proiezioni]).where(and_(proiezioni.c.film==film.c.idFilm,film.c.idFilm==bindparam('id'),proiezioni.c.orario>datetime.now(),
                sale.c.idSala==proiezioni.c.sala,sale.c.disponibile))
    res=conn.execute(s,id=id_film)
    res=res.fetchall()
    conn.close()
    if(len(res)==0): #Errore : risultato vuoto
        raise EmptyResultException
    return res

#data una stringa titoloFilm ritorna i film che hanno come titolo una stringa che contiene al suo interno titoloFilm (titoloFilm e' sottostringa)
def film_titolo_query(titoloFilm):
    conn=engine.connect()
    s=select([film]).where(film.c.titolo.contains(bindparam('titolo')))
    res=conn.execute(s,titolo=titoloFilm)
    res=res.fetchall()
    conn.close()
    if(len(res)==0): #Errore : risultato vuoto
        raise  EmptyResultException
    return res

#data una lista ritorna una lista senza duplicati
def deleteDup(x):
  return list(dict.fromkeys(x))

#ritorna tutti i generi memorizzati nel database
def generi_query():
    conn=engine.connect()
    res=conn.execute(select([generi.c.genere]))
    list=[x["genere"] for x in res.fetchall()]
    conn.close()
    return deleteDup(list)

#ritorna i film che hanno come genere il genere ricevuto in input (genereFilm)
def film_genere_query(genereFilm):
    conn=engine.connect()
    s=select([film]).where(and_(generi.c.film==film.c.idFilm,generi.c.genere==bindparam('genere')))
    res=conn.execute(s,genere=genereFilm)
    print(res)
    res=res.fetchall()
    print(res)
    conn.close()
    if(len(res)==0): #Errore: risultato vuoto
        raise  EmptyResultException
    return res

#ritorna i posti occupati della proiezione con questo id
def postiOccupati_proiezione_query(id_proiezione):
    conn=engine.connect()
    #controllo che la sala sia ancora disponibile e che la proiezione non sia gia' passata
    s=select([sale.c.disponibile,sale.c.numPosti,proiezioni.c.orario]).where(and_(proiezioni.c.idProiezione==bindparam('id'),sale.c.idSala==proiezioni.c.sala))
    res=conn.execute(s,id=id_proiezione)
    res=res.fetchone()
    if(len(res)==0 or (not res["disponibile"]) or res["orario"]<datetime.now()):
        conn.close()
        raise ResultException

    numPosti=res["numPosti"]

    """s=select([proiezioni.c.orario]).where(proiezioni.c.idProiezione==bindparam('id'))
    res=conn.execute(s,id=id_proiezione)
    res=res.fetchall()
    if(len(res)==0 or res["orario"]<datetime.now()):
        conn.close()
        raise ResultException"""


    #Per ora tutto ok
    #Prendo i posti totali della sala della proiezione
    #s=select([sale.c.numPosti]).where(and_(proiezioni.c.idProiezione==bindparam('id'),sale.c.idSala==proiezioni.c.sala))
    #res=conn.execute(s,id=id_proiezione)
    #postiTotali=res.fetchone()["numPosti"]
    #Prendo i posti gia' acquistati per quella proiezione

    s=select([biglietti.c.posto]).where(biglietti.c.proiezione==bindparam('id'))
    res=conn.execute(s,id=id_proiezione)
    list=res.fetchall()
    if(len(list)>0):
        list=[x["posto"] for x in list]
    #list= [x["posto"] for x in list]
    #list= [x for x in range(0,postiTotali) if x not in list] #creo la lista di posti liberi
    conn.close()
    if(len(list)>=numPosti):
        raise EmptyResultException

    return list

    #Per ora tutto ok
    #Prendo i posti totali della sala della proiezione
    s=select([sale.c.numPosti]).where(and_(proiezioni.c.idProiezione==bindparam('id'),sale.c.idSala==proiezioni.c.sala))
    res=conn.execute(s,id=id_proiezione)
    postiTotali=res.fetchone()["numPosti"]
    #Prendo i posti gia' acquistati per quella proiezione
    s=select([biglietti.c.posto]).where(biglietti.c.proiezione==bindparam('id'))
    res=conn.execute(s,id=id_proiezione)
    list=res.fetchall()
    list= [x["posto"] for x in list]
    list= [x for x in range(0,postiTotali) if x not in list] #creo la lista di posti liberi
    conn.close()
    if(len(list)==0): #Errore: non ci sono posti liberi
        raise EmptyResultException
    return list


#crea un nuovo biglietto, con questo posto (posto), per questa proiezione(id_proiezione) e per questo utente (email)
def compra_biglietto_query(posto,id_proiezione,email):
    #E' necessaria una transazione, perche' devo effettura in successione una lettura ed una scrittura nel database. L'eventuale concorrenza di questa operazione
    #potrebbe generare problemi (lost update, fantasmi)
    conn=engine.connect()
    trans=conn.begin()

    try:
        if(posto in postiOccupati_proiezione_query(id_proiezione)): #Errore : posto gia' acquistato
            raise ResultException
        ins=biglietti.insert()
        conn.execute(ins,[{"posto":posto,"proiezione":id_proiezione,"cliente":email}]) #Creo nuovo biglietto
        trans.commit()
        conn.close()
    except:
        trans.rollback()
        conn.close()
        raise ResultException
