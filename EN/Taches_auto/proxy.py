import pandas as pd
import os
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import paramiko

### Credentials import ###
import proxy_credentials
from proxy_credentials import ssh_IP_address
from proxy_credentials import ssh_password
from proxy_credentials import ssh_username
from proxy_credentials import root_password

import sql_credentials
from sql_credentials import db_name
from sql_credentials import db_IP_address
from sql_credentials import db_password
from sql_credentials import db_username




# ---> En SSH : Copie du fichier /var/squid/logs/access.log dans /etc/access1.log
def SshCopy1():
    
    try:
        # Client SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ssh_IP_address, username=ssh_username, password=ssh_password)

        # Commande
        cmdSSH = 'echo ' + root_password + '| sudo -S cp /var/squid/logs/access.log /etc/access1.log'
        ssh.exec_command(cmdSSH)

    except:
        print("SshCopy1 : NON")
        return

    else:
        print("SshCopy1 : OK")
        ssh.close()
        
        # Prochaine fonction
        SshCopy2()



# ---> En SSH : Attribution des droits à l'utilisateur $ssh_username sur le fichier precedement copié
def SshCopy2():
    
    try:
        # Client SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ssh_IP_address, username=ssh_username, password=ssh_password)

        # Commande
        cmdSSH = 'echo ' + root_password + '| sudo -S chown ' + ssh_username + ' /etc/access1.log'
        ssh.exec_command(cmdSSH)

    except:
        print("SshCopy2 : NON")
        return

    else:
        print("SshCopy2 : OK")
        ssh.close()
        
        # Prochaine fonction
        SshCopy3()


    
# ---> En SSH : Passage en root et suppression du contenu du fichier /var/squid/logs/access.log
# ---> La suppression du contenu evitera de copier les anciennes données lors de la prochaine execution du script
def SshCopy3():
    
    try:
        # Client SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ssh_IP_address, username=ssh_username, password=ssh_password)


        # Commande
        stdin, stdout, stderr = ssh.exec_command('sudo su')

        # Mot de passe demandé apres la commande "sudo su"
        stdin.write((root_password) + '\n')
        stdin.flush()

        # Suppression du contenu du fichier access.log
        stdin.write('echo "" > /var/squid/logs/access.log\n')
        stdin.flush()

    except:
        print("SshCopy3 : NON")
        return

    else:
        print("SshCopy3 : OK")
        ssh.close()
        
        # Prochaine fonction
        Transfert()



# ---> En SFTP : Telechargement du fichier /etc/access1.log dans le dossier du script executé
def Transfert():
    
    try:
        # Client SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ssh_IP_address, username=ssh_username, password=ssh_password)
        

        ftp_client = ssh.open_sftp()
        ftp_client.get("/etc/access1.log","access1.log")

    except:
        print("Transfert : NON")
        return

    else:
        print("Transfert : OK")
        ftp_client.close()
        
        # Prochaine fonction
        SendToSQL()


    
# ---> En local : Envoie des données contenues dans access1.log vers la table "proxy" de la BDD
def SendToSQL():

    # Nom des colonnes 
    column_names = ['Date','Heure','Ip','Link']
    
    # Lecture du fichier
    df = pd.read_csv(r"access1.log", header = None, names = column_names)

    # Engine de connexion à la BDD
    engine = create_engine('mysql://' + db_username + ':' + db_password + '@' + db_IP_address + '/' + db_name + '', echo=True)



    try:
        with engine.connect() as conn, conn.begin():
            df.to_sql('proxy', conn, if_exists='append', index=False)
        conn.close()

    except:
        print("SendToSQL : NON")
        return

    else:            
        print("SendToSQL : OK")
        os.remove(r"access1.log")
        
        # Prochaine fonction
        RemoveRemoteFile()



# ---> En SSH : Suppression du fichier distant stocké dans /etc/access1.log
# ---> Inutile le conserver sur Pfsense puisqu'il a été importé dans la BDD juste avant
def RemoveRemoteFile():
    
    try:
        # Client SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ssh_IP_address, username=ssh_username, password=ssh_password)

        # Commande
        cmdSSH = 'echo ' + root_password + '| sudo -S rm /etc/access1.log'
        ssh.exec_command(cmdSSH)

    except:
        print("RemoveRemoteFile : NON")
        return

    else:
        ssh.close()
        print("RemoveRemoteFile : OK")
        print("Taches planifiée : OK")
        


if __name__ == '__main__':
    SshCopy1()


