# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
import requests
import  os, sys, re, time, random, hashlib, platform, socket
from pymongo import MongoClient #pip install pymongo
import pymongo
from datetime import datetime
from datetime import timedelta

#import pour graph et stat
from bson.code import Code
import plotly #pip install plotly
import xlwt #pip install xlwt

#import pour la fonction counter
from collections import Counter

#import pour selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.support.ui import Select


#Fonction pour option 1,2 et 3
def hasher(data):
    """ Calculates the hash of the data using sha256. It is returned in HEX formatting."""
    """fonction de hashage: sha256"""
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def ipPublic():
    """Fonction qui recupere l'IP publique de l'observateur"""
    ip = socket.gethostbyname(socket.gethostname()) #!!! seulement sur Windows
    if ip == "127.0.0.1": #pour UNIX
        import commands
        output = commands.getoutput("/sbin/ifconfig")
        ip = parseaddress(output)
    return ip


def observer(cookies):
    """Fonction qui récupère les informations de l'observateur"""
    #Création du hash du script
    script_name = os.path.basename(sys.argv[0])
    with open(script_name, "rb") as f:
        md5_script = hasher(f.read())

    #Création l'objet observeur
    observer = {
        "ip_public": ipPublic(),
        "startTime": datetime.now(),
        "cookies": cookies,
        "place":{
            "address":"University of Lausanne",
            "zip_code":1015,
            "city":"Lausanne",
            "country":"CH"
        },
        "system":{
            "os_name": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version()
        },
        "tool":{
            "software": "Python",
            "software_version": platform.python_version(),
            "script": script_name,
            "md5_script": md5_script
        }
    }
    return observer


def authentification():
    """Retourne Erreur dans le cas ou le state retourné dans l'adresse n'est pas le bon et rappel la fonction, si le state correspond alors la fonction retourne le token de l'utilisateur --
    la fonction permet la connexion de l'utilisateur a pinterest et demande l'autorisation a l'utilisateur que l'application se fasse passer pour lui. Si tout fonctionne, retourne le token alloué à l'utilisateur"""

    profile = webdriver.FirefoxProfile('/Users/Acp/Library/Application Support/Firefox/Profiles/lo79ern1.default')  #Inserer ici le profil avec lequel l'utilisateur est connecté à Pinterest ##/Users/Acp/Library/Application Support/Firefox/Profiles/8fnz2654.ProfilSelenium
    driver=webdriver.Firefox() #firefox_profile=profile

    print("\nVeuillez vous authentifier sur Pinterest et autoriser l'application dans la fenêtre FireFox")
    state=hasher(str(random.randint(10000,1000000000))) #Génère un chiffre aléatoire, crée son hash et le rentre dans la variable state (state est un moyen de sécurité utilisé lors de l'authentifiaction 0Auth)

    etat="Erreur"
    while "Erreur" in etat:
        driver.get("https://api.pinterest.com/oauth/?response_type=code&redirect_uri=https://www.google.ch/&client_id=4866729400791483761&scope=read_public,write_public,read_relationships,write_relationships&state="+state) #Le paramêtre client_id est propore à l'application enregistrée sur pinterest
        while(True):
            try:
                WebDriverWait(driver,60).until(EC.presence_of_element_located((By.ID,'hplogo')))
                break
            except:
                print("On passe la deuxième...")

        urlcode=driver.current_url #Récupère l'URL contenant le code d'authentification

        #Récupèration du state pour vérification
        regexreturnstate=re.compile("state=[0-9a-zA-z]+")
        returnstate=regexreturnstate.findall(urlcode)[0].split("=")[1]

        if state==returnstate:
            pass
        else:
            etat="Erreur: Problème de sécurité lors de l'authentifiaction! Recommencer"
            print(etat)
            continue

        #Récupération du code dans l'url
        try:
            regexcode=re.compile("code=[0-9a-zA-z]+")
            code=regexcode.findall(urlcode)[0].split("=")[1]
        except:
            etat="Erreur: Il faut donner l'authorisation à l'application pour pouvoir continuer"
            print(etat)
            continue
            # code=urlcode.split("code=")[1]

        #Requete via request pour obtenir le json avec l'acces token de l'utilisateur
        etat="Autorisation accordée"
        print(etat)
        auth=requests.post("https://api.pinterest.com/v1/oauth/token?grant_type=authorization_code&client_id=4866729400791483761&client_secret=b87ec2a5fbde804a3a78c25d617da3e2eb386c409555d5156860fc3a6903d45f&code="+str(code)).json() #jason contenant le token et autre donnée lié a l'authentifiaction de plus #Les paramêtre client_id et client_secret sont propore à l'application enregistrée sur pinterest
        token=auth['access_token'] #récupère la valeur du token dans le dico auth
        cookies, s=get_cookies(driver)
        driver.quit()


    return token, cookies, s


def renderedHTML(driver):
    """Récupération du rendered HTML"""
    elem = driver.find_element_by_xpath("//*")
    html = elem.get_attribute("outerHTML")
    return html


def get_pin(pin_id, token):
    """Retourne les informations d'un pin via son ID"""
    return requests.get('https://api.pinterest.com/v1/pins/'+pin_id +'?access_token='+token+'&fields=url,note,link,id,creator,counts,image').json()


def get_boardPins(board, token, limit=100, cursor=None):
    """Retourne les information des pins d'un board spécifique"""
    #le paramètre cursor peut-être récupéré dans la requête précédente result['page']['cursor']
    url = 'https://api.pinterest.com/v1/boards/'+board+'/pins?access_token='+token+'&limit='+str(limit)
    if cursor != None: url += '&cursor='+cursor
    return requests.get(url).json()


def get_board(board, token):
    """Retourne les informations d'un board spécifique"""
    return requests.get('https://api.pinterest.com/v1/boards/'+board+'?access_token='+token).json()


def get_user(user, token):
    """Retourne les informations d'un utilisateur spécifique"""
    return requests.get('https://api.pinterest.com/v1/users/'+user+'?access_token='+token).json()


def get_pinID(url, cookies):
    """Fonction effectuant une recherche et extrait les pinIDs des x premiers résultats"""
    pinID=[]
    pinID2=[]

    #Affichage de la processbar
    i=0
    i=processbar(100)

    #Utilisation de Selenium (Geckodriver)
    profile = webdriver.FirefoxProfile('/Users/Acp/Library/Application Support/Firefox/Profiles/lo79ern1.default')  #Inserer ici le profil avec lequel l'utilisateur est connecté à Pinterest ##/Users/Acp/Library/Application Support/Firefox/Profiles/8fnz2654.ProfilSelenium
    driver=webdriver.Firefox() #firefox_profile=profile

    i=processbar(i) #Update de la processbar

    driver.get("https://www.pinterest.com/")
    for cookie in cookies:
        driver.add_cookie(cookie)

    driver.get(url)

    i=processbar(i%3) #Update de la processbar

    ############ Solution Requests ############
    #
    # r=s.get(url)
    # contents = r.content
    #
    # #création d'un fichier .html pour s'assurer que les cookies on bien été chargé dans requests (debuging)
    # with open("recherche.html", 'wb+') as f:
    #     f.write(contents)
    #
    # #Utilisation de BeautifulSoup pour parser la page et récuperer les pinIDs
    # soup2 = BeautifulSoup(contents)
    # for link in soup2.findAll('a', attrs={'href': re.compile("^/pin/[0-9]+/$")}):
    #     pinID2.append(link.get('href').split("/")[2])

    ############ Solution Selenium ############
    ####Pour scroller en bas de la page (ici scroll jusqu'à ce qu'il ne charge plus de contenu


    lenOfPage = driver.execute_script("var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    html_page=renderedHTML(driver)
    match=False
    while(match==False):
        i=processbar(i%3)
        lastCount = lenOfPage
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)
        lenOfPage = driver.execute_script("var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True
        else:
            html_page=renderedHTML(driver)

    processbar(404)
    #html_page = requests.get("https://fr.pinterest.com/search/pins/?q=fakeid&rs=typed&term_meta%5B%5D=fakeid%7Ctyped").content
    #driver.save_screenshot("screenshot.png") #screenshot de la page pour voir les résultats de la recherche (devrait prendre tout mais ne prend que la partie visible à l'ecran...)

    #Utilisation de BeautifulSoup pour parser la page et récuperer les pinIDs
    soup = BeautifulSoup(html_page)
    for link in soup.findAll('a', attrs={'href': re.compile("^/pin/[0-9]+/$")}):
        pinID.append(link.get('href').split("/")[2])

    driver.quit()
    return pinID #, pinID2


def get_url(url, s):
    """Fonction qui visite l'url et récupère l'url de la page courante.
    Permet de récuperer l'url de la cible lors d'une redirection"""
    r=s.get(url)
    urlsource=r.url
    return urlsource


def get_cookies(driver):
    """Récupération des cookies de Pinterest avec selenium et injection des cookies dans la session requests"""
    driver.get('https://www.pinterest.com/')
    time.sleep(1)
    cookies=driver.get_cookies()
    print("Les cookies Pinterest de l'utilisateur ont été enregistrés")

    s = requests.Session()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
    print("Transfert des cookies Pinterest de Selenium à la session requests 's' réussi")

    return cookies, s


def insert(db, collection, pin):
    """Fonction qui insert un pin dans la collection de la base MongoDB (db)"""
    client = MongoClient('localhost', 27017)  # Changer l'adresse de la base et le port si besoin
    try:
        client[db][collection].insert(pin)
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")
        print("Successfully inserted pin "+str(pin['data']['id'])+" in "+str(collection))
        sys.stdout.flush()
    except:
        pass


def check(db, collection, pinID, recherche):
    """Fonction qui insert un pin dans la collection de la base MongoDB (db)"""
    client = MongoClient('localhost', 27017)  # Changer l'adresse de la base et le port si besoin
    collections=client[db].collection_names()
    if collection in collections:
        pin=client[db][collection].find_one({'data.id':pinID})
        if pin!=None:
            recherches=pin["recherches"]
            if recherche in recherches:
                # print("\nLe pin "+str(pinID)+" a déjà été obtenu avec la recherche "+str(recherche))
                return "present"
            else:
                recherches.append(recherche)
                client[db][collection].update_one({'data.id':pinID},{'$set':{'recherches':recherches}})
                # print("\nLa recherche '"+str(recherche)+"' à été ajouté à la liste des recherches qui renvoient le pin "+str(pinID))
                return "modifie"
        else:
            # print("\nLe pin "+str(pinID)+" est absent de "+str(collection))
            return "absent"

    else:
        return "absent"


def collections(db):
    """Fonction qui renvoit une liste contenant les collections de la db"""
    client = MongoClient('localhost', 27017)  # Changer l'adresse de la base et le port si besoin
    coll=client[db].collection_names()
    return coll


def processbar(i):
    """Fonction qui affiche et actualise "Processing ..."""
    if i==100: #start
        sys.stdout.write("\033[K")
        print("Processing")
        sys.stdout.flush()

    elif i==0:
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")
        print("Processing.")
        sys.stdout.flush()
    elif i==1:
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")
        print("Processing ..")
        sys.stdout.flush()
    elif i==2:
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")
        print("Processing ...")
        sys.stdout.flush()
    elif i==404: #end
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K\n")
        sys.stdout.flush()
    i=i+1
    return i

###Fonctions pour l'option 4 - Statistiques
# plotly.tools.set_credentials_file(username='Boogeyman010', api_key='x4pu1iaz9x')

def mapreduce(db, collection, key, name):
    """Fonction permettant de compter le nombre d'occurence d'un element dans la base"""

    col = db[collection]

    # Creation du mapper
    mapper = Code("""function () {
                  emit(this."""+str(key)+""",1);
                  }""")

    # Creation du reducer
    reducer = Code("""function (k, v) {
                   var total = 0;
                   for (var i = 0; i < v.length; i++){
                       total += v[i];
                       }
                   return total;
                   }""")

    # Appel de la fonction pymongo mapreduce qui cree une collection avec les resultats
    results = col.map_reduce(mapper, reducer, collection+"_"+name)

    return results


def plot_results(db, collection, result_collection, name):
    """Fonction qui plot les resultats des occurences pour un element"""
    list_id = []
    list_compt = []


    for x in result_collection.find({"value": {"$gt": 1}}).sort("value", pymongo.DESCENDING):
        if x.values()[0] is not None:
            list_id.append(x.values()[0])
            list_compt.append(x.values()[1])

    # Aller chercher le nom et prenom pour la legende du graphique
    if name == "users":
        for x in range(len(list_id)):
            info = db[collection].find_one({'data.creator.id': list_id[x]})
            first_name = info.get(u'data', {}).get(u'creator', {}).get(u'first_name', "")
            last_name = info.get(u'data', {}).get(u'creator', {}).get(u'last_name', "")
            list_id[x] = first_name + " " + last_name+ "\n(id: " + list_id[x] + ")"

    if len(list_id) > 0:
        plotly.offline.plot({
            "data": [{
                "x": list_id,
                "y": list_compt,
                "name": "Col2",
                "type": "bar",
                #"text": list_id,
            }],
            "layout": {
                "yaxis": {
                    "type": "linear",
                    "autorange": "true",
                    "tickfont": {"size": "10"},
                    "title": "Number of occurrences"
                },
                "xaxis": {
                    "type": "category",
                    "autorange": "true",
                    "tickangle": "0",
                    "tickfont": {"size": "10"},
                    "title": name + " with a number of occurrences > 1"
                },
                "autosize": "true",
                "dragmode": "pan",
                "title": "Number of occurrences of the " + name + " for the collection '" + collection + "'"
            }
        }, filename=collection +"_"+name+".html", auto_open= True)
    else:
        print("Il n'y a aucun(e) " + name + " qui apparait plus d'une fois")


def get_extended(db, collection, user_collection, domain_collection):
    """Fonction qui recupere les pins qui contiennent les users et domains les plus frequents et les store pour ANB"""
    list_excel = []

    for x in user_collection.find({"value": {"$gt": 1}}).sort("value", pymongo.DESCENDING):
        if x.values()[0] is not None:
            user = x.get(u'_id')
            for doc in db[collection].find({'data.creator.id' : user}):
                list_excel.append(doc)

    for x in domain_collection.find({"value": {"$gt": 1}}).sort("value", pymongo.DESCENDING):
        if x.values()[0] is not None:
            domain = x.get(u'_id')
            for doc in db[collection].find({'data.domain' : domain}):
                if doc not in list_excel:
                    list_excel.append(doc)

    # Enregistrement des informations du pin dans un .xls pour ANB
    new_workbook = xlwt.Workbook()
    new_sheet = new_workbook.add_sheet('Feuille1')

    for x in range(len(list_excel)):
        new_sheet.write(x, 0, list_excel[x].get(u'data', {}).get(u'creator', {}).get(u'id'))
        new_sheet.write(x, 1, list_excel[x].get(u'data', {}).get(u'creator', {}).get(u'first_name'))
        new_sheet.write(x, 2, list_excel[x].get(u'data', {}).get(u'creator', {}).get(u'last_name', ''))
        new_sheet.write(x, 3, list_excel[x].get(u'data', {}).get(u'domain'))

    new_workbook.save('analyst.xls')

    # Suppression des collections de recherche
    db[collection+"_users"].drop()
    db[collection+"_domains"].drop()


#Fonctions pour l'option 5 - Pertinence
def mongo_pinID(db, collection):
    """recupere les pins ID a partir d'une collection mongoDB"""
    client = MongoClient('localhost', 27017)
    pinID = client[db][collection].distinct('data.id')

    return pinID

def verification(listepinID):
    """fonction qui presente a l'utilisateur chaque resultat pour determiner la pertinence"""
    list_pert = []
    for i in listepinID:
        driver.get('https://www.pinterest.com/pin/'+i)
        choix = raw_input("Pertinent ? 1=Oui  0=Non  Q=quitter: ")
        regexp = r"^([0, 1, q, Q])$"
        while (re.match(regexp, choix) is None):
            choix = raw_input("Choix non valide, veuillez selectionner 0, 1 ou Q: ")
        if choix == "0":
            tup = (i, "Non-pertinents")
            list_pert.append(tup)
        elif choix == "1":
            tup = (i, "Pertinents")
            list_pert.append(tup)
        else:
            break

    driver.quit()
    return list_pert


def counter(liste):
    """fonction qui compte les resultat pertinents et non pertinents, et affiche le resultat"""
    compte = Counter(elem[1] for elem in liste)
    pert=0.
    nopert=0.
    for i in compte:
        if i=="Pertinents":
            pert=compte[i]
        else:
            nopert=compte[i]
        print('%s : %d' % (i, compte[i]))

    pourcent=(float(pert)/(float(pert)+float(nopert)))*float(100)
    print("Résultats pertinents: "+str(pourcent)+"%")


def quitter():
    """ Fonction qui termine le programme"""
    print("\nAu revoir !")
    quit()

# Exemples:
# pin_id = '371687775471458656'
# print get_pin(pin_id, token)

# board = 'alen1093/bodybuilding' # format: <username>/<board_name>
# print get_boardPins(board, token)
#
# user = 'rolex'
# print get_user(user, token)



################MAIN################

# token = "ASkXhTh7XX8xsWFCK_3XvQ4t9cp3FIS9ZmaOclZDiV4wn8Av7AAAAAA" #à remplir https://developers.pinterest.com/tools/access_token/?

#Authentification de l'utilisateur et autorisation de l'apps
token , cookies, s = authentification() #Appel la fonction authentification

choix="1"
while(True):
    if choix=="1":
        #collection="fakeid"
        col=collections("Pinterest")
        if len(col)==0:
            print("\nAucune collection existante")
        else:
            print("\nCollections existantes:")
            for collection in col:
                print(collection)
        collection=raw_input("Dans quelle collection voulez-vous ajouter les recherches (crée si inexistante): ")
        choix="2"

    elif choix=="2":
        #Recherche par mot clé et extraction des pinID des résultats
        absents=[]
        modifies=[]
        presents=[]
        listepinID=[]#pour eviter une erreur si l'utilisateur quitte trop tot
        #recherche="fake"
        recherche=raw_input("\nMot à rechercher: ")
        print("(CTRL+C pour arrêter le processus)")
        q=recherche.replace(" ","%20")
        url="https://fr.pinterest.com/search/pins/?q="+str(q)+"&auto_correction_disabled=true"
        # url="https://www.pinterest.com/search/pins/?q=id%20fake&auto_correction_disabled=true"

        try:
            listepinID=get_pinID(url, cookies)
            #print("pintID="+str(listepinID))

            #Extraction des informations pours tous les pins inexistant dans la collection et introduction dans mongoDB
            for pinID in listepinID:
                #Check l'existance de la collection, si le pin est présent dedans ou non si oui, modification de recherches
                ok=check("Pinterest", collection, pinID, recherche)

                if ok=="absent":
                    limite=datetime.now()+timedelta(hours=1)
                    pin = get_pin(pinID, token)

                    #Verification que l'api renvoit bien des données sur le pin et non pas une erreur
                    if 'message' in pin.keys():
                        sys.stdout.write("\033[F")
                        sys.stdout.write("\033[K")
                        print(str(pin['message'])+'\nLa prochaine requête peut être effectuée à '+str(limite.hour)+":"+str(limite.minute)+":"+str(limite.second)+"\n")
                        sys.stdout.flush()
                        break #Arrête de parcourir listepinID
                    else:
                        pass

                    url2 = pin['data']['link']
                    try:
                        urlsource=get_url(url2, s)
                        pin['data']['link']=urlsource
                        re_domain = re.compile(r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}')
                        pin['data']['domain']=re.findall(re_domain,urlsource)[0]
                    except:
                        pass

                    absents.append(pinID)
                    recherches=[]
                    recherches.append(recherche)
                    pin["Observer"] = observer(cookies)
                    pin["recherches"]=recherches
                    insert("Pinterest", collection, pin)

                elif ok=="modifie":
                    if pinID not in modifies:
                    # On ajoute a modifies seulement si il est absent
                        modifies.append(pinID)
                        continue
                    else:
                        pass

                else:
                    if pinID not in presents:
                        # On ajoute a present seulement si il est absent
                        presents.append(pinID)
                    else:
                        pass
        except KeyboardInterrupt:
            pass

        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")
        print("\rLa recherche '"+str(recherche)+"' a renvoyé "+str(len(listepinID))+" résultats")
        print(str(len(absents))+" pins ont été ajoutés à "+str(collection))
        print(str(len(modifies))+" pins ont vu la recherche '"+str(recherche)+"' ajoutée à leur liste 'recherches'")
        print(str(len(presents))+" pins avaient été ajoutés précedement à "+str(collection)+" pour la recherche '"+str(recherche)+"'")
        time.sleep(1)


    elif choix=="3":
        #Recherche par mot clé et extraction des pinID des résultats
        absents=[]
        modifies=[]
        presents=[]
        listepinID=[] #pour eviter une erreur si l'utilisateur quitte trop tot

        #recherche="fake"
        recherche=raw_input("\nMot à rechercher: ")
        print("(CTRL+C pour terminer le processus)")
        q=recherche.replace(" ","%20")
        url="https://fr.pinterest.com/search/pins/?q="+str(q)+"&auto_correction_disabled=true"
        # url="https://www.pinterest.com/search/pins/?q=id%20fake&auto_correction_disabled=true"

        limite=datetime.now()-timedelta(minutes=1)
        while(True):
            try:
                if datetime.now()>limite:
                    limite=datetime.now()+timedelta(hours=1) #La valeur ici peut être modifié en fonction du nombre de recherche que l'on veut effectuer dans un laps de temps donné. Ici une requête par heure mais ca pourait être day=1 pour effectuer une requête par jour
                    listepinID=get_pinID(url, cookies)
                    #print("pintID="+str(listepinID))

                    #Extraction des informations pours tous les pins inexistant dans la collection et introduction dans mongoDB
                    for pinID in listepinID:
                        #Check l'existance de la collection, si le pin est présent dedans ou non si oui, modification de recherches
                        ok=check("Pinterest", collection, pinID, recherche)

                        if ok=="absent":
                            pin = get_pin(pinID, token)

                            #Verification que l'api renvoit bien des données sur le pin et non pas une erreur
                            if 'message' in pin.keys():
                                limite=datetime.now()+timedelta(hours=1)
                                while(datetime.now()<limite):
                                    sys.stdout.write("\033[F")
                                    sys.stdout.write("\033[K")
                                    print(str(pin['message'])+'; La prochaine requête sera effectuée à '+str(limite.hour)+":"+str(limite.minute)+":"+str(limite.second))
                                    sys.stdout.flush()
                                    time.sleep(1)
                                pin = get_pin(pinID, token)
                            else:
                                pass

                            url2 = pin['data']['link']
                            try:
                                urlsource=get_url(url2, s)
                                pin['data']['link']=urlsource
                                re_domain = re.compile(r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}')
                                pin['data']['domain']=re.findall(re_domain,urlsource)[0]
                            except:
                                pass

                            absents.append(pinID)
                            recherches=[]
                            recherches.append(recherche)
                            pin["Observer"] = observer(cookies)
                            pin["recherches"]=recherches
                            insert("Pinterest", collection, pin)

                        elif ok=="modifie":
                            if pinID not in modifies:
                            # On ajoute a modifies seulement si le pinID est absent
                                modifies.append(pinID)
                                continue
                            else:
                                pass

                        else:
                            if pinID not in presents:
                                # On ajoute a presents seulement si le pinID est absent
                                presents.append(pinID)
                            else:
                                pass
                else:
                    sys.stdout.write("\033[F")
                    sys.stdout.write("\033[K")
                    print("La prochaine requête sera effectuée à "+str(limite.hour)+":"+str(limite.minute)+":"+str(limite.second))
                    sys.stdout.flush()
                    time.sleep(1)
            except KeyboardInterrupt:
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[K")
                print("\rLa recherche '"+str(recherche)+"' a renvoyé "+str(len(listepinID))+" résultats")
                print(str(len(absents))+" pins ont été ajoutés à "+str(collection))
                print(str(len(modifies))+" pins ont vu la recherche '"+str(recherche)+"' ajoutée à leur liste 'recherches'")
                time.sleep(1)
                break


    elif choix=="4":
        col=collections("Pinterest") #liste contenant les collection de la db "Pinterest"
        if collection in col:
            client = MongoClient('localhost', 27017)
            db = client.Pinterest

            user_collection = mapreduce(db,collection,"data.creator.id","users")
            domain_collection = mapreduce(db,collection,"data.domain","domains")

            plot_results(db,collection,user_collection,"users")
            plot_results(db,collection,domain_collection,"domains")

            get_extended(db,collection,user_collection,domain_collection)

        else:
            print("La collection est vide.\nVeuillez lancer l'option 2 ou 3 avant d'afficher des statistiques ou changer pour une collection non vide. ")
            time.sleep(2)

    elif choix=="5":
        col=collections("Pinterest") #liste contenant les collection de la db "Pinterest"
        if collection in col:
            listepinID = mongo_pinID("Pinterest", collection)
            driver = webdriver.Firefox()
            driver.get("https://www.pinterest.com/")
            for cookie in cookies:
                driver.add_cookie(cookie)
            list_pert=verification(listepinID)
            counter(list_pert)
        else:
            print("La collection est vide.\nVeuillez lancer l'option 2 ou 3 avant d'effectuer une vérification de pertinence ou changer pour une collection non vide. ")
            time.sleep(2)

    elif choix=="6":
        quitter()

    choix=raw_input("\n1.Changer de collection\n2.Effectuer une recherche à integrer dans '"+str(collection)+"'\n3.Mode Veille\n4.Statistique de '"+str(collection)+"'\n5.Contrôle de pertience des résultats dans '"+str(collection)+"'\n6.Quitter le programme\n\nAction à effectuer: ")
    regexp=r"^([1-6])$"
    while(re.match(regexp, choix) is None):
        choix=raw_input("Choix non valide, veuillez entrer votre choix (1 à 6): ")
