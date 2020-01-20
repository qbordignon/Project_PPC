import socket
from tkinter import *
from threading import Thread
import signal
import os
import sys

client = None
txt_data = ""

def play_card(card):
    global client
    print("Clicked - " + card.get())
    client.send(card.get().encode())

def handle_notifications():
    global txt_data
    while True:
        print("Waiting - Data from server")
        data = client.recv(4096)
        txt_data = data.decode()
        if txt_data == "":
            os.kill(os.getpid(), signal.SIGTERM)
            sys.exit(1) # FERMER LE CLI PROPREMENT
        


if __name__ == '__main__':

    # Ouverture fenêtre de jeu
    window = Tk()

    # Paramètres fenêtre
    window.title("FREAKOUT !")
    window.geometry("1080x720")
    window.minsize(700, 500)
    window.config(background='#114020')

    state = StringVar()
    feedback = StringVar()
    card1 = StringVar()
    card2 = StringVar()
    card3 = StringVar()
    card4 = StringVar()
    card5 = StringVar()
    card6 = StringVar()
    card7 = StringVar()
    card8 = StringVar()
    cards = (card1, card2, card3, card4, card5, card6, card7, card8)

    top = Frame(window, bg='#114020')
    middle = Frame(window, bg='#114020')
    bottom = Frame(window, bg='#114020')
    top.pack(side=TOP)
    middle.pack()
    bottom.pack(side=BOTTOM, fill=BOTH, expand=True)

    # create the widgets for the top part of the GUI,
    # and lay them out
    label_state = Label(window, textvariable=state, font=("Helvetica", 40), bg='white')
    label_state.pack()
    label_state.pack(in_=top)

    label_feedback = Label(window, textvariable=feedback, pady=50, font=("Helvetica", 30), bg='#114020')
    label_feedback.pack()
    label_feedback.pack(in_=middle)

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
    card_button1.pack(in_=bottom, side=LEFT, expand=True)
    card_button2.pack(in_=bottom, side=LEFT, expand=True)
    card_button3.pack(in_=bottom, side=LEFT, expand=True)
    card_button4.pack(in_=bottom, side=LEFT, expand=True)
    card_button5.pack(in_=bottom, side=LEFT, expand=True)
    card_button6.pack(in_=bottom, side=LEFT, expand=True)
    card_button7.pack(in_=bottom, side=LEFT, expand=True)
    card_button8.pack(in_=bottom, side=LEFT, expand=True)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('0.0.0.0', 8080))

    print("Get ready to FREAKOUT !!!")

    notification_t = Thread(target=handle_notifications, args=())
    notification_t.start()

    feedback.set("Jouez !")

    while True:
        array_data = txt_data.split(" ")
        if len(array_data) > 0:
            txt_state = array_data[0]
            state.set(txt_state)
            array_hand = array_data[1:]
            i = 0
            while i < len(cards):
                if i < len(array_hand):
                    cards[i].set(array_hand[i])
                else:
                    cards[i].set("")
                i+=1
        # Affichage fenêtre
        window.update()

    client.close()