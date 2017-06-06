import threading

class Reporter():
	"""Has various statistics, and updates a report every hour"""

	failed = {}

	def __init__( self, *args, **kwargs ):
		sources = kwargs.get('sources',[])
		for source in sources:
			failed[source.lower()] = 0

	def __report( self ):
		with open('report','w') as f:
			f.write('Reported Failures')
			for source,count in self.failed.items():
				f.write('{}: {}'.format(source.upper(),count))

	def start( self ):
		pass

	def stop( self ):
		pass

	def add( self, article ):
		src = article.source.lower()
		failed[src] = failed.get(src,0) + 1
