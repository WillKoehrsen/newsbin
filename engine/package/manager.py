from queue import Queue
import threading

class Manager(Queue):
	"""Add worker threads to the standard queue.Queue class.

	Keyword arguments:
	workers  -- number of workers (int: default 10)
	callback -- function to process items with (func: default self.__operation)
	"""
	def __init__( self, *args, **kwargs ):
		self.loop = kwargs.pop('loop',False)
		self.count = kwargs.pop('workers',10)
		self.sessionmaker = kwargs.pop('sessionmaker')
		self.running = False
		self.workers = []

		callback = kwargs.pop('callback',None)
		if callback: self.__operation = callback

		super(Manager, self).__init__( *args, **kwargs )

	def add( self, *args ):
		"""Add items to queue."""
		for item in args:
			if item!=None:
				self.put(item)

	def start( self ):
		"""Create and start the workers."""
		if not self.running:
			self.running = True
			self.looping = self.loop
			for _ in range(self.count):
				session = self.sessionmaker()
				thread = threading.Thread(target=self.__worker, args=(session,))
				self.workers.append( thread )
				thread.start()

	def stop( self ):
		"""Stop the workers."""
		if self.running:
			self.looping = False
			self.running = False
			for worker in self.workers:
				self.put( None )
			for worker in self.workers:
				worker.join()
			del self.workers[:]

	def __worker( self, session ):
		"""Pulls items off the queue and passes to the callback."""
		while True:
			item = self.get()
			if item!=None:
				self.__operation( item, session )
				self.task_done()
				if self.looping:
					self.put( item )
			else:
				break

	def __operation( self, item, session ):
		"""A stub callback function."""
		pass

	def __len__( self ):
		"""length of the queue"""
		return len(self.queue)

	def __str__( self ):
		return '{}(items={} workers={} loop={} callback={})'.format( self.__class__.__name__, len(self), len(self.workers), self.loop, self.__operation.__name__ )

	def __repr__( self ):
		return self.__str__()
