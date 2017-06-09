import threading
from os.path import join, dirname, realpath
import datetime


class Action:
	def __init__( self, *args, **kwargs ):
		self.datetime = datetime.datetime.now()

		self.is_success = kwargs.get('success',False)
		self.reason = kwargs.get('reason','')
		self.source = kwargs.get('source')
		self.url = kwargs.get('url')

	def __str__( self ):
		return '{}:::{}:::{}:::{}'.format( self.source, self.url, self.reason, self.is_success  )

class Reporter:

	save_name = join( dirname( realpath(__file__) ), 'reporter.state' )
	records = []

	def __init__( self, *args, **kwargs ):
		self.load( self.save_name )

	def record_failure( self, article, reason='' ):
		self.records.append( Action( source=article.source, url=article.link, reason=reason ) )

	def record_success( self, article ):
		self.records.append( Action( source=article.source, url=article.link, success=True ) )

	def report( self ):
		results = {}
		reasons = {}
		totals = {}
		for record in self.records:
			if not record.source in results:
				results[record.source] = {
					'successes':0,
					'failures':0,
					'total':0,
				}

			results[record.source]['total'] += 1
			if record.is_success:
				results[record.source]['successes'] += 1
			else:
				results[record.source]['successes'] += 1

		print('\n{:<20}{:>10}{:>10}{:>10}'.format('Source','Failed','Succeeded', 'Total'))
		for source,result in results.items():
			successes = result['successes']
			failures = result['failures']
			total = result['total']

			print('{:<20}{:>10}{:>10}{:>10}'.format( source, failures, successes, total ))

		print('\n')

	def save( self ):
		with open(self.save_name,'w') as f:
			for record in self.records:
				f.write(str(record) + '\n')

	def load( self, filename ):
		try:
			with open(filename,'r') as f:
				for line in f:
					source, url, reason, success = line.split(':::')
					success = ( success=='True' )
					self.records.append( Action( source=source, url=url, success=success, reason=reason ) )
		except Exception as e:
			print('Error on reporter load: {}'.format(type(e)))
