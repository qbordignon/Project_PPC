class Player(Process):
	def __init__(self, draw, mutex, id):
		super.__init__()
		self.mutex = mutex
		self.draw = draw
		self.id = id
		self.hand = []
		for i in range(0,5):
			self.draw_card()

	def draw_card():
		self.hand.append(self.draw.value.popleft())

	def handler(sig, frame):
		if sig == SIGINT
		if len(self.hand) == 0 :
			print("Victoire")
		else :
			print("Défaite")
		pause(5)
		sys.exit()

	def display(state):
		print(state)
		print("Main :")
		print(self.hand)
		print(range(1, len(self.hand)))
		print("Jouez !")

	def run():
		mq = MessageQueue(self.id)
		while True:
			state, c = mq.receive() #Après premier envoi du serveur (à affiner)

			if not c:
				draw_card()

			t = Thread(target = display, args = (state,))
			t.start()
			
			k = wait_next_key_strike()

			with mutex:
				mq.send(self.hand[k-1])

			#Libération des autres process sans qu'ils ne jouent

			t.join()