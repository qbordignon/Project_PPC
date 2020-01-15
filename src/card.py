import random

colors = ["R", "B"]
values = range(1, 11)


class Card():
    def __init__(self, value, color):
        self.value = value
        self.color = color

    def is_valid(self, another_card):
        if (self.value == another_card.value) and (self.color != another_card.color):
            return True
        elif ((another_card.value == (self.value + 1)) or (another_card.value == (self.value - 1))) and (
                self.color == another_card.color):
            return True
        else:
            return False

    def __str__(self):
        return str(self.value) + self.color

    

def generate_draw():
    draw = []
    for i in range(1, 11):
        draw.append(Card(i, "R"))
    for j in range(1, 11):
        draw.append(Card(j, "B"))
    random.shuffle(draw)
    return draw

def string_to_card(string):
        return Card(string[0], string[1])


if __name__ == "__main__":
    card_1 = Card(3, "R")
    card_2 = Card(1, "R")
    print(card_1.is_valid(card_2))
    draw = generate_draw()