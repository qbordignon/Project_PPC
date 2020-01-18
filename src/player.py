
import signal
import time
import sys
from multiprocessing import Process
from threading import Thread
import sysv_ipc
# import socket
import subprocess
import os
from card import string_to_card
import tkinter

k = -1

class Player(Process):
    def __init__(self, conn, draw, mutex, id, bmq_key):
        super().__init__()
        self.conn = conn
        self.mutex = mutex
        self.draw = draw
        self.id = id
        self.bmq_key = bmq_key
        self.board_mq = sysv_ipc.MessageQueue(self.bmq_key)

        self.hand = []
        for i in range(0,5):
            self.draw_card()

    def draw_card(self):
        self.hand.append(self.draw.pop(0))

    def handler_int(self, sig, frame):
        if sig == signal.SIGINT:
            if len(self.hand) == 0:
                print("Victoire")
            else:
                print("Défaite")
            time.sleep(5)
            sys.exit()

    def notify(self, state):
        self.conn.send(str(state).encode())
        str_hand = ""
        for c in self.hand:
            str_hand += str(c) + "   "
        self.conn.send(str_hand.encode())
        '''
        print("Main :")
        for c in self.hand:
            print(c, end=' ')
        print("")
        nums = ""
        for i in range(1, len(self.hand) + 1):
            nums += (" " + str(i))
        print(nums)
        print("Jouez !")
        '''

    def next_move(self):
        global k
        print("Entrez la position de la carte à jouer: ")
        k = -1
        while k < 1 and k >= len(self.hand):
            try:
                k = int(input("> "))
            except ValueError:
                print("Invalide, un entier était attendu")
        os.kill(os.getpid(), signal.SIGCHLD)

        
    def handler_chld(self, sig, frame):
        if sig == signal.SIGCHLD:
            global k
            data = str(self.hand[k - 1]) + " " + str(self.id)
            message = data.encode()
            self.board_mq.send(message)



    def run(self):
    # "gnome-terminal"]).pid
        # print(pid)
        signal.signal(signal.SIGINT, self.handler_int)
        signal.signal(signal.SIGCHLD, self.handler_chld)
        my_mq = sysv_ipc.MessageQueue(100 + self.id)

        while True:
            #while my_mq.empty():
            #    continue
            message, t = my_mq.receive()
            data = message.decode()
            print(data)
            if bool(data) == False:
                self.draw_card()
            else:
                state = string_to_card(data)
                for c in self.hand:
                    if c == state:
                        hand.remove(c)
            
            notify_t = Thread(target = self.notify, args = (state,))
            notify_t.start()
            time.sleep(5)
            '''
            play_t = Thread(target=self.next_move)
            play_t.start()
            '''

            # k = None # LA CARTE SELECTIONNEE

            # with mutex:
            #    mq.send(self.hand[k-1])

            #Libération des autres process sans qu'ils ne jouent

            notify_t.join()