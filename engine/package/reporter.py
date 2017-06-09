import threading
from os.path import join, dirname, realpath
import time
from datetime import datetime


class Action:
	def __init__( self, *args, **kwargs ):
		self.is_success = kwargs.get('success',False)
		self.reason = kwargs.get('reason','')
		self.source = kwargs.get('source')
		self.url = kwargs.get('url')

	def __str__( self ):
		return '{}:::{}:::{}:::{}'.format( self.source, self.url, self.reason, self.is_success  )

class Reporter:

	save_name = join( dirname( realpath(__file__) ), 'reporter.state' )
	lock = False
	records = []

	def __init__( self, *args, **kwargs ):
		self.load( self.save_name )
		self.trailing_time = time.time()
		self.output_location = kwargs.get('write_to',None)

	def record_failure( self, article, reason='' ):
		self.records.append( Action( source=article.source, url=article.link, reason=reason ) )
		self.timed_report()

	def record_success( self, article ):
		self.records.append( Action( source=article.source, url=article.link, success=True ) )
		self.timed_report()

	def timed_report( self ):
		now = time.time()
		if now - self.trailing_time > 60:
			self.report()
			del self.records[:]
			self.trailing_time = now

	def report( self ):
		results = {}
		reasons = {}
		totals = {}

		if self.lock: return
		else: self.lock = True

		try:

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

			if self.output_location:
				with open(self.output_location,'w') as f:
					f.write('========== Newsbin Engine Status ==========')
					f.write('Current: {}'.format(datetime.now().strftime('%H:%M:%S %p (server time)')))
					f.write('{:<20}{:>10}{:>10}{:>10}\n'.format('Source','Failed','Succeeded', 'Total'))
					for source,result in results.items():
						successes = result['successes']
						failures = result['failures']
						total = result['total']

						f.write('{:<20}{:>10}{:>10}{:>10}\n'.format( source, failures, successes, total ))

			# allow other threads to use the file
			self.lock = False

		except Exception as e:
			# allow other threads to use the file
			self.lock = False

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
			pass
			#print('Error on reporter load: {}'.format(type(e)))
