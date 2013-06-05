
# Events.py
# --------------------------------------------------------------------------

# Basic event class for DeeIRC. All other events are based on this.
# --------------------------------------------------------------------------

class Event(object):
	
	def __init__(self):
		pass
		
	def fire(self, irc):
		pass

# ------------------------------------------------------------------------------

class ConnectedEvent(Event):
	"""Fired when the framework connects to a server."""
	pass
	
class DisconnectedEvent(Event):
	"""Fired when the framework disconnects from the server."""
	pass
	
class NamesEvent(Event):
	"""Fired when the framework recieves the list of nicknames in an IRC
	channel."""
	def fire(self, irc, nicks, channel):
		pass

# ------------------------------------------------------------------------------

class MessageEvent(Event):
	"""Fired when a message is recieved."""
	def fire(self, irc, nick, target, message):
		pass
		
class NoticeEvent(MessageEvent):
	"""Fired when a notice is recieved. Identical to MessageEvent."""
	pass

# ------------------------------------------------------------------------------

class JoinEvent(Event):
	"""Fired when a user joins a channel."""
	def fire(self, irc, nick, channel):
		pass
		
class PartEvent(JoinEvent):
	"""Fired when a user leaves a channel. Identical to JoinEvent."""
	def fire(self, irc, nick, channel):
		pass

class KickEvent(Event):
	"""Fired when a user is kicked from a channel."""
	def fire(self, irc, nick, kick_nick, channel, message):
		pass

class QuitEvent(Event):
	"""Fired when a user quits the server."""
	def fire(self, irc, nick, message):
		pass
	
# ------------------------------------------------------------------------------

class NickEvent(Event):
	"""Fired when a user changes their nickname."""
	def fire(self, irc, nick, new_nick):
		pass
		
# ------------------------------------------------------------------------------

class SelfJoinEvent(Event):
	"""Fired when the framework itself joins a channel."""
	def fire(self, irc, channel):
		pass
		
class SelfPartEvent(SelfJoinEvent):
	"""Fired when the framework itself leaves a channel. Identical to SelfJoinEvent."""
	pass
	
# ------------------------------------------------------------------------------

class SelfKickEvent(Event):
	"""Fired when we are kicked from a channel."""
	def fire(self, irc, nick, channel, message):
		pass
		
# ------------------------------------------------------------------------------

class SelfNickEvent(Event):
	"""Fired when the framework changes it's nickname."""
	def fire(self, irc, new_nick):
		pass
		
# ------------------------------------------------------------------------------

class UnhandledEvent(Event):
	"""Fired when an event is left unhandled."""
	def fire(self, irc, data):
		pass