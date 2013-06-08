
# Events.py
# --------------------------------------------------------------------------

import DeeIRC.Events as Events
import Config

# Connect Event Class
# --------------------------------------------------------------------------

class ConnectedEvent(Events.ConnectedEvent):
	
	# When this event is fired.
	def fire(self, bot):
		
		# Auth with nickserv on connect.
		bot.sendRaw("PRIVMSG NickServ :identify " + Config.nickserv)
		
		# Joins the configured channel on connect.
		bot.sendJoin(Config.channel)
		
		# Announce running.
		bot.sendAction(Config.channel, "is now running!")
		

# Message Event Class
# --------------------------------------------------------------------------

class MessageEvent(Events.MessageEvent):
	
	# When this event is fired.
	def fire(self, bot, nick, target, message):
	
		# Checks if a command has been said and run it if so.
		if message[0] == Config.command_prefix:
		
			# Get the command from the message.
			trigger_end = message.find(" ")
			
			if not trigger_end >= 0:
				# No parameters.
				trigger_end = len(message)
			
			trigger = message[1:trigger_end].lower()
			
			# If the command exists, run the function.
			plugin_name = bot.findPluginFromTrigger(trigger)
			if plugin_name:
				plugin = bot.getPlugin(plugin_name)
				plugin.runCommand(bot, trigger, nick, target, message[trigger_end+1:])
				
				if bot.debug:
					bot.log("Command(" + plugin_name + ":" + trigger + "): (" + nick + ", " + target + ", " + message +")")
		else:
			# Run commands which do not rely on an actual trigger.
			for plugin_name in bot.plugins:
				plugin = bot.getPlugin(plugin_name)
				
				if plugin.hasCommand("*"):
					plugin.runCommand(bot, "*", nick, target, message)
					
					if bot.debug:
						bot.log("Command(" + plugin + ":*): (" + nick + ", " + target + ", " + message +")")
						pass