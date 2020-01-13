
import signal
import time
import sys
from multiprocessing import Process
import sysv_ipc
# import socket
import subprocess


class Player(Process):
    def __init__(self, draw, mutex, id):
        super().__init__()
        self.mutex = mutex
        self.draw = draw
        self.id = id
        self.hand = []
        for i in range(0,5):
            self.draw_card()

    def draw_card(self):
        self.hand.append(self.draw.pop(0))

    def handler(self, sig, frame):
        if sig == signal.SIGINT:
            if len(self.hand) == 0:
                print("Victoire")
            else:
                print("Défaite")
            time.sleep(5)
            sys.exit()

    def display(self, state):
        print(state)
        print("Main :")
        print(self.hand)
        print(range(1, len(self.hand)))
        print("Jouez !")

    def run(self):
    # "gnome-terminal"]).pid
        # print(pid)
        mq = sysv_ipc.MessageQueue(self.id)
        while True:
                draw_card()

            t = Thread(target = display, args = (state,))
            t.start()
            
            k = wait_next_key_strike()

            with mutex:
                mq.send(self.hand[k-1])

            #Libération des autres process sans qu'ils ne jouent

            t.join()