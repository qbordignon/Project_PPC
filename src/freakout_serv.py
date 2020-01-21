# Serveur de jeu Freakout !
# Auteurs : Quentin Bordignon & Alexandre Onfray

from multiprocessing import Process, Lock, Manager, Value
from player import Player
from card import *
import sysv_ipc
import sys
import socket
from threading import Thread, Timer
import os
import signal

bmqkey = 699 # Clé de connexion à la file de messages du board
ID_LAST_PLAYER = 0 # Identifiant du dernier joueur créé

# Fonction d'envoi de la mise à jour de la carte du milieu à chaque joueur
def board_updater(finished, board, pmqueues):
    for m in pmqueues:
        m.send(str(board).encode())


# Fonction de rafraîchissement du plateau de jeu
def update(finished, board, pmqueues, bmqueue, new_board):
    global timer
    while not finished:
        if new_board:
            board_t = Thread(target=board_updater, args=(finished, board, pmqueues))
            board_t.start()
            new_board = False

        # print("Waiting - Card from player")
        message, t = bmqueue.receive()
        timer.cancel()
        timer = Timer(10, timeout, [pmqueues])
        timer.start()
        data = message.decode()
        array = data.split(" ")
        if len(array) > 1:
            player_id = int(array[1])
            card = string_to_card(array[0])
            if confirm(board, card):
                board = card
                # print("new board !")
                new_board = True
            else:
                data = "draw"
                message = data.encode()
                pmqueues[player_id - 1].send(data)


# Fonction permettant de valider ou d'invalider un coup
# On ne peut joueur qu'une carte de valeur identique ou une carte de même couleur et voisine en valeur (0 est voisin de 9)
def confirm(board, card):
    return (board.value == card.value or (((int(board.value) - 1) % 10 == int(card.value) or (int(board.value) + 1) % 10 == int(card.value)) 
        and board.color == card.color))

# Fonction gérant la connexion d'un client au serveur
# Crée un processus Player et une file de messages pour chaque client
def connection_handler(conn, board, winner, draw, mutex, players, pmqueues):
    global ID_LAST_PLAYER
    global bmqkey

    ID_LAST_PLAYER += 1
    player = Player(conn, winner, board, draw, mutex, ID_LAST_PLAYER, bmqkey)
    players.append(player)

    try:
        pmqueues.append(sysv_ipc.MessageQueue(100 + player.id, sysv_ipc.IPC_CREX))
    except sysv_ipc.ExistentialError:
        print("Message queue", 100 + player.id, "already exists, terminating.")
        return -1

    player.start()


# Fonction gérant la fermeture du serveur de jeu
def shutdown(connections, pmqueues, bmqueue):
    key = ''
    while key != 'q':
        key = str(input("Input q to shutdown server.\n"))

    # Fermeture des connexions
    for conn in connections:
        conn.close()

    # Fermeture des queues de message
    for mq in pmqueues:
        mq.remove()
    bmqueue.remove()

    os.kill(os.getpid(), signal.SIGINT)
    sys.exit(1) # FERMER LE SERV PROPREMENT

# Fonction gérant l'expiration du compte à rebours du jeu
# Si le compte à rebours arrive à 0, chaque joueur pioche une carte
def timeout(pmqueues):
    global timer
    message = "draw"
    for q in pmqueues:
        q.send(message.encode())
    timer = Timer(10, timeout, [pmqueues])
    timer.start()

if __name__ == "__main__" :
    # Manager permettant le partage de la pioche entre les processus Player et le serveur
    with Manager() as manager:
        # Crée la pioche
        draw = manager.list(generate_draw())
        # Verrou pour accès à la pioche
        mutex = Lock()
        # Bool de fin de partie
        winner = Value("i", 0)

        # Indicateur de fin de partie
        finished = False
        #Indicateur de changement de carte (au milieu)
        new_board = False
        
        # Liste des connexions ouvertes par le serveur
        connections = []
        # Liste des processus Players lancés par le serveur
        players = []
        # Liste des files de messages ouvertes depuis le serveur vers les processus Player
        pmqueues = []

        # Initialise le board 
        board = draw.pop(0)
        new_board = True

        # Ouverture de la file de messages vers le serveur
        bmqueue = None
        try:
            bmqueue = sysv_ipc.MessageQueue(bmqkey, sysv_ipc.IPC_CREX)
        except sysv_ipc.ExistentialError:
            print("Message queue", bmqkey, "already exists, terminating.")
            sys.exit(1)

        # Thread d'extinction du serveur
        sd = Thread(target=shutdown, args=(connections, pmqueues, bmqueue))
        sd.start()

        # Compte à rebours de la partie
        timer = Timer(10, timeout, [pmqueues])
        timer.start()

        # Thread de rafraîchissement de l'état du jeu
        refresh = Thread(target=update, args=(finished, board, pmqueues, bmqueue, new_board))
        refresh.start()

        conn_nbr = 0 # Compteur de connexions
        # Ouverture socket et écoute sur port 8080
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv.bind(('0.0.0.0', 8080))
        serv.listen(5)
        # Boucle acceptant toute nouvelle connexion en démarrant un processus Player pour chaque
        while True:
            conn, addr = serv.accept()
            connections.append(conn)
            conn_nbr += 1
            print("Client " + str(conn_nbr) + " connected.")
            # Thread de gestion de la connexion (Lancement du Player, ouverture d'une file de message)
            handler = Thread(target=connection_handler, args=(conn, board, winner, draw, mutex, players, pmqueues))
            handler.start()

        # Fonction de rafrâichissement
        while not finished:
            update()

        # Attente des fils
        for p in players:
            p.join()

        # Fermeture des queues de message
        for mq in pmqueues:
            mq.remove()
        bmqueue.remove()
    