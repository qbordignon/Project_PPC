
import signal
import time
import sys
from multiprocessing import Process
from threading import Thread
import sysv_ipc
import subprocess
import os
from card import string_to_card

class Player(Process):
    def __init__(self, conn, winner, state, draw, mutex, id, bmq_key):
        super().__init__()
        self.conn = conn
        self.winner = winner
        self.state = state
        self.mutex = mutex
        self.draw = draw
        self.id = id
        self.bmq_key = bmq_key
        self.board_mq = sysv_ipc.MessageQueue(self.bmq_key)

        self.hand = []
        for i in range(0,5):
            self.draw_card()

    def draw_card(self):
        if len(self.draw) > 0:
            with self.mutex:
                self.hand.append(self.draw.pop(0))


    # Envoie l'état de la partie au client sous la forme {[Carte du Milieu][Main du joueur]}
    def notify(self):
        message = str(self.state)
        if self.winner.value:
            if self.winner.value == self.id:
                message += " Gagné!"
            else:
                message += " Perdu..."
            self.conn.send(message.encode())
            self.conn.close()
            os.kill(os.getppid(), signal.SIGTERM)
            os.kill(os.getpid(), signal.SIGTERM)

        else:
            for c in self.hand:
                message += " " + str(c)
            self.conn.send(message.encode())
    
    def next_move(self):
        while True:
            # print("Waiting - Player's move")
            from_client = self.conn.recv(4096)
            card = from_client.decode()
            data = str(card) + " " + str(self.id)
            # print("Card Played & id " + data)
            self.board_mq.send(data.encode())

    def run(self):

        my_mq = sysv_ipc.MessageQueue(100 + self.id)

        play_t = Thread(target=self.next_move)
        play_t.start()

        notify_t = Thread(target = self.notify, args = ())
        notify_t.start()

        while True:
            # print("Waiting - State from board")
            message, t = my_mq.receive()
            data = message.decode()
            if data == "draw":
                # print("Warning - Board didn't accept last move.")
                self.draw_card()
                notify_t = Thread(target = self.notify, args = ())
                notify_t.start()
            else:
                new_state = string_to_card(data)
                if new_state != self.state:
                    self.state = new_state
                    if self.state in self.hand:
                        self.hand.remove(self.state)
                    if len(self.hand) == 0:
                        with self.mutex:
                            self.winner.value = self.id
                    notify_t = Thread(target = self.notify, args = ())
                    notify_t.start()

