# ADCrossCheckSquid

ADCrossCheckSquid est un programme python permettant de recouper les informations de connexion d'un Active Directory avec les logs d'un proxy Squid. 

Ce script a vu le jour en juillet 2019 dans le but de répondre à une problématique liée à mon activité professionnelle.

## Tables des matières
- [Description du projet](#description-du-projet)
- [Scénario d'utilisation](#scénario-dutilisation)
- [Etat du projet](#etat-du-projet)
- [Configuration requise](#configuration-requise)
- [Préparation du serveur Windows](#préparation-du-serveur-windows)
	- [Installation de python](#installation-de-python)
	- [Enregistrement de l’activité Active Directory](#enregistrement-de-lactivité-active-directory)
		- [Téléchargement des scripts](#1-téléchargement-des-scripts)
		- [Création du répertoire partagé](#2-création-du-répertoire-partagé)
		- [Création des GPO](#3-création-des-gpo)
		- [Ajout des taches planifiées](#4-ajout-des-taches-planifiées)
- [Préparation de pfSense](#préparation-de-pfsense)
	- [Création du compte utilisateur SSH](#création-du-compte-utilisateur-ssh)
	- [Installation du paquet SUDO](#installation-du-paquet-sudo)
	- [Autoriser la connexion SSH](#autoriser-la-connexion-ssh)
- [Initialisation de l'application](#initialisation-de-lapplication)



## Description du projet

ADCrossCheckSquid dispose d'une interface graphique créée avec Tkinter, son fonctionnement se rapproche de celui d'un moteur de recherche. Vous entrerez une date cible et le programme vous indiquera quels étaient les utilisateurs connectés ainsi que leurs historiques de navigation respectifs. 

![enter image description here](https://adcrosschecksquid2019.s3.us-east-2.amazonaws.com/prog_1.png)

<img src="https://adcrosschecksquid2019.s3.us-east-2.amazonaws.com/prog_2.png" width="775" height="558">

> **Important** : Pour pouvoir utiliser cette application, toutes les données (historique AD et logs) devront être stockées dans une base de données (voir plus bas)
<br>

## Scénario d'utilisation

Imaginez-vous un instant.... 
Vous travaillez pour une association qui propose un accès à internet aux habitants de votre quartier.
>L'Infrastructure de cet espace numérique est constituée entre autres d'un Active Directory et d'un proxy Squid (tournant sur pfSense). 
>
Vous mettez à disposition une dizaine de PC aux habitants et chacun d'entre eux ont un compte utilisateur dans votre AD. Grace à des profils itinérants ils peuvent se connecter à n'importe laquelle des machines pour travailler. 

Un matin en arrivant au travail vous recevez un mail de votre FAI indiquant qu'un téléchargement illégal a eu lieu depuis votre connexion, 3 ou 4 mois en arrière ! Il vous demande alors de faire le nécessaire pour que cela ne se produise plus...

Vous vous remontez les manches et allez explorer plusieurs mois de log de votre proxy Squid dans l'espoir retrouver la ligne faisant référence à ce téléchargement. 
> Si vous avez de la chance vous trouverez cette ligne ! Vous sauriez alors depuis quel PC cela a eu lieu. Il faudrait alors analyser les journaux d’événement de votre AD pour savoir lequel des vos utilisateurs était connecté sur le PC au moment du téléchargement. 

Bref, c'est très long, compliqué et si vous ne concevrez pas suffisant de log c'est impossible ! Voilà donc le pourquoi du comment :)
<br><br>

## Etat du projet

A ce jour le projet est complètement fonctionnel à condition d'utiliser les composants indiqués ci-dessous et de suivre le cheminement d'installation.  
Une version compatible avec Debian/Ubuntu **pourrait** voir le jour dans les prochains mois !
<br><br>

## Configuration requise

- Un **Active Directory** fonctionnel sous Windows Server (tests effectués sous 2016)

- Un **serveur de base données avec un moteur MySQL** (et une base de données vide utilisable par cette application)

- Un **proxy** (et oui... sinon je ne vois pas trop à quoi je vais vous servir !). Comme indiqué plus haut, nous parlerons ici  de `Squid` qui tournera sous `PfSense`. 

- **Python en version 3.X** sur Windows (voir installation ci-dessous) et des paquets utilisés par le programme. 

La mise en place de tout le reste sera expliqué plus bas !
<br><br>

## Préparation du serveur Windows

###  Installation de python
- Télécharger et installer la dernière version de Python 3.X [Page de téléchargement](https://www.python.org/downloads/)

- **Attention** : veillez à bien activer l'option "Add Python 3.X to PATH" pendant l'installation (voir image ci-dessous)  
	><img src="https://adcrosschecksquid2019.s3.us-east-2.amazonaws.com/add_path.png" width="600" height="364">
<br>

- Depuis l'invite de commande Windows, installer les paquets suivants à l'aide de PIP : `tkcalendar`, `sqlalchemy`, `mysqlclient`, `paramiko` et `pandas` (voir ci-dessous).

	>Commande utilisée : `python -m pip install nom_du_package`    
	> 
	> **Information** : Si vous rencontrez une erreur lors de l'installation du paquet `mysqlclient`, vous pourrez l'installer en téléchargement le fichier approprié à votre installation [à cette adresse.](https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient) 

<br>

### Enregistrement de l'activité Active Directory

La journalisation des connexions sera effectuée grâce à deux GPO et deux scripts. Suivez les étapes suivantes pour mettre en place les différentes parties.

#### 1. Téléchargement des scripts

 - Téléchargez l'ensemble du repository GitHub au format zip puis dézipper le sur le bureau de votre contrôleur de domaine (serveur qui gère l'Active Directory et qui sera appelé DC dans ce document). 

 - Supprimez l'un des deux sous-dossiers (ENG ou FR). Vous devez alors vous retrouver un avec arborescence similaire à celle-ci. 
	> Mettre un schéma de l’arborescence des dossiers 

 - Transférez les script présents dans le dossier `Active_directory` vers le dossier  `NETLOGON` de votre DC.
 - Éditez les deux scripts et remplacez `WRITE_NAME_HERE` par le nom de votre DC. Voici un exemple pour une machine portant le nom de `AROBAZ-DC` :

	>::### DC NAME ###  
	set "DC=**AROBAZ-DC**"
	
<br>

#### 2. Création du répertoire partagé

Les scripts déplacés ci-dessous sont paramétrés pour stocker les informations dans un dossier nommé `SharedUsersLogs` qui doit être accessible à l'adresse `\\DC_NAME\SharedUsersLogs$`. Le signe $ indique que le dossier est masqué sur le réseau et n'est donc accessible que si l'on connaît son adresse exacte. 
Pour le mettre en place :

>- Sur le serveur, créez un dossier nommé `SharedUsersLogs`
>- Faites un clic droit sur ce dossier puis rendez-vous dans l'onglet `partage`  puis `partage avancé`
>- Cochez `partager ce dossier` puis ajouté le signe `$` à la fin du nom de partage. 
>- Enfin modifiez les autorisations du partage pour que vos utilisateurs puissent avoir accès (en écriture) au dossier. 

<br>

#### 3. Création des GPO

 Depuis la console `Gestion de stratégie de groupe`, créez une nouvelle GPO puis suivez les instructions suivantes. Il va de soi que la GPO que vous allez créer devra être appliquée à vos utilisateurs. 
 
 - Script d'ouverture de session :
	>Sous Windows Server 2016, la GPO est paramétrable dans Configuration utilisateur > Stratégies > Paramètres Windows. Double-cliquez sur Ouverture de session puis sur Ajouter, enfin indiquez le chemin réseau jusqu'au script `login.bat`.
	
	>Exemple de chemin réseau : **\\\AROBAZ-DC\netlogon\login.bat**


- Script de fermeture de session : 
	>Toujours sous Windows Server 2016 dans Configuration utilisateur > Stratégies > Paramètres Windows > Fermeture de session, double-cliquez sur Fermeture de session, cliquez sur Ajouter puis indiquez le chemin jusqu'au script `logout.bat`

	>Exemple de chemin réseau : **\\\AROBAZ-DC\netlogon\logout.bat**

<br>

#### 4. Ajout des taches planifiées 
 
Vous en avez bientôt fini avec la partie Windows !  Il ne vous reste plus qu'à créer deux taches planifiées pour l’exécution des scripts.
- Le premier script, `csv_to_sql`, sert à envoyer les données de connexion et de déconnexion enregistrés par la GPO vers la  table "user_act" de la base de données.
- Le second,`proxy`, se connecte à pfSense pour y récupérer les données de navigation et les envoyer vers la table "proxy" de la même BDD. 
 
 Je vous recommande de créer une tache qui s’exécutera toutes les 30 minutes pour le script `csv_to_sql`
 et une autre qui sera lancée toutes les nuits pour le script `proxy`. 

<br>**Information** : Si vous ne savez pas créer de tache planifiée, vous trouverez ci-dessous le cheminement permettant d'en créer une fonctionnelle, qui exécutera le script csv_to_sql toutes les 30 minutes. 

<br>**1.** Renseignez le nom, la description de la tache et cochez la case "Exécuter même si l'utilisateur n'est pas connecté"
><img src="https://adcrosschecksquid2019.s3.us-east-2.amazonaws.com/tache_planifiee/1.png">

<br>**2.** Dans l'onglet Déclencheurs, cliquez sur Nouveau puis renseignez les informations comme ceci
><img src="https://adcrosschecksquid2019.s3.us-east-2.amazonaws.com/tache_planifiee/3.png">

<br>**3.** Cliquez sur Actions puis Nouveau et Parcourir pour aller chercher votre script `csv_to_sql`
><img src="https://adcrosschecksquid2019.s3.us-east-2.amazonaws.com/tache_planifiee/6.png">
 
<br><br>


## Préparation de pfSense

### Création du compte utilisateur SSH

Connectez-vous à l'interface web de pfSense, rendez-vous dans `System` puis dans `User Manager` et créez votre utilisateur en l'ajoutant au groupe admin (voir ci-dessous)

> - Remplissez  au minimum les champs Username et Password 
> - Sélectionnez `admins` et enfin sur `Move to "Member of" list` (entouré en rouge)
>
>![enter image description here](https://adcrosschecksquid2019.s3.us-east-2.amazonaws.com/ssh_user.png)
<br>


### Installation du paquet SUDO
Toujours depuis l'interface web, rendez-vous dans `System` puis dans `Package manager`. Dans l'onglet `Available Packages`  vous pourrez y rechercher le paquet nommé `sudo` et l'installer. 
<br>

### Autoriser la connexion SSH
Encore une fois depuis l'interface web, rendez-vous dans `System` puis `Advanced` et cocher la case "Enable Secure Shell". 
<br><br>


## Initialisation de l'application
Pour que l'application fonctionne il vous sera nécessaire de procéder à une première initialisation. Cela s’effectuera grâce au script `setup.pyw` disponible dans le dossier que vous avez téléchargé. 

L'interface du script se présente comme suit. Pour réussir cette étape : 
- Remplissez chacune des cases en indiquant l'information demandée. Au moment de la validation plusieurs tests seront effectués, si l'un d'entre eux échoue vous serez averti par un message d'erreur. 
- Après avoir validé les trois rubriques, un check final sera effectué et vous verrez (si tout vas bien) un message de confirmation vous indiquant que vous êtes fin prêt à utiliser AdCrossCheckSquid !
<img src="https://adcrosschecksquid2019.s3.us-east-2.amazonaws.com/setup_1.png" width="561" height="596">
