import threading
import os
import datetime


class Action:
	def __init__( self, *args, **kwargs ):
		self.datetime = datetime.datetime.now()

		self.is_success = kwargs.get('success',False)
		self.reason = kwargs.get('reason','')
		self.source = kwargs.get('source')
		self.url = kwargs.get('url')


class Reporter:
	records = []

	def __init__( self, *args, **kwargs ):
		pass

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

		print('\n{:<10}{:<10}{:<10}{:<10}'.format('Source','Failure','Success', 'Total'))
		for source,result in results.items():
			successes = result['successes']
			failures = result['failures']
			total = result['total']

			print('{:<10}{:<10}{:<10}{:<10}'.format( source, failures, successes, total ))

		print('\n')
