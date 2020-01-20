from multiprocessing import Process, Lock, Manager, Value
from player import Player
from card import *
import sysv_ipc
import sys
import socket
from threading import Thread, Timer
import os
import signal

draw = []
bmqkey = 699
pmqueues = []
bmqueue = None
ID_LAST_PLAYER = 0
finished = False
new_board = False

def board_updater(board):
    global pmqueues
    global finished
    for m in pmqueues:
        m.send(str(board).encode())


# Fonction de rafraîchissement
def update(finished, board):
    while not finished:
        global pmqueues
        global bmqueue
        global new_board
        global timer
        if new_board:
            board_t = Thread(target=board_updater, args=(board,))
            board_t.start()
            new_board = False

        # print("Waiting - Card from player")
        message, t = bmqueue.receive()
        timer.cancel()
        timer = Timer(10, timeout)
        timer.start()
        data = message.decode()
        array = data.split(" ")
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


# Une fonction permettant de valider ou d'invalider un coup
def confirm(board, card):
    return (board.value == card.value or (((int(board.value) - 1) % 10 == int(card.value) or (int(board.value) + 1) % 10 == int(card.value)) and board.color == card.color))

def connection_handler(conn, winner, draw, mutex, players, pmqueues):
    global ID_LAST_PLAYER
    global bmqkey
    global board
    ID_LAST_PLAYER += 1
    player = Player(conn, winner, board, draw, mutex, ID_LAST_PLAYER, bmqkey)
    players.append(player)

    try:
        pmqueues.append(sysv_ipc.MessageQueue(100 + player.id, sysv_ipc.IPC_CREX))
    except sysv_ipc.ExistentialError:
        print("Message queue", 100 + player.id, "already exists, terminating.")
        return -1

    player.start()


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

def timeout():
    global pmqueues
    print("TIMEOUT")
    message = "draw"
    for q in pmqueues:
        q.send(message.encode())
    timer = Timer(10, timeout)
    timer.start()

if __name__ == "__main__" :
    with Manager() as manager:
        # Crée la pioche
        draw = manager.list(generate_draw())
        # Verrou pour droit de jouer
        mutex = Lock()
        # Bool de fin de partie
        winner = Value("i", 0)
        
        connections = []
        players = []
        pmqueues = []

        # Initialise le board 
        board = draw.pop(0)
        new_board = True

        try:
            bmqueue = sysv_ipc.MessageQueue(bmqkey, sysv_ipc.IPC_CREX)
        except sysv_ipc.ExistentialError:
            print("Message queue", bmqkey, "already exists, terminating.")
            sys.exit(1)

        sd = Thread(target=shutdown, args=(connections, pmqueues, bmqueue))
        sd.start()

        refresh = Thread(target=update, args=(finished, board))
        refresh.start()

        timer = Timer(10, timeout)
        timer.start()

        conn_nbr = 0
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv.bind(('0.0.0.0', 8080))
        serv.listen(5)
        while True:
            conn, addr = serv.accept()
            connections.append(conn)
            conn_nbr += 1
            print("Client " + str(conn_nbr) + " connected.")
            handler = Thread(target=connection_handler, args=(conn, winner, draw, mutex, players, pmqueues))
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
    