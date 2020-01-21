import socket
from tkinter import *
from threading import Thread
import signal
import os
import sys
import time

ending_messages = ["Gagné!", "Perdu..."] # Liste des messages de fin de partie
array_data = [] # Tableau de données reçues par le client
finished = False # Indicateur de fin de partie

# Fonction gérant l'envoi de la carte jouée au serveur (liée aux boutons de l'interface représentant les cartes du joueur)
def play_card(card):
    global client
    # print("Clicked - " + card.get())
    client.send(card.get().encode())

# Fonction gérant la réception d'une mise à jour émise par le serveur
def update(client):
    global array_data
    global ending_messages
    global finished
    while not finished:
        # print("Waiting - Data from server")
        data = client.recv(4096)
        txt_data = data.decode()
        if txt_data == "": # Si aucune donnée n'a été reçue, la connexion a été perdue et on ferme le client
            os.kill(os.getpid(), signal.SIGTERM)
            sys.exit(1) # FERMER LE CLI PROPREMENT
        array_data = txt_data.split(" ")
        if len(array_data) > 1:
            if array_data[1] in ending_messages: # A la réception d'un message de fin de partie, le jeu s'arrête
                finished = True

if __name__ == '__main__':
    # Connexion au serveur
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('0.0.0.0', 8080))

    # Ouverture fenêtre de jeu
    window = Tk()

    # Paramètres fenêtre
    window.title("FREAKOUT !")
    window.geometry("1080x720")
    window.minsize(700, 500)
    window.config(background='#004a09')

    # Variables textuelles de l'interface graphique
    board = StringVar()
    status = StringVar()
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

    # Espaces d'affichage de la fenêtre
    top = Frame(window, bg='#004a09')
    middle = Frame(window, bg='#004a09')
    bottom = Frame(window, bg='#004a09')
    top.pack(side=TOP)
    middle.pack()
    bottom.pack(side=BOTTOM, fill=BOTH, expand=True)

    # Labels de l'interface graphique (Board et Statut de la partie)
    label_board = Label(window, textvariable=board, font=("Helvetica", 40), bg='white')
    label_board.pack()
    label_board.pack(in_=top)

    label_status = Label(window, textvariable=status, pady=150, font=("Helvetica", 30), bg='#004a09', fg='white')
    label_status.pack()
    label_status.pack(in_=middle)

    # Boutons représentant les cartes de la main du joueur. Un clic déclenche la fonction play_card().
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

    # Thread gérant la réception et le traitement des données envoyées par le serveur (Process Player)
    notification_t = Thread(target=update, args=(client,))
    notification_t.start()

    status.set("Jouez !")

    while True:
        if len(array_data) > 0:
            board.set(array_data[0]) # Mise à jour du board
            if len(array_data) > 1:
                if finished: # Si la partie est terminée, mise à jour du statut affiché puis fermeture du client après 5 sec
                    status.set(array_data[1])
                    for c in cards:
                        c.set("__")
                    window.update()
                    notification_t.join()
                    time.sleep(5)
                    client.close()
                    window.destroy()
                    sys.exit(1)
                else: # Sinon, mise à jour des boutons en fonction de la main du joueur
                    array_hand = array_data[1:]
                    i = 0
                    while i < len(cards):
                        if i < len(array_hand):
                            cards[i].set(array_hand[i])
                        else:
                            cards[i].set("__")
                        i+=1
        # Affichage fenêtre
        window.update()
