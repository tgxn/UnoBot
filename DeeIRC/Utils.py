
# Utils.py
# --------------------------------------------------------------------------

# Returns the underline control code.
def underlineCode():
	return '\x1F'

# Returns the bold control code.
def boldCode():
	return '\x02'

# Returns the normal control code.
def normalCode():
	return '\x0F'

# Returns the colour control code.
def colorCode(**colors):
	
	# colours:
	#  fg - foreground
	#  bg - background
	
	# Check that the arguments were actually passed.
	if colors.has_key('fg'):
		fg = colors['fg']
	else:
		fg = None
	if colors.has_key('bg'):
		bg = colors['bg']
	else:
		bg = None
	
	code = "\x03"
	
	# If we have a foreground, hopefully, add that.
	if not fg == None:
		code = code + str(fg).rjust(2,'0')
	
	# If no foreground is specifified, assume it to want 01 (black).
	# otherwise assume one was infact specified.
	if not bg == None and fg == None:
		code = code + '01,' + str(bg).rjust(2,'0')
	elif bg:
		code = code + ',' + str(bg).rjust(2,'0')
	
	return code

# Strips all control codes from a message.
def stripCodes(message):
	message = message.replace(underlineCode(),'')
	message = message.replace(boldCode(),'')
	message = message.replace(colorCode(),'')
	message = message.replace(normalCode(),'')
	
	return message

# ------------------------------------------------------------------------------

# Strips all user status symbols from a nickname
def stripNickStatus(nick):
	nick = nick.replace("+", "")
	nick = nick.replace("@", "")
	nick = nick.replace("%", "")
	nick = nick.replace("~", "")
	
	return nick