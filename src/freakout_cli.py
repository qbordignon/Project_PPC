import socket
from tkinter import *
from threading import Thread
import signal
import os
import sys
import time

ending_messages = ["Gagné!", "Perdu..."]
array_data = []
finished = False

def play_card(card):
    global client
    # print("Clicked - " + card.get())
    client.send(card.get().encode())

def handle_notifications(client):
    global array_data
    global ending_messages
    global finished
    while not finished:
        # print("Waiting - Data from server")
        data = client.recv(4096)
        txt_data = data.decode()
        if txt_data == "":
            os.kill(os.getpid(), signal.SIGTERM)
            sys.exit(1) # FERMER LE CLI PROPREMENT
        array_data = txt_data.split(" ")
        if len(array_data) > 1:
            if array_data[1] in ending_messages:
                finished = True

if __name__ == '__main__':
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('0.0.0.0', 8080))

    # Ouverture fenêtre de jeu
    window = Tk()

    # Paramètres fenêtre
    window.title("FREAKOUT !")
    window.geometry("1080x720")
    window.minsize(700, 500)
    window.config(background='#300400')

    board = StringVar()
    feedback = StringVar()
    card1 = StringVar()
    card2 = StringVar()
    card3 = StringVar()
    card4 = StringVar()
    card5 = StringVar()
    card6 = StringVar()
    card7 = StringVar()
    card8 = StringVar()
    card9 = StringVar()
    card10 = StringVar()
    cards = (card1, card2, card3, card4, card5, card6, card7, card8, card9, card10)

    top = Frame(window, bg='#300400')
    middle = Frame(window, bg='#300400')
    bottom = Frame(window, bg='#300400')
    top.pack(side=TOP)
    middle.pack()
    bottom.pack(side=BOTTOM, fill=BOTH, expand=True)

    # create the widgets for the top part of the GUI,
    # and lay them out
    label_board = Label(window, textvariable=board, font=("Helvetica", 40), bg='white')
    label_board.pack()
    label_board.pack(in_=top)

    label_feedback = Label(window, textvariable=feedback, pady=150, font=("Helvetica", 30), bg='#300400', fg='white')
    label_feedback.pack()
    label_feedback.pack(in_=middle)

    # create the widgets for the bottom part of the GUI,
    # and lay them out
    # create the widgets for the bottom part of the GUI,
    # and lay them out
    card_button1 = Button(window, textvariable=card1, command=lambda : play_card(card1), font=("Helvetica", 30), bg='white', fg='black')
    card_button2 = Button(window, textvariable=card2, command=lambda : play_card(card2), font=("Helvetica", 30), bg='white', fg='black')
    card_button3 = Button(window, textvariable=card3, command=lambda : play_card(card3), font=("Helvetica", 30), bg='white', fg='black')
    card_button4 = Button(window, textvariable=card4, command=lambda : play_card(card4), font=("Helvetica", 30), bg='white', fg='black')
    card_button5 = Button(window, textvariable=card5, command=lambda : play_card(card5), font=("Helvetica", 30), bg='white', fg='black')
    card_button6 = Button(window, textvariable=card6, command=lambda : play_card(card6), font=("Helvetica", 30), bg='white', fg='black')
    card_button7 = Button(window, textvariable=card7, command=lambda : play_card(card7), font=("Helvetica", 30), bg='white', fg='black')
    card_button8 = Button(window, textvariable=card8, command=lambda : play_card(card8), font=("Helvetica", 30), bg='white', fg='black')
    card_button9 = Button(window, textvariable=card9, command=lambda : play_card(card9), font=("Helvetica", 30), bg='white', fg='black')
    card_button10 = Button(window, textvariable=card10, command=lambda : play_card(card10), font=("Helvetica", 30), bg='white', fg='black')
    buttons = (card_button1, card_button2, card_button3, card_button4, card_button5, card_button6, card_button7, card_button8, card_button9, card_button10)

    for b in buttons:
        b.pack(in_=bottom, side=LEFT, expand=True)

    print("Get ready to FREAKOUT !!!")

    notification_t = Thread(target=handle_notifications, args=(client,))
    notification_t.start()

    feedback.set("Jouez !")

    while True:
        if len(array_data) > 0:
            board.set(array_data[0])
            if len(array_data) > 1:
                if finished:
                    feedback.set(array_data[1])
                    for c in cards:
                        c.set("  ")
                    window.update()
                    notification_t.join()
                    time.sleep(5)
                    client.close()
                    window.destroy()
                    sys.exit(1)
                else:
                    array_hand = array_data[1:]
                    i = 0
                    while i < len(cards):
                        if i < len(array_hand):
                            cards[i].set(array_hand[i])
                        else:
                            cards[i].set("  ")
                        i+=1
        # Affichage fenêtre
        window.update()
