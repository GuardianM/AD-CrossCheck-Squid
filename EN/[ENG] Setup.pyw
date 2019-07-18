import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
from tkinter import messagebox
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import paramiko
import datetime
import win32com.client
import os
import os.path



# -------------------- Premiere fenetre avec le choix de la date -------------------- #

class MainW(tk.Tk):
    def __init__(self, root):
        tk.Tk.__init__(self, root)

        self.Structure()
        self.DbStructure()
        self.PfsenseStructure()
        self.ComputerStructure()

        self.resizable(False, False)
        self.title("Setup")
        self.protocol("WM_DELETE_WINDOW", self.ExitMain)
        self.configure(background="#343434")

    # Initialisation de quelques variables

        self.sshState = 0
        self.dbState = 0
        self.shareState = 0



    # Style ttk pour les boutons
    
        style = ttk.Style()
        style.configure("TButton", background="#343434", width=18, font=('Century Gothic',11))


    # Style ttk pour les LabelFrame
    
        style2 = ttk.Style()
        style2.configure("TLabelframe", background="#343434", bordercolor="#343434", font=('Century Gothic',11), bd=150)


    # Style ttk pour les Label des LabelFrame
        style3 = ttk.Style()
        style3.configure("TLabelframe.Label", font=('Century Gothic',11), foreground="#D2A028", background="#343434")


# ---> Fonction executée si l'utilisateur ferme la fenetre
    def ExitMain(self):
        
    # Un message indiquant les parties non renseignées est affiché
        if self.sshState == 0 and self.dbState == 0 and self.shareState == 0:
            if messagebox.askokcancel("Exit", "None of the parts have been configured. Do you really want to leave this application?", parent=self):
                app.destroy()

        elif self.sshState == 1 and self.dbState == 0 and self.shareState == 0:
            if messagebox.askokcancel("Exit", "The Database and Shared Folder sections have not been configured. Do you really want to leave this application?", parent=self):
                app.destroy()

        elif self.sshState == 0 and self.dbState == 1 and self.shareState == 0:
            if messagebox.askokcancel("Exit", "The PfSense and Shared Folder sections have not been set up. Do you really want to leave this application?", parent=self):
                app.destroy()


        elif self.sshState == 0 and self.dbState == 0 and self.shareState == 1:
            if messagebox.askokcancel("Exit", "The Database and PfSense sections have not been configured. Do you really want to leave this application?", parent=self):
                app.destroy()

        elif self.sshState == 1 and self.dbState == 1 and self.shareState == 0:
            if messagebox.askokcancel("Exit", "The Shared folder section has not been configured. Do you really want to leave this application?", parent=self):
                app.destroy()

        elif self.sshState == 1 and self.dbState == 0  and self.shareState == 1:
            if messagebox.askokcancel("Exit", "The Database section has not been configured. Do you really want to leave this application", parent=self):
                app.destroy()

        elif self.sshState == 0 and self.dbState == 1  and self.shareState == 1:
            if messagebox.askokcancel("Exit", "The Pfsense section has not been configured. Do you really want to leave this application", parent=self):
                app.destroy()

        elif self.sshState == 1 and self.dbState == 1  and self.shareState == 1:
            if messagebox.askokcancel("Exit", "All data has been recorded. Do you really want to leave this application?", parent=self):
                app.destroy()


# ---> Structure de la fenetre main        
    def Structure(self):
        
    # Les deux frames de cette même fenetre
        self.top_frame = tk.Frame(self, bg="#343434", height=50, width=320, padx=10)
        self.cred_frame = tk.Frame(self, bg="#343434", height=100, width=320, padx=10)
        

    # Quelques reglages liés aux frames
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.top_frame.grid(row=1)
        self.top_frame.grid_propagate(True)

        self.cred_frame.grid(row=3)
        self.cred_frame.grid_propagate(True)



    # LabelFrame pour les parties bdd, pfsense et dossier partagé
        self.db_f = ttk.LabelFrame(self.cred_frame, text="   Database   ", labelanchor="n")
        self.db_f.grid(row=2, column=0, padx=10, sticky="n", pady=(10,30))

        self.pfsense_f = ttk.LabelFrame(self.cred_frame, text="   PfSense   ", labelanchor="n")
        self.pfsense_f.grid(row=2, column=1, padx=10, sticky="n", pady=(10,30))

        self.computer_f = ttk.LabelFrame(self.cred_frame, text="   Shared Folder   ", labelanchor="n")
        self.computer_f.grid(row=3, columnspan=2, padx=10, sticky="n", pady=(10,30))
    

    # Message de "bienvenue"  
        self.welcomeLabel = tk.Label(self.top_frame, bg="#343434", fg="#D2A028",
                                     text="Initialization of the user activity search engine !", wrap=305, font=('Century Gothic',13))
        self.welcomeLabel.grid(row=1, pady=(15, 40))



# ---> Partie base de données
    def DbStructure(self):
        
    # Message de bienvenue
        self.db_message = tk.Label(self.db_f, bg="#343434", fg="white", font=('Century Gothic',11),
                                   text="Authentication information")
        self.db_message.grid(row=0, sticky="n", columnspan=2, pady=(15, 15))
    
    # Champ Username
        self.db_UsernameLabel = tk.Label(self.db_f, bg="#343434", fg="white", font=('Century Gothic',11), text="Username")
        self.db_UsernameLabel.grid(row=1, column=0, sticky="w", padx=(10,10), pady=(30,0))

        self.db_Username = ttk.Entry(self.db_f, font=('opensans',11), justify="center")
        self.db_Username.grid(row=1, column=1, pady=(30,0), padx=(0,10))


    # Champ password
        self.db_PasswordLabel = tk.Label(self.db_f, bg="#343434", fg="white", font=('Century Gothic',11), text="Password")
        self.db_PasswordLabel.grid(row=2, column=0, sticky="w", padx=(10,10), pady=(10,0))

        self.db_Password = ttk.Entry(self.db_f, show="*", font=('opensans',11), justify="center")
        self.db_Password.grid(row=2, column=1, pady=(10,0), padx=(0,10))

        
    # Champ Ip address
        self.db_IpLabel = tk.Label(self.db_f, bg="#343434", fg="white", font=('Century Gothic',11), text="IP Address")
        self.db_IpLabel.grid(row=3, column=0, sticky="w", padx=(10,10), pady=(10,0))

        self.db_IP = ttk.Entry(self.db_f, font=('opensans',11), justify="center")
        self.db_IP.grid(row=3, column=1, pady=(10,0), padx=(0,10))


    # Champ DB name
        self.db_NameLabel = tk.Label(self.db_f, bg="#343434", fg="white", font=('Century Gothic',11), text="Database name")
        self.db_NameLabel.grid(row=4, column=0, sticky="w", padx=(10,10), pady=(10,0))

        self.db_Name = ttk.Entry(self.db_f, font=('opensans',11), justify="center")
        self.db_Name.grid(row=4, column=1, pady=(10,0), padx=(0,10))


    # Bouton valider       
        self.db_button = ttk.Button(self.db_f, text="Confirm", command=self.DbVerification)
        self.db_button.grid(row=5, columnspan=2, pady=(35,25))


# ---> Partie pfsense
    def PfsenseStructure(self):
        
    # Message d'entete
        self.pf_message = tk.Label(self.pfsense_f, bg="#343434", fg="white", font=('Century Gothic',11),
                                   text="SSH authentification")
        self.pf_message.grid(row=0, columnspan=2, sticky="n", pady=(15, 15))                     

    # Champ SSH Username
        self.pf_UsernameLabel = tk.Label(self.pfsense_f, bg="#343434", fg="white", font=('Century Gothic',11), text="Username")
        self.pf_UsernameLabel.grid(row=1, column=0, sticky="w", padx=(10,10), pady=(30,0))

        self.pf_Username = ttk.Entry(self.pfsense_f, font=('opensans',11), justify="center")
        self.pf_Username.grid(row=1, column=1, pady=(30,0), padx=(0,10))


    # Champ SSH password
        self.pf_PasswordLabel = tk.Label(self.pfsense_f, bg="#343434", fg="white", font=('Century Gothic',11), text="Password")
        self.pf_PasswordLabel.grid(row=2, column=0, sticky="w", padx=(10,10), pady=(10,0))

        self.pf_Password = ttk.Entry(self.pfsense_f, show="*", font=('opensans',11), justify="center")
        self.pf_Password.grid(row=2, column=1, pady=(10,0), padx=(0,10))

        
    # Champ Ip address
        self.pf_IpLabel = tk.Label(self.pfsense_f, bg="#343434", fg="white", font=('Century Gothic',11), text="IP address")
        self.pf_IpLabel.grid(row=3, column=0, sticky="w", padx=(10,10), pady=(10,0))

        self.pf_IP = ttk.Entry(self.pfsense_f, font=('opensans',11), justify="center")
        self.pf_IP.grid(row=3, column=1, pady=(10,0), padx=(0,10))

    # Champ Root password
        
        self.pf_RootLabel = tk.Label(self.pfsense_f, bg="#343434", fg="white", font=('Century Gothic',11), text="ROOT password")
        self.pf_RootLabel.grid(row=4, column=0, sticky="w", padx=(10,10), pady=(10,0))

        self.pf_Root = ttk.Entry(self.pfsense_f, show="*", font=('opensans',11), justify="center")
        self.pf_Root.grid(row=4, column=1, pady=(10,0), padx=(0,10))
    
    # Bouton valider
        self.pf_button = ttk.Button(self.pfsense_f, text="Confirm", command=self.SshVerification)
        self.pf_button.grid(row=5, columnspan=2, pady=(35,25))



# ---> Partie computer
    def ComputerStructure(self):

        # Message d'entete
        self.computer_message = tk.Label(self.computer_f, bg="#343434", fg="white", font=('Century Gothic',11),
                                   text="Enter the name of the domain controller below ")
        self.computer_message.grid(row=0, columnspan=4, sticky="n", pady=(15,10), padx=(10,10))                     


    # Message d'avertissement
        self.computer_avert_message = tk.Label(self.computer_f, bg="#343434", fg="red", font=('Century Gothic',10,'italic'), text="Be careful with upper and lower case letters!")
        self.computer_avert_message.grid(row=1, columnspan=4, sticky="n", padx=(10,10), pady=(0,20))

    # Case dans laquelle on entre le nom du serveur
        self.computer_NameEntry = ttk.Entry(self.computer_f, font=('opensans',11), justify="center", width=25)
        self.computer_NameEntry.grid(row=2, columnspan=4, pady=(10,15), padx=(10,10))


    # Bouton valider
        self.computer_button = ttk.Button(self.computer_f, text="Confirm", command=self.CheckShare)
        self.computer_button.grid(row=3, columnspan=4, pady=(0,25), padx=(10,10))


# ---> Verification de l'existence du dossier ShareUsersLogs sur le controleur de domaine
    def CheckShare(self):

    # On stock le nom du seveur dans une variable
        self.computername = self.computer_NameEntry.get()

    # On creer le chemin jusqu'au repertoire partagé
        # Le signe $ indique que le repetoire est masqué (donc accessible seulement lorsque l'on indique l'adresse entiere)
        self.path1 = "\\\\" + self.computername + "\SharedUsersLogs$"
        
    # Chemin vers les scripts login.bat et logout.bat
        self.path2 = "\\\\" + self.computername + "\\NETLOGON\login.bat"
        self.path3 = "\\\\" + self.computername + "\\NETLOGON\logout.bat"


    # Test de l'accessibilité au repertoire partagé et aux scripts. Message d'erreur en fonction de l'accessiblité de chacun
        if os.path.isdir(self.path1) and os.path.isfile(self.path2) and os.path.isfile(self.path3):
            messagebox.showinfo("Good job!", "Access to SharedUsersLogs shared directory and login/login.bat scripts successful!", parent=self)
            self.shareState += 1
            self.computer_button.config(text="Successful", command=self.AlreadyDone)
            self.computer_message.config(fg="green")
            self.computer_avert_message.config(fg="green")


            # Si toutes toutes les fonctions sont notées comme valider, on execute le final check    
            if self.sshState == 1 and self.dbState == 1 and self.shareState == 1:
                self.FinalCheck()

            # Sinon on continu
            else:
                return

        elif os.path.isdir(self.path1) and os.path.isfile(self.path2) and not os.path.isfile(self.path3):
            messagebox.showerror("Error", "Access to the logout.bat script impossible.", parent=self)
            

        elif os.path.isdir(self.path1) and not os.path.isfile(self.path2) and os.path.isfile(self.path3):
            messagebox.showerror("Error", "Access to the login.bat script impossible.", parent=self)


        elif not os.path.isdir(self.path1) and os.path.isfile(self.path2) and os.path.isfile(self.path3):
            messagebox.showerror("Error", "Access to the SharedUsersLogs shared directory is not possible.", parent=self)


        elif not os.path.isdir(self.path1) and not os.path.isfile(self.path2) and os.path.isfile(self.path3):
            messagebox.showerror("Error", "Access to the SharedUsersLogs shared directory and the login.bat script impossible.", parent=self)


        elif not os.path.isdir(self.path1) and os.path.isfile(self.path2) and not os.path.isfile(self.path3):
            messagebox.showerror("Error", "Access to the SharedUsersLogs shared directory and the logout.bat script is not possible.", parent=self)


        elif not os.path.isdir(self.path1) and not os.path.isfile(self.path2) and not os.path.isfile(self.path3):
            messagebox.showerror("Error", "Access to the SharedUsersLogs shared directory and logoin/logout.bat scripts is not possible.", parent=self)

        else:
            messagebox.showerror("Error", "A problem was encountered.", parent=self)               
            return

        
        
# ---> Fonction de verification de la connectivité à la base de données
    def DbVerification(self):

    # Les données saisies sont stockés dans les variables suivante
        self.dbusername = self.db_Username.get()
        self.dbpassword = self.db_Password.get()
        self.dbIP_address = self.db_IP.get()
        self.db_name = self.db_Name.get()
     
    # Engine que la Session utilisera pour la connexion
        engine = create_engine('mysql://' + self.dbusername + ':' + self.dbpassword + '@' + self.dbIP_address + '/' + self.db_name + '')

    # Create a configured "Session" class
        Session = sessionmaker(bind=engine)

    # Create a Session
        global session
        session = Session()

    # Test de connexion
        try:
            session.query("1").from_statement(text("SELECT 1")).all()
            
        except:
            messagebox.showerror("Error", "Unable to connect to the database.", parent=self)               
            return

        else:
            messagebox.showinfo("Information", "Successful database connection!", parent=self)
            self.CreateTables()



# --->  Fonction de creation des tables dans la BDD
    def CreateTables(self):
        messagebox.showinfo("Information", "Creating tables, please wait...", parent=self)
        
        try:
            cmd1 = text("CREATE TABLE user_act(Date TEXT, Heure TEXT, Action TEXT, User TEXT, Ip TEXT, PC TEXT)")
            cmd2 = text("CREATE TABLE proxy(Date TEXT, Heure TEXT, Ip TEXT, Link TEXT)")
            session.execute(cmd1)
            session.execute(cmd2)

        except:
            messagebox.showerror("Error", "Unable to create tables.", parent=self)               
            return

        else:
            messagebox.showinfo("Good job!", "Successful table creation!", parent=self)
            self.dbState += 1
            self.db_button.config(text="Successful", command=self.AlreadyDone)
            self.db_message.config(fg="green")
            self.DbCredentialWrite()

            
            # Si toutes toutes les fonctions sont notées comme valider, on execute le final check    
            if self.sshState == 1 and self.dbState == 1 and self.shareState == 1:
                self.FinalCheck()

            # Sinon on continu
            else:
                return



# ---> Envoie des informations d'authentification BDD vers le script qui sera utilisé comme tache planifiée
    def DbCredentialWrite(self):

    # Si le fichier credentials existe deja on supprime le contenu pour le mettre à jour
        if os.path.isfile(r"Taches_auto\sql_credentials.py"):           
            with open("Taches_auto\sql_credentials.py", 'w') as f:
                f.write('db_name = ' + '"' + self.db_name + '"\n')
                f.write('db_IP_address = ' + '"' + self.dbIP_address + '"\n')
                f.write('db_password = ' + '"' + self.dbpassword + '"\n')
                f.write('db_username = ' + '"' + self.dbusername + '"\n')
                f.close()

            
    # Sinon
        else:           
            with open("Taches_auto\sql_credentials.py", 'w+') as f:
                f.write('db_name = ' + '"' + self.db_name + '"\n')
                f.write('db_IP_address = ' + '"' + self.dbIP_address + '"\n')
                f.write('db_password = ' + '"' + self.dbpassword + '"\n')
                f.write('db_username = ' + '"' + self.dbusername + '"\n')
                f.close()

   

# ---> Fonction de verification de la connexion à PfSense via SSH
    def SshVerification(self):
        self.rootpassword = self.pf_Root.get()
        self.sshusername = self.pf_Username.get()
        self.sshpassword = self.pf_Password.get()
        self.sshIP_address = self.pf_IP.get()
        
        try:
            cmdSSH = "ls -l"
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.sshIP_address, username=self.sshusername, password=self.sshpassword)
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmdSSH)

        except:
            messagebox.showerror("Error", "Unable to connect to PfSense via SSH.", parent=self)               
            return


        else:
            messagebox.showinfo("Good job!", "Successful connection to PfSense!", parent=self)
            self.pf_button.config(text="Successful", command=self.AlreadyDone)
            self.pf_message.config(fg="green")
            self.sshState += 1
            self.SshCredentialWrite()


            # Si toutes toutes les fonctions sont notées comme valider, on execute le final check    
            if self.sshState == 1 and self.dbState == 1 and self.shareState == 1:
                self.FinalCheck()

            # Sinon on continu
            else:
                return


            
# ---> Envoie des informations d'authentification à Pfsense vers le script qui sera utilisé comme tache planifiée
    def SshCredentialWrite(self):

    # Si le fichier credentials existe deja on supprime le contenu pour le mettre à jour
        if os.path.isfile(r"Taches_auto\proxy_credentials.py"):           
            with open("Taches_auto\proxy_credentials.py", 'w') as f:
                f.write('ssh_IP_address = ' + '"' + self.sshIP_address + '"\n')
                f.write('ssh_password = ' + '"' + self.sshpassword + '"\n')
                f.write('ssh_username = ' + '"' + self.sshusername + '"\n')
                f.write('root_password = ' + '"' + self.rootpassword + '"\n')
                f.close()

            
    # Sinon
        else:           
            with open("Taches_auto\proxy_credentials.py", 'w+') as f:
                f.write('ssh_IP_address = ' + '"' + self.sshIP_address + '"\n')
                f.write('ssh_password = ' + '"' + self.sshpassword + '"\n')
                f.write('ssh_username = ' + '"' + self.sshusername + '"\n')
                f.write('root_password = ' + '"' + self.rootpassword + '"\n')
                f.close()





# ---> Fonction liée au boutons "réussi" pour eviter de reecrire les informations (ssh, bdd et dossier partagé)
    def AlreadyDone(self):
        messagebox.showinfo("Information", "All the parameters related to this part have already been filled in", parent=self)




# ---> Check final - On verifie si les script qui doivent etre utilisés par les taches plannifiés sont bien accessible
    def FinalCheck(self):
        messagebox.showinfo("Good job!", "All information is correct! One last check and you will be done with the configuration of this application:)  ", parent=self)


    # Style utilisé sur le bouton "réssayer la verification finale" qui s'affiche en cas d'echec
        style4 = ttk.Style()
        style4.configure("Rb.TButton", background="#343434", width=30, font=('Century Gothic',11))


    # Test de l'accessibilité des scripts. Message d'erreur en fonction de l'accessiblité de chacun
        if os.path.isfile("Taches_auto\csv_to_sql.py") and os.path.isfile("Taches_auto\proxy.py"):
            messagebox.showinfo("Good job again!", "You can close this window (setup.py) and you will be able to use the search engine once data will have been recorded by the different scheduled tasks.", parent=self)
            self.welcomeLabel.config(fg="green")



    # Si le script csv_to_sql.py est introuvable mais que proxy.py existe
        elif os.path.isfile("Taches_auto\csv_to_sql.py") and not os.path.isfile("Taches_auto\proxy.py"):
            
        # Message d'erreur
            messagebox.showerror("Error", "Unable to find the proxy.py script in the Tasks_auto folder..", parent=self)

        # Changement de couleur pour le message principal de la fenetre
            self.welcomeLabel.config(fg="red", font=('Century Gothic',13,'underline'))
            self.welcomeLabel.grid(row=1, pady=(15,20))

        # Creation d'un bouton pour réessayer la validation
            self.retry_button = ttk.Button(self.top_frame, text="Try the final validation", style="Rb.TButton", command=self.FinalCheck)
            self.retry_button.grid(row=2, pady=(10, 30))



    # Si le script csv_to_sql.py est introuvable mais que proxy.py existe
        elif not os.path.isfile("Taches_auto\csv_to_sql.py") and os.path.isfile("Taches_auto\proxy.py"):

        # Message d'erreur
            messagebox.showerror("Error", "Unable to find the script csv_to_sql.py in the Tasks_auto folder.", parent=self)

        # Changement de couleur pour le message principal de la fenetre
            self.welcomeLabel.config(fg="red", font=('Century Gothic',13,'underline'))
            self.welcomeLabel.grid(row=1, pady=(15,20))

        # Creation d'un bouton pour réessayer la validation
            self.retry_button = ttk.Button(self.top_frame, text="Try the final validation", style="Rb.TButton", command=self.FinalCheck)
            self.retry_button.grid(row=2, pady=(10, 30))



    # Si csv_to_sql.py et proxy.py sont introuvables
        elif not os.path.isfile("Taches_auto\csv_to_sql.py") and not os.path.isfile("Taches_auto\proxy.py"):
            
        # Message d'erreur
            messagebox.showerror("Error", "Unable to find the scripts csv_to_sql.py and proxy.py in the Tasks_auto folder.", parent=self)

        # Changement de couleur pour le message principal de la fenetre
            self.welcomeLabel.config(fg="red", font=('Century Gothic',13,'underline'))
            self.welcomeLabel.grid(row=1, pady=(15,20))

        # Creation d'un bouton pour réessayer la validation
            self.retry_button = ttk.Button(self.top_frame, text="Try the final validation", style="Rb.TButton", command=self.FinalCheck)
            self.retry_button.grid(row=2, pady=(10, 30))

            
        
# --- App ---#
app = MainW(None)
app.mainloop()
