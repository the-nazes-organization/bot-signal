
class Command():
	_command = {}

	def __init__(self):
		pass

	def handle_message(self, command: str):
		# Exec all the command with trigger all message
		# 
		if command in self._command:
			self._command[command]()

	@classmethod
	def add(cls, name: str):
		def decorator(func):
			cls._command[name] = func
			return func
		return decorator
