
# IRC.py
# --------------------------------------------------------------------------

# ------ Events
#	All events get passed the instance of the IRC framework.
#	You must add events as a static function, not an instanced one.
#
# 	connected
#	disconnected
# 	names
#		users
#		channel
#	message
#		nick
#		target
#		message
#	notice
#		nick
#		target
#		message
#	join
#		nick
#		channel
#	part
#		nick
#		channel		
#	kick
#		nick
#		kick_nick
#		channel	
#		message
#	nick
#		nick
#		new_nick
#	self_join
#		channel
#	self_part
#		channel
#	self_kick
#		nick
#		channel
#		message
#	self_nick
#		new_nick
#	unhandled
#		data
#
# ------ Data Structures
# 	DeeIRC.channels = {
#		"[channel_name]": {
#			"nicks":[list of users]
#		}
#	}

import Events
import DefaultEvents
import Utils

import socket
import threading
import datetime

# ------------------------------------------------------------------------------

class DeeIRC(object):
	"""Manages connecting to IRC and handles events."""
	
	def __init__(self, nick="UnoBot", user="UnoBot", name="Uno Game Robot"):
		"""Constructor."""
				
		self.__sock = None
		self.__sock_file = None
		
		self.nick = nick
		self.user = user
		self.name = name
		
		self.channels = {}
		self.connected = False
		
		if not "debug" in dir(self):
			self.debug = False
		
		self.__events = {
			"connected":[],
			"disconnected":[],
			"names":[],
			"message":[],
			"notice":[],
			"nick":[],
			"join":[],
			"part":[],
			"kick":[],
			"quit":[],
			"self_nick":[],
			"self_join":[],
			"self_part":[],
			"self_kick":[],
			"unhandled":[]
		}
		
		# Add our default events.
		self.addEvent("connected", DefaultEvents.DefaultConnectedEvent())
		self.addEvent("disconnected", DefaultEvents.DefaultDisconnectedEvent())
		self.addEvent("join", DefaultEvents.DefaultJoinEvent())
		self.addEvent("part", DefaultEvents.DefaultPartEvent())
		self.addEvent("kick", DefaultEvents.DefaultKickEvent())
		self.addEvent("nick", DefaultEvents.DefaultNickEvent())
		self.addEvent("quit", DefaultEvents.DefaultQuitEvent())
		self.addEvent("self_nick", DefaultEvents.DefaultSelfNickEvent())
		self.addEvent("self_join", DefaultEvents.DefaultSelfJoinEvent())
		self.addEvent("self_part", DefaultEvents.DefaultSelfPartEvent())
		self.addEvent("self_kick", DefaultEvents.DefaultSelfKickEvent())
		self.addEvent("names", DefaultEvents.DefaultNamesEvent())
		self.addEvent("unhandled", DefaultEvents.DefaultUnhandledEvent())
		
		# Run the main loop in a thread, because that is cool.
		self.__main_thread = threading.Thread(target=self.mainLoop)
	
	def connect(self, server, port=6667):
		"""Connects to the IRC server and sets up a socket."""
		self.log("Attempting to connect to server.")
		
		self.__sock = socket.create_connection((server, port))
		self.__sock_file = self.__sock.makefile("rb")
		
		self.sendRaw("NICK " + self.nick)
		self.sendRaw("USER " + self.user + " * * :" + self.name)
		
		# Start the thread.
		self.__main_thread.start()
	
	def disconnect(self, message="UnoBot Framework"):
		"""Disconnects from the server."""
		if self.connected:		
			self.sendRaw("QUIT :" + message)
			self.__sock.close()
	
	def mainLoop(self):
		"""Main loop - reads in data and forwards it to events. Runs in it's
		own thread."""

		while True:
			data = self.__sock_file.readline()
			
			if data:
				data = data[:-2]
				
				# Check for server ping.
				if data[0:4] == "PING":
					return_data = data.split(":")[1]
					self.sendRaw("PONG :" + return_data)
				else:
					# Assume it is some sort of message or something.
					split_data = data.split(" ")
					
					user_full = split_data[0][1:]
					nick = user_full[0:user_full.find("!")]
					command = split_data[1].upper()
					
					if command == "001":
						# First line of MOTD or something?
						# Generally means we're connected.
						self.connected = True
						self.handleEvents("connected")
					elif command == "353":
						# Gives list of users in IRC channel.
						users = " ".join(split_data[5:])[1:].split(" ")[:-1]
						channel = split_data[4]
						
						self.handleEvents("names", channel, users)
					elif command == "PRIVMSG":
						# Message sent.
						target = split_data[2]
						message = " ".join(split_data[3:])[1:]
						
						self.handleEvents("message", nick, target, message)
					elif command == "NOTICE":
						# Message sent.
						target = split_data[2]
						message = " ".join(split_data[3:])[1:]
						
						self.handleEvents("notice", nick, target, message)
					elif command == "JOIN":
						# Someone has joined a channel, or we have.
						channel = split_data[2][1:]
						
						if nick == self.nick:
							self.handleEvents("self_join", channel)
						else:
							self.handleEvents("join", nick, channel)
					elif command == "PART":
						# Someone has parted a channel, or we have.
						channel = split_data[2]
						
						if nick == self.nick:
							self.handleEvents("self_part", channel)
						else:
							self.handleEvents("part", nick, channel)
					elif command == "KICK":
						# Someone has joined a channel, or we have.
						channel = split_data[2]
						kick_nick = split_data[3]
						message = " ".join(split_data[4:])[1:]
						
						if kick_nick == self.nick:
							self.handleEvents("self_kick", nick, channel, message)
						else:
							self.handleEvents("kick", nick, kick_nick, channel, message)
					elif command == "NICK":
						# Nickname has changed. Also includes ourselves.
						new_nick = split_data[2][1:]
						
						if nick == self.nick:
							self.handleEvents("self_nick", new_nick)
						else:
							self.handleEvents("nick", nick, new_nick)
					elif command == "QUIT":
						# User has quit the server.
						message = " ".join(split_data[2:])[1:]
						
						self.handleEvents("quit", nick, message)
					else:
						self.handleEvents("unhandled", data)
			else:
				# Socket has been closed.
				self.handleEvents("disconnected")
				quit()
		
	def handleEvents(self, event_type, *event_parameters):
		"""Calls the appropriate functions for each event"""
		for event in self.__events[event_type]:
			event.fire(self, *event_parameters)
			
			if self.debug:
				self.log("Handled event(" + event_type + "): " + str(event))
		
		# Debug silliness.
		if self.debug:
			self.log("Event(" + event_type + "): " + str(event_parameters))
	
	# ------ IRC operation functions.
	
	def sendJoin(self, channel):
		"""Sends commands to join a channel."""
		if not channel in self.channels:
			self.sendRaw("JOIN " + channel)
	
	def sendPart(self, channel):
		"""Sends commands to part a channel."""
		if channel in self.channels:
			self.sendRaw("PART " + channel)
	
	def sendAction(self, target, message):
		"""Sends a notice to a target."""
		self.sendRaw("DESCRIBE " + target + " :" + message)
		
	def sendAddModes(self, channel, target, modes)
		self.sendRaw("MODE " + channel + " +" + modes + " :" + target)
	
	def sendRemModes(self, channel, target, modes)
		self.sendRaw("MODE " + channel + " -" + modes + " :" + target)
	
	def sendMessage(self, target, message):
		"""Sends a message to the specificed target."""
		self.sendRaw("PRIVMSG " + target + " :" + message)
	
	def sendNotice(self, target, message):
		"""Sends a notice to a target."""
		self.sendRaw("NOTICE " + target + " :" + message)
	
	def sendNick(self, new_nick):
		"""Changes the nickname."""
		self.sendRaw("NICK " + new_nick)
	
	def sendRaw(self, data):
		"""Sends raw data to the socket. Automatically adds a new
		line feed and such at the end."""		
		self.__sock.send(data + "\r\n")
	
	# ------ Event management helpers.
	
	def addEvent(self, event_type, event):
		"""Adds an event to the handler."""
		if not event in self.__events[event_type]:
			self.__events[event_type].append(event)
			
			if self.debug:
				self.log("Added event(" + event_type + "): " + str(event))
	
	def removeEvent(self, event_type, event):
		"""Removes an event from the handler."""
		if event in self.__events[event_type]:
			self.__events[event_type].remove(event)
			
			if self.debug:
				self.log("Removed event(" + event_type + "): " + str(event))
		
	# ------ Error Handling
	
	def error(self, message):
		"""Logs errors to the console."""
		print self.errorTime(), "<ERROR> ", message
		
	def log(self, message):
		"""Prints message to console"""
		print self.errorTime(), "<LOG>", message
		
	def errorTime(self):
		"""Returns the standard format for log time."""
		return datetime.datetime.now().strftime("[%H:%M]")