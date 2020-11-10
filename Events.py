
# Events.py
# --------------------------------------------------------------------------

import DeeIRC.Events as Events

# Connect Event Class
# --------------------------------------------------------------------------

class ConnectedEvent(Events.ConnectedEvent):
	
	# When this event is fired.
	def fire(self, bot):
		
		# Auth with nickserv on connect.
		bot.sendRaw("PRIVMSG NickServ :identify 1234")
		
		# Joins the configured channels on connect.
		bot.sendJoin(bot.config["channel"])

# Message Event Class
# --------------------------------------------------------------------------

class MessageEvent(Events.MessageEvent):
	
	# When this event is fired.
	def fire(self, bot, nick, target, message):
	
		# Get the command from the message.
		trigger_end = message.find(" ")
		
		if not trigger_end >= 0:
		
			# No parameters.
			trigger_end = len(message)
		
		trigger = message[0:trigger_end].lower()
		
		# If the command exists, run the function.
		plugin_name = bot.findPluginFromTrigger(trigger)
		if plugin_name:
			plugin = bot.getPlugin(plugin_name)
			plugin.runCommand(bot, trigger, nick, target, message[trigger_end+1:])
			
			if bot.debug:
				bot.log("Command(" + plugin_name + ":" + trigger + "): (" + nick + ", " + target + ", " + message +")")
