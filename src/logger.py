from datetime import datetime
import traceback, sys, os

class Logger:
	instance = None
	def __init__( self, log ):
		with open(log,'w') as f:
			f.write('')
		self.path = os.path.abspath(log)
		self.name = log.replace('\\','/').split('/')[-1]

	def write( self, msg, **kwargs):
		if kwargs.get('echo',False):
			print(msg)
		with open(self.path,'a') as f:
			f.write(msg + '\n')

	def notify( self, msg, **kwargs ):
		dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

		self.write('(' + dt + ') [NOTIFICATION] ' + msg, echo=False)
		print(msg)

	def debug( self, msg, **kwargs ):
		echo, fatal = kwargs.get('echo',False), kwargs.get('fatal',False)
		dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

		self.write('(' + dt + ') DEBUG: ' + msg, echo=echo)

		if fatal:
			self.write('-- FATAL ERROR --', echo=echo)
			sys.exit()

	def error( self, msg, **kwargs):
		echo, fatal = kwargs.get('echo',False), kwargs.get('fatal',False)
		dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

		self.write('(' + dt + ') ERROR: ' + msg, echo=echo)
		self.write('TRACEBACK:', echo=echo)
		self.write(''.join(traceback.format_stack()), echo=echo)

		if fatal:
			self.write('-- FATAL ERROR --', echo=echo)
			sys.exit()

	@classmethod
	def load( cls, location ):
		if not cls.instance:
			cls.instance = cls(location)
		return cls.instance
