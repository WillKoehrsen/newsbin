import threading
import os
import session
import datetime


class Action:
	def __init__( self, *args, **kwargs ):
		self.datetime = datetime.datetime.now()

		self.is_success = kwargs.get('success',False)
		self.reason = kwargs.get('reason','')
		self.source = kwargs.get('source')
		self.url = kwargs.get('url')


class Reporter:
	"""Has various statistics, and updates a report every hour"""

	records = []

	def __init__( self, *args, **kwargs ):
		pass

	def record_failure( self, article, reason='' ):
		self.records.append( Action( source=article.source, url=article.url, reason=reason ) )

	def record_success( self, article ):
		self.records.append( Action( source=article.source, url=article.url, success=True ) )

	def report( self ):
		results = {}
		reasons = {}
		totals = {}
		for record in records:
			totals[record.source] = totals.get(record.source,0) + 1

			if record.is_success:
				results[record.source] = results.get(record.source,(0,0))[0] + 1
			else:
				results[record.source] = results.get(record.source,(0,0))[1] + 1

			if record.reason:
				reasons[record.reason] = reason.get(record.reason,0) + 1

		print('{:<10}{:<10}{:<10}{:<10}'.format('Source','Failure','Success', 'Total'))
		for source, result in results.items():
			print('{:<10}{:<10}{:<10}{:<10}'.format(source,result[0],result[1],total[source]))
