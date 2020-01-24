# Freakout
Projet de fin de module PPC visant à la réalisation d'un Jeu de Cartes en temps réel.

Lancement: 
Notre mise en oeuvre suit un schéma classique client/serveur tcp.
Placez-vous dans le répertoire src/ et lancez le serveur: python3 freakout_serv.py
Puis toujours depuis src/ exécutez autant de clients que vous souhaitez de joueurs pour cette partie: python3 freakout_cli.py
Une interface graphique très simple s'ouvre pour chaque client, il suffit alors de cliquer sur une carte pour la jouer.

Règles du jeu:
Notre version du jeu observe les règles suivantes
- Il se joue avec des cartes de quatre couleurs (Bleues, Rouges, Vertes et Jaunes) numérotées de 0 à 9.
- Il est possible de jouer une carte de la même couleur que celle du milieu, uniquement si sa valeur est directement voisine de celle-ci (0 et 9 sont voisins)
- Si aucun joueur ne tente un coup dans les 10 secondes imparties, chaque joueur pioche une carte.
- Si toutes les cartes de la pioche sont tirées, tous les joueurs perdent.

Réalisé par Quentin Bordignon et Alexandre Onfray
