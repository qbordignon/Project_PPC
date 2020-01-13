#Classe serveur

from multiprocessing import *
# from multiprocessing.sharedctypes import *
from player import Player
from card import *
import sysv_ipc
import sys
# import socket

draw = []
state = None
c = True

def update():
    global draw
    global state
    c = True
    for m in mqueues:
        m.send(state, c)

    # Attendre une réponse
    for m in mqueues:
        if not m.empty():
            card = m.receive()
            if is_valid(card): # Fonction de validation à coder
                state = card
                c = True
            else:
                c = False

def confirm(state, card):
    return state.value == card.value or ((state.value - 1 == card.value or state.value + 1 == card.value) and state.color == card.color)
        

if __name__ == "__main__" :
    # Unhashable type : list
    # draw = RawArray([], generate_draw())
    # mutex = RawValue(Lock, Lock())
    draw = generate_draw()

    mutex = Lock()
    finished = False
    p1 = Player(draw, mutex, 532)
    p2 = Player(draw, mutex, 867)
    players = [p1, p2]
    mqueues = []
    for p in players:
        p.start()
        try:
            mqueues.append(sysv_ipc.MessageQueue(p.id, sysv_ipc.IPC_CREX))
        except sysv_ipc.ExistentialError:
            print("Message queue", p.id, "already exists, terminating.")
            sys.exit(1)
        
    
    state = draw.pop(0)

    while not finished:
        update()

    for p in players:
        p.join()

    for mq in mqueues:
        mq.remove()