
# _init_.py
# --------------------------------------------------------------------------

# Plugin Base Class
# --------------------------------------------------------------------------

class Plugin(object):
	
	# --------------------------------------------------------------------------
	
	# Constructor. Sets up command dictionary.
	def __init__(self):
		
		# No commands defined.
		self.commands = {}
	
	# Called when the plugin is loaded. Use this to add commands.
	def load(self, bot):
		pass
	
	# Called when the plugin is unloaded.
	def unload(self, bot):
		pass
	
	# --------------------------------------------------------------------------
	
	# Runs the specified command.
	def runCommand(self, bot, trigger, nick, target, message):
		
		# If triggered, run the function.
		if trigger in self.commands:
			self.commands[trigger](bot, nick, target, message)
	
	# Returns true if a trigger exists in this plugin.
	def hasCommand(self, trigger):
		
		# If the trigger exists, return true.
		if trigger in self.commands:
			return True
		else:
			return False
	
	# --------------------------------------------------------------------------
	
	# Adds a command to the command dictionary so it can be triggered.
	def addCommand(self, trigger, function):
		
		# If it does not already exist, add it to the dictionary.
		if not trigger in self.commands:
			self.commands[trigger] = function
	
	# Removed a command from the command dictionary.
	def removeCommand(self, trigger):
		
		# If the trigger exists, have ti removed from the dictionary.
		if trigger in self.commands:
			del self.commands[trigger]