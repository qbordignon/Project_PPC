
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

k = -1

class Player(Process):
    def __init__(self, conn, state, draw, mutex, id, bmq_key):
        super().__init__()
        self.conn = conn
        self.state = state
        self.mutex = mutex
        self.draw = draw
        for c in draw:
            print(c)
        self.id = id
        self.bmq_key = bmq_key
        self.board_mq = sysv_ipc.MessageQueue(self.bmq_key)

        self.hand = []
        for i in range(0,5):
            self.draw_card()

        print("Après pioche :")
        for c in draw:
            print(c)

    def draw_card(self):
        if len(self.draw) > 0:
            with self.mutex:
                self.hand.append(self.draw.pop(0))

    def handler_int(self, sig, frame):
        if sig == signal.SIGINT:
            if len(self.hand) == 0:
                print("Victoire")
            else:
                print("Défaite")
            sys.exit()


    # Envoie l'état de la partie au client sous la forme {[Carte du Milieu][Main du joueur]}
    def notify(self):
        str_cards = str(self.state)
        for c in self.hand:
            str_cards += " " + str(c)
        self.conn.send(str_cards.encode())
    
    def next_move(self):
        while True:
            print("Waiting - Player's move")
            from_client = self.conn.recv(4096)
            card = from_client.decode()
            data = str(card) + " " + str(self.id)
            print("Card Played & id " + data)
            self.board_mq.send(data.encode())

    def run(self):
    # "gnome-terminal"]).pid
        # print(pid)
        signal.signal(signal.SIGINT, self.handler_int)
        # signal.signal(signal.SIGCHLD, self.handler_chld)
        my_mq = sysv_ipc.MessageQueue(100 + self.id)

        play_t = Thread(target=self.next_move)
        play_t.start()

        notify_t = Thread(target = self.notify, args = ())
        notify_t.start()

        while True:
            #while my_mq.empty():
            #    continue
            print("Waiting - State from board")
            message, t = my_mq.receive()
            data = message.decode()
            if data == "False":
                print("Warning - Board didn't accept last move.")
                self.draw_card()
                notify_t = Thread(target = self.notify, args = ())
                notify_t.start()
            else:
                new_state = string_to_card(data)
                if new_state != self.state:
                    self.state = new_state
                    if self.state in self.hand:
                        self.hand.remove(self.state)
                    notify_t = Thread(target = self.notify, args = ())
                    notify_t.start()

