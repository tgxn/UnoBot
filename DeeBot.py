
# DeeBot.py
# --------------------------------------------------------------------------

# ------ Data Structures
#	DeeBot.plugins = {
#		"[plugin_name]":{
#			"module":[module_object], 
#			"instance":[instance_object],
#		}
#	}

import os
import argparse
import threading

import DeeIRC
import DeeIRC.Utils as Utils

import Plugin
import Events

# ------------------------------------------------------------------------------

class DeeBot(DeeIRC.IRC.DeeIRC):
	
	def __init__(self):
		"""Constructor"""
		self.debug = True
		super(DeeBot, self).__init__("UnoBot")
		
		# Config
		self.config = {}
		self.config["server"] = os.environ['IRC_SERVER']
		self.config["channel"] = os.environ['IRC_CHANNEL']
		self.config["admins"] = [x.strip() for x in os.environ['IRC_ADMINS'].split(',')]
		self.config["plugins"] = ["Uno"]
		
		# Add events.
		self.addEvent("connected", Events.ConnectedEvent())
		self.addEvent("message", Events.MessageEvent())
		
		# Plugin modules are loaded into the plugin dictionary, with the key
		# being the name of the module.
		self.plugins = {}
		
		# Load plugins.
		for plugin in self.config["plugins"]:
			self.loadPlugin(plugin)
	
	# ------ Loop --------------------------------------------------------------
	
	def run(self):
		"""Runs continously in it's own thread, calling plugin, think functions and other things. Neccessary for timers, etc."""
		
		self.connect(self.config["server"])
			
	# ------ Plugin helpers ----------------------------------------------------
	
	# Loads a plugin.
	def loadPlugin(self, plugin_name):
		
		try:
			# Get the full import string and import the module
			import_path = "Plugin." + plugin_name
			plugin_module = __import__(import_path, globals(), locals(), plugin_name)
			
			# Get the instance of the plugin and load it.
			plugin = plugin_module.getPluginInstance()
			plugin.load(self)
			
			# Add it into the dictionary.
			self.plugins[plugin_name] = {
				"module":plugin_module,
				"instance":plugin,
			}
			
			# Log it.
			self.log("Loaded plugin(" + plugin_name + ")")
		except Exception:
			self.error("Failed to load plugin(" + plugin_name + "): " + str(e))
			raise # pass so calling function can manage it.
		
	# Reloads a plugin.
	def reloadPlugin(self, plugin_name):
	
		if self.hasPlugin(plugin_name):
			# Reload the actual module file.
			reload(self.plugins[plugin_name]["module"])
			
			# Run the unload/load functions on it.
			self.unloadPlugin(plugin_name)
			self.loadPlugin(plugin_name)
	
	# Unloads a plugin.
	def unloadPlugin(self, plugin_name):
	
		if self.hasPlugin(plugin_name):
			# Run the unload method.
			self.getPlugin(plugin_name).unload(self)
			
			# Delete the plugin and log a message.
			del self.plugins[plugin_name]
			self.log("Unloaded plugin(" + plugin_name + ")")
	
	def hasPlugin(self, plugin_name):
		"""Returns true if a plugin is loaded, otherwise false"""
		if plugin_name in self.plugins:
			return True
		else:
			return False
	
	def getPlugin(self, plugin_name):
		"""Returns a plugin instance."""
		if plugin_name in self.plugins:
			return self.plugins[plugin_name]["module"].getPluginInstance()
		else:
			return None
			
	# ------ Command helpers ---------------------------------------------------
	
	def findPluginFromTrigger(self, trigger):
		"""Returns the plugin name if a command exists, otherwise none"""
		trigger = trigger.lower() # lowercase!
		
		# Loop through all plugins.
		for plugin_name in self.plugins:
			plugin = self.getPlugin(plugin_name)
			
			# Check if the plugin has that trigger.
			if plugin.hasCommand(trigger):
				return plugin_name
		
		# Not found :(
		return None
		
	# ------ User helpers ------------------------------------------------------
	
	def isAdmin(self, nick):
		"""Returns if a user is an admin or not"""
		if nick in self.config["admins"]:
			return True
		else:
			return False
			
	# ------ Error Messages and Logging ----------------------------------------
	
	def error(self, message, **args):
		"""Prints errors to console or channel. Overrides default one.
		
		args:
			target: Channel/user to output to.
			console: Boolean saying if we should output to console or not."""
		error_message = Utils.boldCode() + "Error: " + Utils.normalCode() + message
		
		if args.has_key("target"):
			self.sendMessage(args["target"], error_message)
			
		if args.has_key("console"):
			if args["console"]:
				print self.errorTime(), "<ERROR>", Utils.stripCodes(message)
		else:
			print self.errorTime(), "<ERROR>", Utils.stripCodes(message)
			
# ------------------------------------------------------------------------------

if __name__ == "__main__":
	print "Starting Deebot"
	print

	parser = argparse.ArgumentParser()
	parser.add_argument('--server')
	parser.add_argument('--channel')
	parser.add_argument('--admins')
	parser.add_argument('--ns_pw')
	args = parser.parse_args()
	
	if args:
		print args
		for arg in vars(args):
			print arg, getattr(args, arg)
			if arg =="server":
				print "server", getattr(args, arg)
				os.environ['IRC_SERVER'] = getattr(args, arg)
			if arg =="channel":
				print "channel", getattr(args, arg)
				os.environ['IRC_CHANNEL'] = getattr(args, arg)
			if arg =="admins":
				print "admins", getattr(args, arg)
				os.environ['IRC_ADMINS'] = getattr(args, arg)
			if arg =="ns_pw":
				print "ns_pw", getattr(args, arg)
				os.environ['IRC_NS_PW'] = getattr(args, arg)
		
	
	bot = DeeBot()
	bot.run()