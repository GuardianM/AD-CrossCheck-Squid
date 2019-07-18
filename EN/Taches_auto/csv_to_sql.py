import pandas as pd
import os
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

### Credentials import ###
import sql_credentials
from sql_credentials import db_name
from sql_credentials import db_IP_address
from sql_credentials import db_password
from sql_credentials import db_username
from sql_credentials import DC_name



#### Activité de connexion (login.csv) ####

# ---> Ouverture du fichier CSV et envoi des donnnées vers la table "user_act"
def login():

    # Noms des colonnes 
    column_names = ['Date','Heure','Action','User','Ip','PC']


## TEST 1 ##
    
    # Test lecture du fichier login.csv
    try:
        # Chemin vers le fichier en utilisant la variable DC_name renseignée avec le script setup.pyw
        path1 = "\\\\" + DC_name + "\SharedUsersLogs$\login.csv"
        df = pd.read_csv(path1, header = None, names = column_names)

    # Si test lecture non concluant on stop tout
    except:
        print("login.csv lecture : NON")
        return

    # Si test de lecture OK on test la creation du moteur BDD
    else:
        print("login.csv lecture : OK")



    ## TEST 2 ##
        
        # Test creation moteur BDD
        try:
            global engine
            engine = create_engine('mysql://' + db_username + ':' + db_password + '@' + db_IP_address + '/' + db_name + '')

            # Connexion pour verification credentials bdd fournis par sql_credentials.py
            engine.connect()


        # Si moteur BDD non fonctionnel on stop tout
        except:
            print("Creation moteur BDD : NON")
            return

        # Si moteur BDD OK on test l'envoi des données vers la BDD
        else:
            print("Creation moteur BDD : OK")
            


        ## TEST 3 ##
            
            # Test d'envoi des données vers BDD
            try:
                with engine.connect() as conn, conn.begin():
                    df.to_sql('user_act', conn, if_exists='append', index=False)


            # Si test non concluant on stop tout
            except:
                print("login.csv to SQL : NON")
                conn.close()
                return

            
            # Si test OK on continu 
            else:
                print("login.csv to SQL : OK")

                # Suppression du contenu du fichier pour être sur de ne pas les importer lors de la prochaine executionde la tache planifiée
                f = open(path1, "w")
                f.truncate()
                f.close()

                # Prochaine fonction
                logout()




#### Activité de deconnexion (logout.csv) ####
# ---> 
def logout():

    # Noms des colonnes
    column_names2 = ['Date','Heure','Action','User','Ip','PC']


## TEST 1 ##
    
    # Test lecture du fichier logout.csv
    try:
        path2 = "\\\\" + DC_name + "\SharedUsersLogs$\logout.csv"
        df = pd.read_csv(path2, header = None, names = column_names2)

    # Si test de lecture non concluant on stop tout
    except:
        print("logout.csv lecture : NON")
        return

    # Si test de lecture OK on test la BDD
    else:
        print("logout.csv lecture : OK")



    ## TEST 2 ##
        
        # Test d'envoi des données vers BDD
        try:
            with engine.connect() as conn, conn.begin():
                df.to_sql('user_act', conn, if_exists='append', index=False)


        # Si test non concluant on stop tout
        except:
            print("logout.csv to SQL : NON")
            conn.close()
            return


        # Si test OK on continu 
        else:
            print("logout.csv to SQL : OK")
            
            # Suppression du contenu du fichier pour être sur de ne pas les importer lors de la prochaine executionde la tache planifiée
            f2 = open(path2, "w")
            f2.truncate()
            f2.close()

            # Fermeture de la session BDD
            conn.close()



if __name__ == "__main__":
    login()
