import socket
from threading import Thread
from tkinter import *


def display(state, hand):
    print(state)
    print(hand)
    print("Jouez!")

if __name__ == '__main__':
    
    # Ouverture fenêtre de jeu
    window = Tk()

    # Paramètres fenêtre
    window.title("FREAKOUT !")
    window.geometry("1080x720")
    window.minsize(700, 500)
    window.config(background='#114020')

    state = StringVar()

    frame = Frame(window, bg="#114020")

    label_state = Label(frame, textvariable=state, font=("Helvetica", 40), bg='white')
    label_state.pack()

    card_button1 = Button(frame, text="Carte 1", font=("Helvetica", 30), bg='white', fg='black')
    card_button1.pack(pady=25, fill=X)

    frame.pack(expand=YES)
    

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('0.0.0.0', 8080))

    print("Get ready to FREAKOUT !!!")

    while True:
        # Affichage fenêtre
        window.update()
        state.set(client.recv(4096).decode())
        hand = client.recv(4096).decode()
        #display_t = Thread(target = display, args = (state,hand))
        #display_t.start()

    client.close()
    print(from_server)
    print(hand)