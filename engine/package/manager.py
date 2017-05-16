from queue import Queue
import threading
import logging

log = logging.getLogger("newsbin.engine")

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
		self.name = self.__class__.__name__

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
			log.info('{} has started {} workers'.format(self.name,len(self.workers)))

	def stop( self ):
		"""Stop the workers."""
		if self.running:
			log.info('{} is stopping'.format(self.name))

			self.looping = False
			self.running = False
			self.__clear()

			wcount = len(self.workers)

			# stop all workers and wait for threads
			# to end before deleting them.
			for worker in self.workers:
				self.put( None )
			for worker in self.workers:
				worker.join()
			del self.workers[:]

			log.info('{} has stopped {} workers'.format(self.name,wcount))

		else:
			log.info('{} is not running'.format(self.name))

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

	def __clear( self ):
		with self.mutex:
			self.queue.clear()
			self.all_tasks_done.notify_all()
			self.unfinished_tasks = 0

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
