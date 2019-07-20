import tkinter as tk
import tkinter.font as tkFont
import tkinter.scrolledtext as tkst
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkcalendar import DateEntry
from tkcalendar import Calendar
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import re
import sys
import webbrowser


# -------------------- Premiere fenetre avec le choix de la date -------------------- #

class MainW(tk.Tk):
    def __init__(self, root):
        tk.Tk.__init__(self, root)

        self.MainStructure()

        self.resizable(False, False)
        self.title("Main Window")
        self.protocol("WM_DELETE_WINDOW", self.ExitMain)
        self.configure(background="#343434")

        style = ttk.Style()
        style.configure("TButton", background="#343434", width=18, font=('opensans',10))

        
    # Variable qui sera utilisée par le code pour savoir si la recherche est la premiere effectuée lors de cette instance
        global second_count, username
        second_count = 0
        username = None


# ---> Fonction executée si l'utilisateur ferme la fenetre
    def ExitMain(self):
        if  messagebox.askokcancel("Quitter", "Souhaitez-vous vraiment quitter cette application ?", parent=self) and second_count == 0:
            app.destroy()

        elif messagebox.askokcancel("Quitter", "Souhaitez-vous vraiment quitter cette application ?", parent=self) and second_count >= 1:
            SecondW.destroy(self)
            app.destroy()


# ---> Structure de la fenetre main        
    def MainStructure(self):
        
    # Les deux frames de cette même fenetre
        self.top_frame = tk.Frame(self, bg="#343434", height=50, width=320, padx=10)
        self.sep_frame = tk.Frame(self, bg="#343434", height=2, width=250, bd=1, relief="sunken")
        self.search_frame = tk.Frame(self, bg="#343434", height=100, width=320, padx=10)

    # Quelques reglage liés aux frames
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.top_frame.grid(row=1)
        self.top_frame.grid_propagate(True)

        self.sep_frame.grid(row=2)
        self.sep_frame.grid_propagate(True)

        self.search_frame.grid(row=3)
        self.search_frame.grid_propagate(True)



    # Message de "bienvenue"
        self.welcomeLabel = tk.Label(self.top_frame, bg="#343434", fg="#D2A028",
                                     text="Bienvenue sur le moteur de recherche d'activité des utilisateurs !", wrap=305, font=('Century Gothic',13))
        self.welcomeLabel.grid(row=1, pady=(15, 15))

        self.welcomeLabel2 = tk.Label(self.top_frame, bg="#343434", fg="white",
                                      text="Choisissez une date ci-dessous puis appuyez sur OK", font=('Century Gothic',11))
        self.welcomeLabel2.grid(row=2, pady=(0, 20))

        
    # Execution de la fonction suivante
        self.DateWidget()



# ---> Elements constituants la partie choix de la date
    def DateWidget(self):

    # Calendrier permetant le choix de la date
        self.cal = DateEntry(self.search_frame, width=32, year=2019, month=5, day=9, background="#343434", borderwidth=0, headersbackground="#D2A028", foreground="white", selectbackground="#D2A028",
                             selectforeground="white", font=("Century Gothic",11), justify="center")
        
        self.cal.grid(row=1, padx=10, pady=(35, 10), columnspan=2)

        
    # Bouton de validation de la recherche       
        self.ok_button = ttk.Button(self.search_frame, text="OK", command=self.ValidAction)
        self.ok_button.grid(row=2, column=0, pady=(10, 15))

    # Bouton de reinitialisation de la fenetre (au cas ou)
        self.reset_button = ttk.Button(self.search_frame, text="Reset", command=self.ResetAction)
        self.reset_button.grid(row=2, column=1, pady=(10, 15))



# ---> Fonction de reinitialisation de l'interface (liée au bouton Reset)
    def ResetAction(self):
        self.MainStructure()


# ---> Fonction executée lorsque l'on valide la recherche (liée au bouton OK)
    def ValidAction(self):

    # Pour toute nouvelle recherche, on change la commande liée au bouton qui a maintenant "Nouvelle recherche" comme label
        self.ok_button.config(text="OK", command=self.ValidAction2)

    # On passe à la fonction Chech_date
        self.CheckDate()



# ---> Fonction permettant une nouvelle recherche
    def ValidAction2(self):

        if username is None:
            messagebox.showinfo("Information", "Impossible de recuperer les informations d'authentifications à la base de données, merci de les saisir à nouveau", parent=self)
            DbW()
            

    # Si les variables username, password, IP_address et DB_name contienent bien des données
        elif password != "" and IP_address != "" and DB_name != "" and username is not None :

            # On ajoute 1 à la variable second_count pour indiquer que ce n'est pas la premiere recherche lancée
            global second_count
            second_count += 1

            # On passe à la fonction CheckDate
            self.CheckDate()


    # Si les variables indiquées ci-dessus ne contienent pas de données, il faut les saisir à nouveau
        else:
            messagebox.showinfo("Information", "Impossible de recuperer les informations d'authentifications à la base de données, merci de les saisir à nouveau", parent=self)
            DbW()




# ---> Fonction de verification de la date   
    def CheckDate(self):
        global date
        date = self.cal.get()


    # Si la date entrée correspond bien au pattern dd/jj/aaaa on exectue la commande de recherche dans la BDD    
        if re.match(r"^[Z0-9]{2}/[Z0-9]{2}/[Z0-9]{4}", date) and second_count == 0:           
            # On ouvre la deuxieme fenetre
            DbW()

         
    # Sinon si la date entrée correspond bien au pattern et que ce ne n'est pas la premiere recherche (second_count >= 1)
        elif re.match(r"^[Z0-9]{2}/[Z0-9]{2}/[Z0-9]{4}", date) and second_count >= 1:
            # On ne passe pas par la fenetre demandant les informations d'authentification à la BDD puisque cela à déja été fait
            SecondW()         

                   
    # Sinon on indique à l'utilisateur que la date n'est pas utilisable
        else:
            messagebox.showerror("Erreur", "La date entrée est inutilisable, veuillez saisir une date au format jj/mm/aaaa", parent=self)


        
# --- Fin class MainW --- #


# -------------------- Deuxieme fenetre avec les informations d'authentification à la BDD -------------------- #
class DbW(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
    # Setup graphique & titre de la fenetre
        self.resizable(False, False)
        self.title("Connexion à la base de données")
        self.configure(background="#343434")

        style = ttk.Style(self)
        style.configure("TButton", background="#343434", font=('opensans',10))

    # Envoi vers la fonction self.exit lorsque l'on ferme la fenetre
        self.protocol("WM_DELETE_WINDOW", self.ExitDbW)

    # Execution de la fonction suivante (structure de la fenetre)
        self.DbWStructure()


# ---> Fonction executée si l'utilisateur ferme la fenetre 
    def ExitDbW(self):
        self.destroy()


# ---> Structure de la fenetre DbW
    def DbWStructure(self):
        
        self.top_frame = tk.Frame(self, bg="#343434", height=50, width=340, padx=10)
        self.sep_frame = tk.Frame(self, bg="#343434", height=2, width=250, bd=1, relief="sunken")
        self.DB_frame = tk.Frame(self, bg="#343434", height=150, width=340, padx=30)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.top_frame.grid(row=1)
        self.top_frame.grid_propagate(True)

        self.sep_frame.grid(row=2)
        self.sep_frame.grid_propagate(True)

        self.DB_frame.grid(row=3)
        self.DB_frame.grid_propagate(True)
 
        self.db_message = tk.Label(self.top_frame, bg="#343434", fg="#D2A028", font=('Century Gothic',12),
                                   text="Merci de saisir l'adresse IP et les informations d'authentification à la base de données", wrap=300)
        self.db_message.grid(row=1, sticky="w", pady=(15, 15))
                          

    
    # Username
        self.db_UsernameLabel = tk.Label(self.DB_frame, bg="#343434", fg="white", font=('Century Gothic',11), text="Nom d'utilisateur")
        self.db_UsernameLabel.grid(row=1, column=0, sticky="w", padx=(0,10), pady=(30,0))

        self.db_Username = ttk.Entry(self.DB_frame, font=('opensans',11), justify="center")
        self.db_Username.grid(row=1, column=1, pady=(30,0), padx=(10,0))


    # Password
        self.db_PasswordLabel = tk.Label(self.DB_frame, bg="#343434", fg="white", font=('Century Gothic',11), text="Mot de passe")
        self.db_PasswordLabel.grid(row=2, column=0, sticky="w", padx=(0,10), pady=(10,0))

        self.db_Password = ttk.Entry(self.DB_frame, show="*", font=('opensans',11), justify="center")
        self.db_Password.grid(row=2, column=1, pady=(10,0), padx=(10,0))

        
    # Ip address
        self.db_IpLabel = tk.Label(self.DB_frame, bg="#343434", fg="white", font=('Century Gothic',11), text="Adresse IP")
        self.db_IpLabel.grid(row=3, column=0, sticky="w", padx=(0,10), pady=(10,0))

        self.db_IP = ttk.Entry(self.DB_frame, font=('opensans',11), justify="center")
        self.db_IP.grid(row=3, column=1, pady=(10,0), padx=(10,0))


    # DB name
        self.db_NameLabel = tk.Label(self.DB_frame, bg="#343434", fg="white", font=('Century Gothic',11), text="Nom de la BDD")
        self.db_NameLabel.grid(row=4, column=0, sticky="w", padx=(0,10), pady=(10,0))

        self.db_Name = ttk.Entry(self.DB_frame, font=('opensans',11), justify="center")
        self.db_Name.grid(row=4, column=1, pady=(10,0), padx=(10,0))


    # Bouton valider       
        self.db_button = ttk.Button(self.DB_frame, text="Valider", command=self.ValidAction)
        self.db_button.grid(row=5, columnspan=2, pady=(35,25))


# ---> Fonction liée au bouton valider
    def ValidAction(self):
        global username, password, IP_address, DB_name

    # Les données saisies sont stockés dans les variables suivante
        username = self.db_Username.get()
        password = self.db_Password.get()
        IP_address = self.db_IP.get()
        DB_name = self.db_Name.get()

    # On passe à la fonction suivante
        self.CheckDbConnection()
        

# ---> Verification de la connexion à la BDD avec les informations d'authentifications fournies
    def CheckDbConnection(self):
        
    # Engine que la Session utilisera pour la connexion
        engine = create_engine('mysql://' + username + ':' + password + '@' + IP_address + '/' + DB_name + '')

    # Create a configured "Session" class
        Session = sessionmaker(bind=engine)

    # Create a Session
        global session
        session = Session()

    # Test de connexion
        try:
            session.query("1").from_statement(text("SELECT 1")).all()
            messagebox.showinfo("Information", "Connexion à la base de données réussi", parent=self)
            
            # On ouvre la fenetre avec les resultats
            SecondW()

            # On ferme la fenetre DbW
            DbW.destroy(self)

            
        except:
            messagebox.showerror("Erreur", "Impossible de se connecter à la base de données", parent=self)               
            return
        
# --- Fin class DbW --- #
    
    


# -------------------- Troisieme fenetre avec les resultats précis -------------------- #

class SecondW(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

    # Setup graphique & titre de la fenetre
        self.resizable(False, False)
        self.title("Résultats")
        self.configure(background="#343434")

        style = ttk.Style(self)
        style.configure("TButton", background="#343434", font=('opensans',10))

    # Variable qui sera utilisée pour les création des boutons utilisateurs
        self.bttn_clicks = 0

    # Envoi vers la fonction self.exit lorsque l'on ferme la fenetre
        self.protocol("WM_DELETE_WINDOW", self.ExitSecondW)
   
    # Execution des fonctions annexes (menu de l'application, structure de la fenetre, partie résultat et creation des boutons cliquable pour chacun des users
        self.MenuWidget()
        self.SecondWStructure()
        self.ResultatsStructure()
        self.Search()


# --->  Action lorsque l'on essaye de quitter la fenetre
    def ExitSecondW(self):
        if  messagebox.askokcancel("Quitter", "Souhaitez-vous vraiment quitter cette application ?", parent=self):
            self.destroy()
            app.destroy()
            

# ---> Menu de l'application
    def MenuWidget(self):
        menuBar = tk.Menu(self)

    # Premiere partie du menu nommée : File
        menuFile = tk.Menu(menuBar, tearoff=0)
        menuFile.add_command(label="Nouvelle recherche", command=self.NewSearch)
        menuFile.add_command(label="Quitter", command=self.ExitSecondW)


    # Deuxieme partie du menu nommée : Options
        menuOptions = tk.Menu(menuBar, tearoff=0)
        menuOptions.add_command(label="Montrer le code")


    # Troisieme partie du menu nommée : Help
        menuHelp = tk.Menu(menuBar, tearoff=0)
        menuHelp.add_command(label="A propos de cette application", command=self.GoToGit)
        menuHelp.add_command(label="GitHub", command=self.GoToGit)


    # Ajout des 3 parties au menu
        menuBar.add_cascade(label="Fichiers", menu=menuFile)
        menuBar.add_cascade(label="Options", menu=menuOptions)
        menuBar.add_cascade(label="Aide", menu=menuHelp)
        self.config(menu=menuBar)

        
# ---> Fonctions liées au menu de l'application

    # Nouvelle recherche
    def NewSearch(self):      
        SecondW.destroy(self)
       

    # Go to git
    def GoToGit(self):
        webbrowser.open('https://github.com')



# ---> Structure de la deuxieme fenetre (SecondW)
    def SecondWStructure(self):

    # Creation des 5 frames de cette fenetre
        global top_frame2, result_frame2, output_frame2, information_frame2, export_frame2

        top_frame2 = tk.Frame(self, bg="#343434", height=50, pady=5, padx=10)
        sep1_frame2 = tk.Frame(self, bg="#343434", height=2, width=550, bd=1, relief="sunken")
        result_frame2 = tk.Frame(self, bg="#343434", height=150, width=500, pady=5, padx=10)
        output_frame2 = tk.Frame(self, bg="#343434", height=50, width=500, pady=5, padx=10)
        export_frame2 = tk.Frame(self, bg="#343434", height=50, width=500, padx=5, pady=10)
        sep2_frame2 = tk.Frame(self, bg="#343434", height=2, width=900, bd=1, relief="sunken")
        information_frame2 = tk.Frame(self, bg="#343434", height=50)


    # Quelques reglage liés aux frames
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        top_frame2.grid(row=1, stick="n")
        top_frame2.grid_propagate(True)

        sep1_frame2.grid(row=2)
        sep1_frame2.grid_propagate(True)
       
        result_frame2.grid(row=3)
        result_frame2.grid_propagate(True)

        output_frame2.grid(row=4)
        output_frame2.grid_propagate(True)

        export_frame2.grid(row=5)
        export_frame2.grid_propagate(True)

        sep2_frame2.grid(row=6)
        sep2_frame2.grid_propagate(False)
        
        information_frame2.grid(row=7)
        information_frame2.grid_propagate(True)



# ---> Elements constituants la partie resultats       
    def ResultatsStructure(self):

    # Les messages d'informations de la partie resultats
        self.infoLabel1 = tk.Label(top_frame2, bg="#343434", fg="#D2A028", font=('Century Gothic',12), text="Vous trouverez ci-dessous les noms des utilisateurs connectés le " + date)
        self.infoLabel1.grid(row=1, column=0, pady=(15,10))

        self.infoLabel2 = tk.Label(top_frame2, bg="#343434", fg="white", font=('Century Gothic',11), text="Cliquez sur l'un des boutons pour afficher l'historique de navigation de l'utilisateur sélectionné")
        self.infoLabel2.grid(row=2, column=0, pady=(0,20))


    # La text box dans laquelle est redirigé le texte qui est normalement imprimé dans la console
        self.resultatsTxt = tkst.ScrolledText(output_frame2, height=15, width=72, wrap="word", bg="#ababab", fg="#333333" , font=("Century Gothic",11))
        self.resultatsTxt.grid(row=1, sticky="w", padx=10, pady=10)
        self.resultatsTxt.tag_configure("stderr", foreground="#b22222")


    # La partie redirection
        sys.stdout = TextRedirector(self.resultatsTxt, "stdout")
        sys.stderr = TextRedirector(self.resultatsTxt, "stderr")
        

    # La partie information (tout en bas de la fenetre)
        self.infoLabe3 = tk.Label(information_frame2, bg="#343434", fg="white", font=('Century Gothic',9), text="Information : si un nom d'utilisateur apparaît plusieurs fois, cela indique qu'il s'est connecté à plusieurs reprises à la date sélectionnée")
        self.infoLabe3.grid(row=1, column=0, pady=5, padx=10)



                                           
# ---> Action executée si date saisie correspond au pattern
    def Search(self):

    # Si la date contient bien des données, on execute la requete contenue dans cmd
        if date != "":

        # Requete avec laquelle on recheche les utilisateur (User) connectés (Login) à la date selectionnée (stockés dans x)
            #cmd = text("SELECT User FROM activity.user_act WHERE Action Like '%Login%' AND Date = :x group by User")
            #print("DB NAME", DB_name)
            cmd = text("SELECT User FROM " + DB_name + ".user_act WHERE Action Like '%Login%' AND Date = :x group by User")
            cmd = cmd.bindparams(x=date)
            result = session.execute(cmd)

        # Si un ou plusieurs utilisateurs étaient connectés, on créer un bouton pour chacun d'entres eux
            if result.rowcount >= 1:
                rowcount = 2
                columncount = 1
                but_strings = ['But1']
                
                for row in result:
                    for label in but_strings:
                        self.button_n = ttk.Button(result_frame2, text=row[0])
                        self.button_n.grid(row=rowcount, column=columncount, padx=10, pady=(15,10))
                        self.button_n.bind('<Button-1>', self.PressedButton)

                       
                    while columncount <= 6:
                        columncount += 1
                        break
                      
                        if columncount == 6:
                            rowcount += 1
                            columncount = 1
                            break


        # Si personne n'était connecté, on indique qu'aucun utilisateur n'était connecté à $date  
            elif result.rowcount == 0:
                a = "Aucun utilisateur connecté le "
                b = date
                c = a + "" + b
                messagebox.showinfo("Information", c, parent=self)
                SecondW.destroy(self)
                

        # Si result ne contient aucune donnée à cause d'un probleme de connection à la BDD
            else:
                print("Un problème a été rencontré")

                


# ---> Capture du nom d'utilisateur lié au bouton sur lequel on a cliqué 
    def PressedButton(self, event):

    # Cette fonction est executée seulement si l'on appui le bouton d'un des utilisateurs qui etaient connecté, la variable bttn_clicks passe donc de 0 à 1
        self.bttn_clicks += 1


    # Grace à la fonction event.widget et w.cget("text"), on recupere le nom d'utilisateur lié au bouton sur lequel on viens de cliquer
        global selectedUser
        w = event.widget
        selectedUser = w.cget("text")
        print("L'utilisateur sélectionné est :", selectedUser)
        print("Merci de patienter...")
        print("Requête en cours...")
        print("")
        print("*********************************************************")
        print("")


    # Quand on aura cliqué sur l'un des boutons, de nouveaux boutons personnalisés apparaissent (exportation et nouvelle recherche)
        if self.bttn_clicks == 1:
            self.exportButton1 = ttk.Button(export_frame2, text="Exporter l'historique de " + selectedUser, command=self.Export)
            self.exportButton1.grid(row=1, column=0, pady=(10,20), padx=10)

            self.newSearchButton1 = ttk.Button(export_frame2, text="Faire une nouvelle recherche", command=self.NewSearch)
            self.newSearchButton1.grid(row=1, column=1, pady=(10,20), padx=10)


            
    # Si bttn_clicks n'est pas égale à 1, cela veut dire que l'on à deja cliqué au moins une fois sur l'un des boutons
        elif self.bttn_clicks > 1:

        # On detruit alors les boutons export personnalisés pour les recréer
            self.exportButton1.destroy()
            self.newSearchButton1.destroy()

        # Pour eviter toute erreur, on efface le contenu de la text box (dans laquelle l'historique de l'utilisateur precedent avait été affichée)
            self.ResetTxt()
            self.bttn_clicks -= 1

        # On capture à nouveau le nom d'utilisateur lié au bouton cliqué
            w = event.widget
            selectedUser = w.cget("text")
            print("L'utilisateur sélectionné est :", selectedUser)
            print("Merci de patienter...")
            print("Requête en cours...")
            print("")
            print("*********************************************************")
            print("")

            
            self.exportButton1 = ttk.Button(export_frame2, text="Exporter l'historique de " + selectedUser, command=self.Export)
            self.exportButton1.grid(row=1, column=0, pady=(10,20), padx=10)

            self.newSearchButton1 = ttk.Button(export_frame2, text="Faire une nouvelle recherche", command=self.NewSearch)
            self.newSearchButton1.grid(row=1, column=1, pady=(10,20), padx=10)


    # Execution de la fonction MultiCheck
        self.CheckMultiSearch()



# ---> Fonction d'exportation 
    def Export(self):
        self.filename = ""
        self._filetypes = [("Text", "*.txt"),("All files", "*")]
        
        self.filename = filedialog.asksaveasfilename(defaultextension='.txt', filetypes = self._filetypes)
        f = open(self.filename, "w")
        f.write(self.resultatsTxt.get("1.0", "end"))
        f.close()
        messagebox.showinfo("Information", "Fichier enregistré", parent=self)


        
# ---> Fonction qui permet de clear la text box
    def ResetTxt(self):
        self.resultatsTxt.configure(state='normal')
        self.resultatsTxt.delete(1.0, tk.END)
        self.resultatsTxt.configure(state='disabled')



# ---> Fonction de verification : Single search = 1 seule connexion de l'utilisateur dans la journée / Multi search = plusieurs connexion de l'utilisateur dans la même journée
    def CheckMultiSearch(self):
        global user
        user = selectedUser

    # On verifie pour l'utilisateur selectionné, les actions de Login
        cmd = text("SELECT Heure FROM " + DB_name + ".user_act WHERE User Like :b AND Action Like '%Login%' AND Date Like :a")
        cmd = cmd.bindparams(a=date)
        cmd = cmd.bindparams(b=user)
        result = session.execute(cmd)

    # Si un seul resultat est trouvé on passe sur la fonction SingleSearch
        if result.rowcount == 1:
            print("Recherche simple...")
            print("En cours...")
            SingleSearch()
                          
    # Si plusieurs résultats sont trouvés on passe sur la fonction MultipleSearch
        elif result.rowcount >= 2:
            print("Session multiple trouvée...")
            print("Recherche de toutes les informations en cours...")
            MultiSearch()
       
    # Si aucun résultat n'est trouvé, il doit y avoir un probleme
        else:
            print("Un problème a été rencontré")

# --- Fin class SecondW --- #


        

# -------------------- Class SingleSearch -------------------- #

class SingleSearch():
    def __init__(self):
        self.SearchLoginHeure()


        
# ---> Fonction de recuperation de l'heure de connexion
    def SearchLoginHeure(self):
        cmd = text("SELECT Heure FROM " + DB_name + ".user_act WHERE User Like :b AND Action Like '%Login%' AND Date Like :a")
        cmd = cmd.bindparams(a=date)
        cmd = cmd.bindparams(b=user)
        result = session.execute(cmd)
            
        if result.rowcount == 1:
            for row in result:
                global login_heure
                login_heure = row[0]
                print("Heure de connexion trouvée :", login_heure)
                self.SearchLogoutHeure()

        else:
            print("Un problème a été rencontré")



# ---> Fonction de recuperation de l'heure de deconnexion
    def SearchLogoutHeure(self):
        cmd = text("SELECT Heure FROM " + DB_name + ".user_act WHERE User Like :b AND Action Like '%Logout%' AND Date Like :a")
        cmd = cmd.bindparams(a=date)
        cmd = cmd.bindparams(b=user)
        result = session.execute(cmd)

        if result.rowcount == 1:
            for row in result:
                global logout_heure
                logout_heure = row[0]
                print("Heure de deconnexion trouvée :", logout_heure)
                self.SearchIp()

        else:
            print("Un problème a été rencontré")



# ---> Fonction de recuperation de l'IP
    def SearchIp(self):    
        cmd = text("SELECT Ip FROM " + DB_name + ".user_act WHERE User Like :b AND Action Like '%Login%' AND Date Like :a")
        cmd = cmd.bindparams(a=date)
        cmd = cmd.bindparams(b=user)
        result = session.execute(cmd)

        if result.rowcount == 1:
            for row in result:
                global ip_selected
                ip_selected = row[0]
                print("Adresse IP du poste :", ip_selected)
                print("")
                print("*********************************************************")
                print("")
                self.SearchHistorique()



# ---> Fonction de recherche de l'historique de l'utilisateur
    def SearchHistorique(self):    
        cmd = text("SELECT * FROM " + DB_name + ".proxy WHERE Date Like :a AND Ip Like :d AND Heure BETWEEN :b AND :c")
        
    # On prend en compte les informations trouvées ci-dessus (date, heure de login, heure de logout et ip)
        cmd = cmd.bindparams(a=date)
        cmd = cmd.bindparams(b=login_heure)
        cmd = cmd.bindparams(c=logout_heure)
        cmd = cmd.bindparams(d=ip_selected)
        result = session.execute(cmd)


    # Ici on demande d'imprimer l'heure de navigation, l'IP du poste ainsi que l'URL visitée
        if result.rowcount >= 1:
            for row in result:
                print(row[1], row[2], row[3])


    # Si aucune réponse à la requete, cela veut dire que user c'est bien connecté mais n'a pas été sur internet
        elif result.rowcount == 0:
            print("Aucun activité trouvée le", date, "avec l'adresse IP", ip_selected, "pour l'utilisateur", user)


    # Si result ne contient aucune donnée c'est qu'un probleme a été rencontré
        else:
             print("Un problème a été rencontré")



# --- Fin class SingleSearch --- #

        

# -------------------- Class MultiSearch -------------------- #     
class MultiSearch():
    def __init__(self):
        
        global session_count
        session_count = 0
        self.SearchMultiLogin()


# ---> Fonction de recuperation des heures de connexion
    def SearchMultiLogin(self):
        cmd = text("SELECT Heure FROM " + DB_name + ".user_act WHERE User Like :b AND Action Like '%Login%' AND Date Like :a")
        cmd = cmd.bindparams(a=date)
        cmd = cmd.bindparams(b=user)
        self.result1 = session.execute(cmd)
        self.SearchMultiLogout()

        
# ---> Fonction de recuperation des heures de deconnexion
    def SearchMultiLogout(self):
        cmd = text("SELECT Heure FROM " + DB_name + ".user_act WHERE User Like :b AND Action Like '%Logout%' AND Date Like :a")
        cmd = cmd.bindparams(a=date)
        cmd = cmd.bindparams(b=user)
        self.result2 = session.execute(cmd)
        self.SearchMultiIp()


# ---> Fonction de recuperation des IP
    def SearchMultiIp(self):
        cmd = text("SELECT Ip FROM " + DB_name + ".user_act WHERE User Like :b AND Action Like '%Login%' AND Date Like :a")
        cmd = cmd.bindparams(a=date)
        cmd = cmd.bindparams(b=user)
        self.result3 = session.execute(cmd)


    # La variable rows_amount sera égale au nombre de connexion trouvée dans SearchMultiLogin
        rows_amount = self.result1.rowcount


    # Boucle permettant de recuperer les informations retournées precedement (heure de login, heure de lougout et ip)
        for row in self.result1, self.result2, self.result3:


        # Si la variable rows_amount est égale à zero cela veut dire la derniere session trouvée a été imprimée
            if rows_amount == 0:
                print("")
                print("")
                print("******************* Fin des resultats *******************")
                break


        # Sinon, on capture le premier résultat de chaque requete SQL. On retire les possibles caracteres speciaux pour pouvoir exploiter les données
            else:
                                
                login_heure = str(self.result1.fetchone())
                login_heure = re.sub('[\(\)\{\}\'\<>,]', '', login_heure)
                
                logout_heure = str(self.result2.fetchone())
                logout_heure = re.sub('[\(\)\{\}\'\<>,]', '', logout_heure)
                
                ip_selected = str(self.result3.fetchone())
                ip_selected = re.sub('[\(\)\{\}\'\<>,]', '', ip_selected)


            # Impression des resultats dans la text box
                global session_count
                session_count += 1
                print("")
                print("------------------------------")
                print("")
                print("Heure de connexion trouvée :", login_heure)
                print("Heure de deconnexion trouvée :", logout_heure)
                print("Adresse IP du poste :", ip_selected)
                rows_amount -= 1


            # Recherche de l'historique pour cette session
                cmd = text("SELECT * FROM " + DB_name + ".proxy WHERE Date Like :a AND Ip Like :d AND Heure BETWEEN :b AND :c") 
                cmd = cmd.bindparams(a=date)
                cmd = cmd.bindparams(b=login_heure)
                cmd = cmd.bindparams(c=logout_heure)
                cmd = cmd.bindparams(d=ip_selected) 
                result = session.execute(cmd)


            # Impression de l'heure, de l'ip du poste ainsi que des URL visitées
                print("Voici l'historique de", user, "pour cette session", session_count, ":")
                print("")
                for row in result:
                    print(row[1], row[2], row[3])
                

        
            
# -------------------- Redirection du texte vers la text box "resultatsTxt" -------------------- #
class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        
        self.widget = widget
        self.tag = tag


    def write(self, str):
        
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.configure(state="disabled")       

# --- Fin class TextRedirector --- #



# --- App ---#
app = MainW(None)
app.mainloop()
