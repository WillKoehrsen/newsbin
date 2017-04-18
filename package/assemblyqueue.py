from queue import Queue
import threading

class AssemblyQueue(Queue):
	"""Add worker threads to the standard queue.Queue class.

	Keyword arguments:
	workers  -- number of workers (int: default 10)
	callback -- function to process items with (func: default self.__process)
	"""
	def __init__( self, *args, **kwargs ):
		count = kwargs.pop('workers',10)
		callback = kwargs.pop('callback',None)
		if callback:
			self.__process = callback
			self.callback = True
		else:
			self.callback = False

		super(AssemblyQueue, self).__init__( *args, **kwargs )

		self.workers = []
		for _ in range(count):
			thread = threading.Thread(target=self.__worker)
			thread.start()
			self.workers.append( thread )

	def add( self, *args ):
		"""Add items to queue."""
		for item in args:
			if item!=None:
				self.put(item)

	def stop( self ):
		"""Stop the workers."""
		for worker in self.workers:
			self.put( None )
		for worker in self.workers:
			worker.join()

	def __worker( self ):
		"""Pulls items off the queue and passes to the callback."""
		while True:
			item = self.get()
			if item!=None:
				self.__process( item )
				self.task_done()
			else:
				break

	def __process( self, item ):
		"""A stub callback function."""
		pass

	def __len__( self ):
		"""length of the queue"""
		return len(self.queue)

	def __str__( self ):
		return '<AssemblyQueue items={} workers={} callback={}>'.format( len(self), len(self.workers), self.callback )

	def __repr__( self ):
		return self.__str__()
