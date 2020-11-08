
# _init_.py
# --------------------------------------------------------------------------

# Player Array:
# 
# UnoPlugin.players = [
#	[player_index]:{
#			"nick":[player_nick],
#			"hand":[player_hand]
#		}
# ]

# Cards are divided up as follows in a new deck:
# 19 Blue Cards (1 x b0, 2 x b1-b9)
# 19 Green Cards (1 x g0, 2 x g1-g9)
# 19 Red Cards (1 x r0, 2 x r1-r9)
# 19 Yellow Cards (1 x y0, 2 x y1-y9)
# 8 Draw Two cards (2 in each colour)
# 8 Reverse Cards (2 in each colour)
# 8 Skip Cards (2 in each colour)
# 4 Wild Cards
# 4 Wild Draw 4 cards

import random
import Plugin
import DeeIRC.Utils as Utils

# ------- Constants ------------------------------------------------------------

UNO_STATE_STOPPED = 0
UNO_STATE_STARTING = 1
UNO_STATE_STARTED = 2

# ------------------------------------------------------------------------------


class UnoPlugin(Plugin.Plugin):
	
	# Onload Setup.
	def load(self, bot):
		
		# Uno turns bot on.
		self.addCommand("uno", self.commandUno)
		
		# Join allows players to join the current game.
		self.addCommand("join", self.commandJoin)
		
		# Stop the current game.
		self.addCommand("stop", self.commandStop)
		
		# Deal initiates the current game.
		self.addCommand("deal", self.commandDeal)
		
		# Play sets cards into play.
		self.addCommand("play", self.commandPlay)
		self.addCommand("p", self.commandPlay)
		
		# Draw card draws a card to the players deck.
		self.addCommand("draw", self.commandDraw)
		self.addCommand("d", self.commandDraw)
		
		# Pass turn.
		self.addCommand("pass", self.commandPass)
		
		# Show hand to player.
		self.addCommand("cards", self.commandCards)
		self.addCommand("hand", self.commandCards)
		
		# Display top card.
		self.addCommand("top", self.commandTop)
		
		# Display current turn
		self.addCommand("turn", self.commandTurn)
		
		# Admin Commands
		self.addCommand("admin", self.commandAdmin)
		
		# Admin Commands
		self.addCommand("help", self.commandHelp)
		self.addCommand("commands", self.commandHelp)
		
		# Set default states.
		self.state = UNO_STATE_STOPPED
		self.deck = None
		self.pile = None
		self.channel = None
		self.players = None
		self.turn_index = None
		self.reverse = False
		self.last_card = False
		self.gameowner = None
		self.canpass = False
		
# ----------------------------------------------------------------------------------
# ------- Command Handlers ---------------------------------------------------------
# ----------------------------------------------------------------------------------
	
	# commandUno() - Begins a new game of Uno.
		# - Checks is game is running.
		# - Creates a new deck, shuffles it.
		# - Creates a new pile.
		# - Sets up the channel target.
		# - Sets current state to UNO_STATE_STARTING
		# - Announces game started.
		# - Set the current user to the game owner.
		# - Add the current player to the game.
	
	def commandUno(self, bot, nick, target, message):
		
		# Confirm no game in progress.
		if self.state == UNO_STATE_STOPPED:
			
			# Start Uno by initalizing the deck and pile.
			self.deck = self.createDeck()
			self.shuffleDeck(self.deck)
			self.pile = []
			
			# Setup the plugin for starting.
			self.channel = target
			self.state = UNO_STATE_STARTING
			
			# Print some messages.
			bot.sendMessage(target, nick + " has created a game lobby for Uno. Players can now \"join\".")
			bot.sendNotice(nick, "You need to use \"deal\" when you are ready to start your game.")
			
			# Set the game's owner.
			self.gameowner = nick
			
			# Setup the players.
			self.players = []
			self.addPlayer(bot, nick)
			
			# Give HOP to owner
			self.givePlayerHop(bot, nick)
			
		# Already a game in progress.
		elif self.state == UNO_STATE_STARTING or self.state == UNO_STATE_STARTED:
			if not self.isPlayerInGame(nick):
				self.commandJoin(bot, nick, target, message)
			else:
				bot.sendNotice(nick, "You are already in the current game.")
	
	# commandJoin() - Allows player to join the current game.
		# - Checks game is in progress.
		# - Checks the player is not in the game.
		# - Adds the player to the game.
	
	def commandJoin(self, bot, nick, target, message):
		
		# Check there is a game in progress.
		if self.state == UNO_STATE_STARTING or self.state == UNO_STATE_STARTED:
		
			# Confirm they are not in the game.
			if not self.isPlayerInGame(nick):
				
				# Add then to the game.
				self.addPlayer(bot, nick)
				
				# Give voice to players
				self.givePlayerVoice(bot, nick)
				
			else:
				bot.sendNotice(nick, "You are already in the game.")
		else:
			bot.sendNotice(nick, "There is no current game, you can create one using \"uno\".")
	
	# commandDeal() - Starts the game by dealing cards.
		# - Checks game is in lobby state.
		# - Deals cards to the players.
	
	def commandDeal(self, bot, nick, target, message):
		
		# Check this is the owner or is an admin.
		if self.gameowner == nick or bot.isAdmin(nick):
			
			# Check if game in lobby
			if self.state == UNO_STATE_STARTING:
				
				# Deal the cards.
				self.unoStartGame(bot)
				
			# In progress or not started.
			elif self.state == UNO_STATE_STOPPED or self.state == UNO_STATE_STARTED:
				
				# Cant deal now.
				bot.sendNotice(nick, "You can't do that now.")
			
		else:
			bot.sendNotice(nick, "You need to be the owner of the game to start it.")
	
	
	# commandPlay() - Allows a player to play a card.
		# - Confirm a game is in progress.
		# - Confirm the player specified a card.
		# - Check if it is their turn.
		# - Check if they played a wild card, and confirm they have it.
		# - Check if they played a normal card, and confirm they have it.
		# - Remove the card from their hand, and add it to the pile.
		# - Update the top card reference.
		# - Set their turn to played.
		# - Announce what card was played.
		# - Check for winning player.
		# - Announce amount of cards remaining.
		# - Continue to next players turn.
	
	def commandPlay(self, bot, nick, target, message):
		
		# Confirm game is in progress.
		if self.state == UNO_STATE_STARTED:
			
			# Confirm a card is played.
			if message:
				
				# make it lower case.
				message = message.lower()
				
				# strip whitespace
				message = message.strip()
				
				# Get the current player
				player_index = self.turn_index
				player = self.players[player_index]
				
				# Make sure that it's the players turn.
				if player["nick"] == nick:
						
						turn_played = False
						
						# if the first letter is w
						if message[0] == "w":
							
							# Wild draw 4 and confirm they have it
							if message[1:3] == "d4" and "wd4" in player["hand"]:
								
								color = message[4:5]
								
								if self.isValidColor(color):
									
									# Remove the card from the player.
									self.removeCardFromHand(player_index, "wd4")
									
									# Draw four. Get the next player.
									next_player_index = self.getNextPlayerIndex()
									next_player = self.players[next_player_index]
									
									# Place 4 cards in next players hand
									self.drawCards(next_player_index, 4)
									
									# Print a message and send the player their hand.
									bot.sendMessage(target, next_player["nick"] + " draws four cards.")
									self.sendPlayerHand(bot, next_player_index)
									
									# Top of pile.
									self.last_card = color
									bot.sendMessage(target, "Top card is now: " + self.cardString(self.last_card))
									
									# Skip next players turn.
									self.skipTurn()
										
									# mark that we played a turn.
									turn_played = True
									
								else:
									bot.sendNotice(nick, "Please specify a colour.")
								
							# wild normal
							elif "w" in player["hand"]:
								
								color = message[2:3]
								
								# Check for valid color
								if self.isValidColor(color):
									
									# Remove the card from the the palyer
									self.removeCardFromHand(player_index, "w")
									
									# Top of pile.
									self.last_card = color
									bot.sendNotice(nick, "Top card is now: " + self.cardString(self.last_card))
									
									# We did indeed play a turn.
									turn_played = True
								else:
									bot.sendNotice(nick, "Please specify a colour.")
							else:
								bot.sendNotice(nick, "You don't have that card!")
						
						elif len(message) >= 2:
							
							
							## when playing a card on top of a wildcard at the start of the game with no color
							#   File "/data/bot/Plugin/Uno/__init__.py", line 290, in commandPlay
							#     if message[0] == self.last_card[0] or message[1] == self.last_card[1] or self.last_card == "w" or self.last_card == "wd4":
							# IndexError: string index out of range
							
							# wild_card = False
							# if len(self.last_card) == 1:
							# 	bot.sendMessage(target, " error case? CAUTE!")	
							# 	wild_card = True
								
							if self.last_card == "w" or self.last_card == "wd4" or message[0] == self.last_card[0] or message[1] == self.last_card[1]:
								
								# Make sure the player actually has that card.
								if message in player["hand"]:
									
									# Reverse Card
									if message[1] == "r":
										
										# Reverse play
										self.reverse = not self.reverse
										
									# Skip Card
									elif message[1] == "s":
									
										# Skip. Get the next player.
										next_player = self.players[self.getNextPlayerIndex()]
										
										# Print out a message.
										bot.sendMessage(target, next_player["nick"] + " skips their turn.")	
											
										# Skip their turn.
										self.skipTurn()
										
									# Draw Two Card
									elif message[1:3] == "d2":
										
										# Draw two.	Get the next player.
										next_player_index = self.getNextPlayerIndex()
										next_player = self.players[next_player_index]
										
										# Move the cards from the deck to the player's hands.
										self.drawCards(next_player_index, 2)
										
										# Print a message and send the player their hand.
										bot.sendMessage(target, next_player["nick"] + " draws two cards.")
										self.sendPlayerHand(bot, next_player_index)
											
										# Skip the turn.
										self.skipTurn()
										
									# Remove the card from the player's hand.
									self.removeCardFromHand(player_index, message)
									
									# Set top card
									self.last_card = message
									
									# Yep.
									turn_played = True
								else:
									bot.sendNotice(nick, "You don't have that card!")
							else:
								bot.sendNotice(nick, "You can't play that card!")
						
						else:
								bot.sendNotice(nick, "Please specify a proper colour.")
						
						# Send a message to the channel and send the player's hand.
						if turn_played:
							
							# Card played.
							bot.sendMessage(target, player["nick"] + " played " + self.cardString(self.last_card)+".")
							
							# A player just won!
							if len(player["hand"]) == 0:
								
								# Print out messages to the channel.
								bot.sendMessage(self.channel, nick + " has won the game!")
								bot.sendMessage(self.channel, "\o/ " + nick + "\o/ ")
								bot.sendMessage(self.channel, "/o/ " + nick + "/o/ ")
								bot.sendMessage(self.channel, "\o\ " + nick + "\o\ ")
								bot.sendMessage(self.channel, "/o/ " + nick + "/o/ ")
								bot.sendMessage(self.channel, "\o\ " + nick + "\o\ ")
								
								# Reset the uno game.
								self.resetUno(bot)
								
							else:
								
								# Cards remaining!
								bot.sendMessage(target, nick + " now has "+str(len(player["hand"]))+" cards left.")
								
								# Send players hand.
								self.sendPlayerHand(bot, player_index)
								
								# Run the next turn.
								self.doTurn(bot)
				else:
					bot.sendNotice(nick, "It's not your turn!")
			else:
				bot.sendNotice(nick, "Please choose a card to play.")
		else:
			bot.sendNotice(nick, "There is no game in progress.")
	
	# commandDraw() - Allows a player to draw a card.
		# - Confirm a game is in progress.
		# - Check the user has not already drawn a card.
		# - Make sure it's this players turn.
		# - Add card to players hand.
		# - Announce they drew a card.
		# - Send their hand.
		# - Allow them to pass.
	
	def commandDraw(self, bot, nick, target, message):
		
		# Make sure game in progress.
		if self.state == UNO_STATE_STARTED:
			
			# Get the current player and card.
			player = self.players[self.turn_index]
			player_index = self.turn_index
			
			# Check if drawn card.
			if self.canpass == False:
				
				# Make sure it's the player using the command.
				if player["nick"] == nick:
					
					# Move the cards from the deck to the player's hand.
					self.moveCards(self.deck, player["hand"], 1)
					
					# Send a message to the channel and send the player's hand.
					bot.sendMessage(target, player["nick"] + " drew a card. They now have "+str(len(player["hand"]))+" cards.")
					
					# Send players hand.
					self.sendPlayerHand(bot, player_index)
					
					# They can now pass.
					self.canpass = True
			
			else:
				bot.sendNotice(nick, "You cannot draw another card, you must either play or \"pass\".")
		else:
			bot.sendNotice(nick, "There is no game in progress.")
	
	# commandPass() - Allows a player to pass their turn.
		# - Confirm a game is in progress.
		# - Checks they are allowed to pass.
		# - Checks it is their turn.
		# - Announce they passed.
		# - Continue to the next player.
	
	def commandPass(self, bot, nick, target, message):
		
		# Check for game in progress.
		if self.state == UNO_STATE_STARTED:
			
			# Check if drawn card.
			if self.canpass == True:
				
				# Get the current player and card.
				player = self.players[self.turn_index]
				player_index = self.turn_index
				
				# Make sure it's the player using the command.
				if player["nick"] == nick:
					
					# Pass turn.
					bot.sendMessage(self.channel, nick + " passed their turn.")
					
					# Can no longer pass.
					self.canpass = False
					
					# Next turn.
					self.doTurn(bot)
					
			else:
				bot.sendNotice(nick, "You need to \"draw\" a card first.")
		else:
			bot.sendNotice(nick, "There is no game in progress.")
	
	# commandStop() - Allows the games owner to stop the game.
		# - Confirm a game is in progress.
		# - Confirm they are the owner.
		# - Reset the game.
		# - Announce game ended.
	
	def commandStop(self, bot, nick, target, message):
		
		# Game in progress
		if self.state == UNO_STATE_STARTED or self.state == UNO_STATE_STARTING:
			
			# Check this is the owner or is an admin.
			if self.gameowner == nick or bot.isAdmin(nick):
				
				# Reset Game
				self.resetUno(bot)
					
				# Print a message.
				bot.sendMessage(target, nick + " stopped the current game.")
				
			else:
				bot.sendNotice(nick, "You need to be the owner of the game to stop it.")
				
		# No game in progress
		elif self.state == UNO_STATE_STOPPED:
			bot.sendNotice(nick, "There is no current game.")
	
	# commandCards() - Message a user their cards.
		# - Confirm a game is in progress.
		# - Confirm the player is in the current game.
		# - Get the players index.
		# - Message them their cards.
	
	def commandCards(self, bot, nick, target, message):
		
		# Make sure we are in game
		if self.state == UNO_STATE_STARTED:
			
			# Make sure they are in the game.
			if self.isPlayerInGame(nick):
				
				# Get their index
				player_index = self.getIndexForNick(nick)
				
				# Send hand
				self.sendPlayerHand(bot, player_index)
				
			else:
				bot.sendNotice(nick, "You are not in this game.")
		else:
			bot.sendNotice(nick, "There is no current game.")
	
	# commandTop() - Announce the top card.
		# - Confirm a game is in progress.
		# - Announce the top card.
	
	def commandTop(self, bot, nick, target, message):
		
		# Check if we're in a game
		if self.state == UNO_STATE_STARTED:
			
			# Send top card
			bot.sendMessage(target, "Top card: " + self.cardString(self.last_card))
	
	# commandTurn() - Announce who's turn it is.
		# - Confirm a game is in progress.
		# - Announce the current turn.
	
	def commandTurn(self, bot, nick, target, message):
		
		# Check if we're in a game
		if self.state == UNO_STATE_STARTED:
			
			player = self.players[self.turn_index]
			
			# Send top card
			bot.sendMessage(target, "It's currently " + player["nick"] + "'s turn!")
		
		else:
			bot.sendNotice(nick, "No game in progress.")
		
	
	
	# commandHelp() - Send player help message.
		# - Message the player the help messages.
	
	def commandHelp(self, bot, nick, target, message):
		bot.sendMessage(target, "PMing help message to " + nick)
		bot.sendNotice(nick, "UnoBot v0.3 Alpha")
		bot.sendNotice(nick, "")
		bot.sendNotice(nick, "-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")
		bot.sendNotice(nick, "")
		bot.sendNotice(nick, "uno")
		bot.sendNotice(nick, "- Creates a new game lobby if none already exist.")
		bot.sendNotice(nick, "")
		bot.sendNotice(nick, "join")
		bot.sendNotice(nick, "- Join the current game lobby.")
		bot.sendNotice(nick, "")
		bot.sendNotice(nick, "deal")
		bot.sendNotice(nick, "- Once enough players have joined, this starts the game.")
		bot.sendNotice(nick, "")
		bot.sendNotice(nick, "play <card> [color]")
		bot.sendNotice(nick, "- Play a card, color is optional for wild cards, and should be only a single letter.")
		bot.sendNotice(nick, "")
		bot.sendNotice(nick, "draw / d")
		bot.sendNotice(nick, "- If you cannot play a card, you can use this command to draw a card.")
		bot.sendNotice(nick, "")
		bot.sendNotice(nick, "pass")
		bot.sendNotice(nick, "- Once you have drawn a card, you may pass your turn.")
		bot.sendNotice(nick, "")
		bot.sendNotice(nick, "hand")
		bot.sendNotice(nick, "- Shows your current hand.")
		bot.sendNotice(nick, "")
		bot.sendNotice(nick, "top")
		bot.sendNotice(nick, "- Display the top card of the pile.")
		bot.sendNotice(nick, "")
		bot.sendNotice(nick, "-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")
	
	# commandAdmin() - Admin Commands.
	
	def commandAdmin(self, bot, nick, target, message):
		
		# Confirm there is an action
		if message:
			 
			# Confirm admin.
			if bot.isAdmin(nick):
					
					# if the first letter is w
					if message == "die":
						exit()
						
			else:
				bot.sendNotice(nick, "You are NOT a bot admin.")
		else:
			bot.sendNotice(nick, "Invalid Command.")
	
	
# ----------------------------------------------------------------------------------
# ------- Uno Functions ------------------------------------------------------------
# ----------------------------------------------------------------------------------
	
	# unoStartGame() - Start the game.
	def unoStartGame(self, bot):
		
		# Confirm we are in lobby mode.
		if self.state == UNO_STATE_STARTING:
			
			# Check we have enough players.
			if len(self.players) >= 2:
			
				# Set the game to started.
				self.state = UNO_STATE_STARTED
				
				# Set the channel moderated
				bot.sendRaw("MODE " + self.channel + " +m")
				
				# Send the hand to each player, except the first?
				for i in range(1, len(self.players)):
					self.sendPlayerHand(bot, i)
				
				# Get one card face up.
				self.moveCards(self.deck, self.pile, 1)
				self.last_card = self.pile[0]
				
				# if the chosen top card is wild, we need a color to go with it!
				top_deck = self.cardString(self.last_card)
				if top_deck == "w" or top_deck == "wd4":
					colors = ["r", "g", "b", "y"]
					color_choice = random.choice(range(0, 3))
					self.last_card += (" " + color_choice)
					
				# Send a message
				bot.sendMessage(self.channel, "Game Started, Top Card is " + self.cardString(self.last_card))
				
				# Start the turns.
				self.doTurn(bot)
			else:
				# Not enough players.
				bot.sendMessage(self.channel, "Not enough players! Please wait for more to join.")
	
	# skipTurn() - Skips the next turn.
	def skipTurn(self):
		
		# Advances the turn index.
		self.turn_index = self.getNextPlayerIndex()
	
	# doTurn() - Initiates the current player's turn.
	def doTurn(self, bot):
		
		# Set the turn to the first player the turn index isn't set.
		if self.turn_index == None:
			
			# Reset turn index.
			self.turn_index = 0
		
		# Move on to the next player.
		else:
			self.turn_index = self.getNextPlayerIndex()
		
		# Get the current player's info.
		player = self.players[self.turn_index]
		nick = player["nick"]
		hand = player["hand"]
		
		# Cannot pass.
		self.canpass = False
		
		# Send them their hand.
		self.sendPlayerHand(bot, self.turn_index)
		
		# Print out messages to the channel.
		bot.sendMessage(self.channel, nick + "'s turn!")
	
	# resetUno() - Resets the game variables.
	def resetUno(self, bot):
		
		# Set the channel moderated
		bot.sendRaw("MODE " + self.channel + " -m")
	
		self.takePlayerHop(bot, self.gameowner)
		
		if self.players:
			for player in self.players:
				if(player is not self.gameowner):
					self.takePlayerVoice(bot, player["nick"])
		
		self.state = UNO_STATE_STOPPED
		self.deck = None
		self.channel = None
		self.players = None
		self.turn_index = None
		self.reverse = False
		self.canpass = False
		
		
# ----------------------------------------------------------------------------------
# ------- Tool Functions -----------------------------------------------------------
# ----------------------------------------------------------------------------------
	
	# isValidColor() - Check if the value is a valid card colour.
	def isValidColor(self, value):
		
		# Define colours.
		colors = ["r", "g", "b", "y"]
		
		# Check if the collor is in the array.
		if value is not None and len(value) > 0 and value in colors:
			return True
		
		# Default return false.
		return False
	
# ----------------------------------------------------------------------------------
# ------- Player Functions ---------------------------------------------------------
# ----------------------------------------------------------------------------------
	
	# addPlayer() - Adds a player to the current game.
	def addPlayer(self, bot, nick):
		
		# Check they are not already in the game.
		if not self.isPlayerInGame(nick):
			
			# Append them onto the players array, no hand.
			self.players.append({"nick":nick, "hand":[]})
			
			# Move cards into their hand.
			self.moveCards(self.deck, self.players[len(self.players)-1]["hand"])
			
			# If they are not the initiator.
			if self.gameowner is not nick:
				
				# Announce their join.
				bot.sendMessage(self.channel, nick + " has joined the game!")
	
	# sendPlayerHand() - Sends a notice to a player with their current hand.
	def sendPlayerHand(self, bot, player_index):
		
		# Get their nick and hand.
		nick = self.players[player_index]["nick"]
		hand = self.players[player_index]["hand"]
		
		# Colourize their cards.
		hand_string = self.deckString(hand)
		
		# Send the hand.
		bot.sendNotice(nick, "Hand: " + hand_string)
	
	# getNextPlayerIndex() - Returns the index of the next player.
	def getNextPlayerIndex(self, turns=1):
		
		# Loops for science!
		for i in range(turns+1):
			
			# Are we running in reverse?
			if not self.reverse:
				next_index = self.turn_index + i
			else:
				next_index = self.turn_index - i
				
			# Wrap around back to the next player.
			if next_index >= len(self.players):
				next_index = 0
			if next_index < 0:
				next_index = len(self.players) - 1
		
		# Return the player index for the next player.
		return next_index
	
	# getIndexForNick() - Returns the index of the specified nick.
	def getIndexForNick(self, nick):
		
		# Loop players, till we find the right nick.
		for index, player in enumerate(self.players):
			
			# If this is the right nick, return the index.
			if player["nick"] == nick:
				return index
	
	# isPlayerInGame() - Returns True if player is in game.
	def isPlayerInGame(self, nick):
		
		# Loop the players.
		for player in self.players:
			if player["nick"] == nick:
				return True
		
		# Defualt return false.
		return False
	
	# givePlayerVoice() - Gives the player Voice (For players)
	def givePlayerVoice(self, bot, nick):
		bot.sendAddMode(self.channel, nick, "v")
		
	# givePlayerHop() - Give a player hop (party owner)
	def givePlayerHop(self, bot, nick):
		bot.sendAddMode(self.channel, nick, "h")
		
	# takePlayerVoice() - Takes the player Voice (For players)
	def takePlayerVoice(self, bot, nick):
		bot.sendRemMode(self.channel, nick, "v")
		
	# takePlayerHop() - Take a player hop (party owner)
	def takePlayerHop(self, bot, nick):
		bot.sendRemMode(self.channel, nick, "h")
		
	
# ----------------------------------------------------------------------------------
# ------- Deck Functions -----------------------------------------------------------
# ----------------------------------------------------------------------------------
	
	# createDeck() - Generate a Uno deck.
	def createDeck(self):
		
		# Define colours.
		colors = ["r", "g", "b", "y"]
		
		# Start with an empty deck.
		deck = []
		
		# Loop for each color.
		for i in range(4):
			
			# Add one of each c0 to the deck.
			deck.append(colors[i] + "0")
			
			# Loop nine times for each number c1-c9
			for j in range(9):
				
				# Loop twice for two of each.
				for k in range(2):
					deck.append(colors[i] + str(j+1))
			
			# Two of each of these cards.
			for j in range(2):
				deck.append(colors[i] + "d2")
				deck.append(colors[i] + "s")
				deck.append(colors[i] + "r")
		
		# Four of each of these.
		for i in range(4):
			deck.append("w")
			deck.append("wd4")
		
		# Return the final deck.
		return deck
	
	# shuffleDeck() - Shuffles the specified Uno deck.
	def shuffleDeck(self, deck):
		random.shuffle(deck)
	
	# moveCards() - Moves cards from decks.
	def moveCards(self, deck_from, deck_to, amount=7):
		
		# Copy cards to second deck.
		deck_to.extend(deck_from[0:amount])
		
		# Remove from original deck.
		del deck_from[0:amount]
	
	# deckString() - Returns a string with all of the cards in the deck, colored.
	def deckString(self, deck):
		
		# Blank return string.
		deck_string = ""
		
		# For each card in the array.
		for i in range(len(deck)):
			
			# Colourize each card and append to string.
			deck_string = deck_string + self.cardString(deck[i]) + " "
		
		# Return the final deck string.
		return deck_string
	
# ----------------------------------------------------------------------------------
# ------- Card Functions -----------------------------------------------------------
# ----------------------------------------------------------------------------------
	
	# cardColorCode() - Returns the appropriate colour code for a card.
	def cardColorCode(self, card):
		
		# Define card colours.
		colors = {
			"r":{"fg":0, "bg":4}, 
			"g":{"fg":0, "bg":3},
			"b":{"fg":0, "bg":12}, 
			"y":{"fg":1, "bg":8},
			"w":{"fg":0, "bg":1}
		}
		
		if len(card) == 2:
			if card[0] == "w":
				color = colors[card[1]]
			else:
				color = colors[card[0]]
		else:
			color = colors[card[0]]
			
		# Return colourized string.
		return Utils.colorCode(**color)
	
	# cardString() - Returns the card name including colours.
	def cardString(self, card):
		return self.cardColorCode(card) + card + Utils.normalCode()
	
	# drawCards() - Draw the specified amount of cards into a players hand.
	def drawCards(self, player_index, amount=1):
		
		# Move the specified amount of cards from the desk to the players hand.
		self.moveCards(self.deck, self.players[player_index]["hand"], amount)
	
	# removeCardFromHand() - Removes a card from a players hand and puts it in the pile.
	def removeCardFromHand(self, player_index, card):
		
		# Remove the card from their hand.
		self.players[player_index]["hand"].remove(card)
		
		# Append it onto the pile.
		self.pile.append(card)
	
# ----------------------------------------------------------------------------------
# ------- Plugin loader ------------------------------------------------------------
# ----------------------------------------------------------------------------------

# Retrieve plugin instance.
__plugin_instance = None

# Get the plugin instance.
def getPluginInstance():
	global __plugin_instance
	
	# Create new instance if not defined.
	if not __plugin_instance:
		__plugin_instance = UnoPlugin()
	
	# Return the instance of this plugin.
	return __plugin_instance