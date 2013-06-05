
# DefaultEvents.py
# --------------------------------------------------------------------------

import Events
import Utils

# ------------------------------------------------------------------------------

class DefaultConnectedEvent(Events.ConnectedEvent):
	def fire(self, irc):
		"""Updates bot connection status."""
		irc.connected = True
		
		irc.log("Connected to server.")
		
class DefaultDisconnectedEvent(Events.DisconnectedEvent):
	def fire(self, irc):
		"""Updates bot connection status."""
		irc.connected = False
		
		irc.log("Disconnected from server.")
		
class DefaultNamesEvent(Events.NamesEvent):
	def fire(self, irc, channel, nicks):
		"""Adds names to channel's nicklist."""
		if channel in irc.channels:
			for nick in nicks:
				if not nick == "" and not nick == irc.nick:
					if not nick in irc.channels[channel]["nicks"]:
						irc.channels[channel]["nicks"].append(Utils.stripNickStatus(nick))
		
# ------------------------------------------------------------------------------

class DefaultJoinEvent(Events.JoinEvent):
	def fire(self, irc, nick, channel):
		"""Updates nick list of channel."""
		if channel in irc.channels:
			irc.channels[channel]["nicks"].append(nick)
			
class DefaultPartEvent(Events.PartEvent):
	def fire(self, irc, nick, channel):
		"""Updates nick list of channel."""
		if channel in irc.channels:
			if nick in irc.channels[channel]["nicks"]:
				irc.channels[channel]["nicks"].remove(nick)
			
class DefaultQuitEvent(Events.QuitEvent):
	def fire(self, irc, nick, message):
		"""Goes through each channel and updates the list of users to match."""
		for channel in irc.channels:
			if nick in irc.channels[channel]["nicks"]:
				irc.channels[channel]["nicks"].remove(nick)

class DefaultKickEvent(Events.KickEvent):
	def fire(self, irc, nick, kick_nick, channel, message):
		"""Updates nick list of channel."""
		if channel in irc.channels:
			if kick_nick in irc.channels[channel]["nicks"]:
				irc.channels[channel]["nicks"].remove(kick_nick)

# ------------------------------------------------------------------------------

class DefaultNickEvent(Events.NickEvent):
	def fire(self, irc, nick, new_nick):
		"""Goes through each channel and updates the list of users to match."""
		for channel in irc.channels:
			if nick in irc.channels[channel]["nicks"]:
				irc.channels[channel]["nicks"][irc.channels[channel]["nicks"].index(nick)] = new_nick


# ------------------------------------------------------------------------------

class DefaultSelfJoinEvent(Events.SelfJoinEvent):
	def fire(self, irc, channel):
		"""Adds channel to channel list and initalizes it's dictionary."""
		if not channel in irc.channels:
			irc.channels[channel] = {"nicks":[]}
			
			irc.log("Joined " + channel)
			
class DefaultSelfPartEvent(Events.SelfPartEvent):
	def fire(self, irc, channel):
		"""	Removes channel from list."""
		if channel in irc.channels:
			del irc.channels[channel]
			
			irc.log("Parted " + channel)

# ------------------------------------------------------------------------------

class DefaultSelfKickEvent(Events.SelfKickEvent):
	def fire(self, irc, nick, channel, message):
		"""Removes channel from list."""
		if channel in irc.channels:
			del irc.channels[channel]

# ------------------------------------------------------------------------------

class DefaultSelfNickEvent(Events.SelfNickEvent):
	def fire(self, irc, new_nick):
		"""Updates bot nickname to match."""
		irc.nick = new_nick # Update our nickname.

# ------------------------------------------------------------------------------

class DefaultUnhandledEvent(Events.UnhandledEvent):
	def fire(self, irc, data):
		"""Called when an event is unhandled."""
		if irc.debug:
			irc.log("Unhandled data: " + data)