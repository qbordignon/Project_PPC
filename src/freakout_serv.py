#Classe serveur

from multiprocessing import Process, Lock
# from multiprocessing.sharedctypes import *
from player import Player
from card import *
import sysv_ipc
import sys
import socket
from threading import Thread
import os
import signal

draw = []
state = None
c = True
bmqkey = 699
pmqueues = []
bmqueue = None
ID_LAST_PLAYER = 0
NB_PLAYERS = 2
finished = False
new_state = False

def state_updater():
    global state
    global pmqueues
    global finished
    for m in pmqueues:
        m.send(str(state).encode())


# Fonction de rafraîchissement
def update(finished):
    while not finished:
        global state
        global pmqueues
        global bmqueue
        global new_state
        if new_state:
            state_t = Thread(target=state_updater, args=())
            state_t.start()
            new_state = False

        print("Waiting - Card from player")
        message, t = bmqueue.receive()
        data = message.decode()
        array = data.split(" ")
        player_id = int(array[1])
        card = string_to_card(array[0])

        if confirm(state, card): # Fonction de validation à coder
            state = card
            print("new state !")
            new_state = True
        else:
            ok = False
            print("wrong move !")
            message = str(ok).encode()
            pmqueues[player_id - 1].send(message)


    

# Une fonction permettant de valider ou d'invalider un coup
def confirm(state, card):
    return (state.value == card.value or (((int(state.value) - 1) == int(card.value) or (int(state.value) + 1) == int(card.value)) and state.color == card.color))

def connection_handler(conn, draw, mutex, players, pmqueues):
    global ID_LAST_PLAYER
    global bmqkey
    global state
    ID_LAST_PLAYER += 1
    player = Player(conn, state, draw, mutex, ID_LAST_PLAYER, bmqkey)
    players.append(player)

    try:
        pmqueues.append(sysv_ipc.MessageQueue(100 + player.id, sysv_ipc.IPC_CREX))
    except sysv_ipc.ExistentialError:
        print("Message queue", 100 + player.id, "already exists, terminating.")
        return -1

    player.start()

    
    '''
    while True:
        data = conn.recv(4096)
        if not data: break
        from_client += data
        print(from_client)
        time.sleep(10)
        conn.send(b'I am SERVER\n')
    conn.close()
    print('Client ' + str(conn_nbr) + ' disconnected')
    '''

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
        

if __name__ == "__main__" :
    # Crée la pioche
    draw = generate_draw()
    # Verrou pour droit de jouer
    mutex = Lock()
    # Bool de fin de partie
    finished = False
    
    connections = []
    players = []
    pmqueues = []

    # Initialise le board 
    state = draw.pop(0)
    new_state = True

    try:
        bmqueue = sysv_ipc.MessageQueue(bmqkey, sysv_ipc.IPC_CREX)
    except sysv_ipc.ExistentialError:
        print("Message queue", bmqkey, "already exists, terminating.")
        sys.exit(1)

    sd = Thread(target=shutdown, args=(connections, pmqueues, bmqueue))
    sd.start()

    refresh = Thread(target=update, args=(finished,))
    refresh.start()

    conn_nbr = 0
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind(('0.0.0.0', 8080))
    serv.listen(5)
    while True:
        conn, addr = serv.accept()
        connections.append(conn)
        conn_nbr += 1
        print("Client " + str(conn_nbr) + " connected.")
        handler = Thread(target=connection_handler, args=(conn, draw, mutex, players, pmqueues))
        handler.start()
    # Imaginons : 2 joueurs
    '''
    
    for i in range(0, NB_PLAYERS):
        ID_LAST_PLAYER += 1
        players.append(Player(draw, mutex, ID_LAST_PLAYER, bmqkey))

    # Tableau de queues de messages (une par joueur)
    
    # Création d'une queue de message par joueur
    for p in players:
        p.start()
        try:
            pmqueues.append(sysv_ipc.MessageQueue(100 + p.id, sysv_ipc.IPC_CREX))
        except sysv_ipc.ExistentialError:
            print("Message queue", 100 + p.id, "already exists, terminating.")
            sys.exit(1)
    '''

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
    