import random

colors = ["R", "B"]
values = range(1, 11)

# Classe représentant une carte
class Card():
    def __init__(self, value, color):
        self.value = value
        self.color = color

    def __str__(self):
        return self.value + self.color

    def __eq__(self, card):
        return (self.value == card.value and self.color == card.color)

# Fonction permettant de générer une pioche, ici 40 cartes (bleues, rouges, vertes et jaunes)
def generate_draw():
    draw = []
    for i in range(0, 10):
        draw.append(Card(str(i), "R"))
        draw.append(Card(str(i), "B"))
        draw.append(Card(str(i), "J"))
        draw.append(Card(str(i), "V"))
    random.shuffle(draw)
    return draw

# Fonction de construction d'une carte à partir d'une chaine de caractère la décrivant (best effort)
def string_to_card(string):
        return Card(string[0], string[1])
