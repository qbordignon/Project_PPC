#Classe serveur

from multiprocessing import *
from multiprocessing.sharedctypes import *
from player import Player
import sysv_ipc
import sys


def update():
    for m in mqueues:
        m.send(state, c)

    # Attendre une réponse
    for m in mqueues:
        if not m.empty():
            card = m.receive()
            if confirm(card): # Fonction de validation à coder
                state = card
                c = True
            else:
                c = False

def confirm(state, card):
    return state.value == card.value or ((state.value - 1 == card.value or state.value + 1 == card.value) and state.color == card.color)
        

if __name__ == "__main__" :
    draw = RawArray([], Card.generate_draw())
    # mutex = RawValue(Lock, Lock())
    mutex = Lock()
    finished = False
    p1 = Player(draw, mutex, 532)
    p2 = Player(draw, mutex, 867)
    players = [p1, p2]
    mqueues = []
    for p in players:
        p.start()
        try:
            mqueues.append(sysv_ipc.MessageQueue(p.id, IPC_CREX))
        except ExistentialError:
            print("Message queue", key, "already exists, terminating.")
            sys.exit(1)
        
    
    state = draw.value.popleft()

    while not finished:
        update()

    for p in players:
        p.join()