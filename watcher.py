import time, requests, threading, filters
from bs4 import BeautifulSoup
from article import Article
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Watcher:
	def __init__( self, *args, **kwargs ):
		self.filter = kwargs['filter']
		self.database = kwargs['database']
		self.feed = args[0]
		#self.__get_urls( self.feed )

	def __get_urls( self, rss ):
		"""parses urls from feed and updates the database"""
		session = sessionmaker( bind=create_engine(self.database) )()
		response = requests.get( rss )
		links = BeautifulSoup( response.text, 'html.parser' ).select('item link')
		found_cnt, new_cnt, ignored_cnt = 0, 0, 0
		for link in links:
			link = link.text
			article = session.query(Article).filter(Article.url == link).all()
			if not article:
				article = Article( link, filter=self.filter, database=self.database )
				saved = article.save()
				if saved:
					new_cnt += 1
				else:
					ignored_cnt +=1
			else:
				found_cnt +=1

		print('found: ' + str(found_cnt) + ' added: ' + str(new_cnt) + ' ignored: ' + str(ignored_cnt))

	def __cycle( self ):
		"""is executed by the worker thread"""
		while self.running.is_set():
			# get a new header
			header = requests.head(self.feed).headers

			# check if etag is different and call notify if so
			if header['etag'] != self.etag:
				self.etag = header['etag']
				print('page changed: updating')
				self.__get_urls( self.feed )
			else:
				print('page unchanged')

			# don't spam the server
			time.sleep(10)

	def watch( self, *args, **kwargs ):
		"""starts a worker watching the target"""
		# get initial etag value
		response = requests.head(self.feed)
		self.etag = response.headers['etag']

		# set 'running' event that will be used to signal exit
		self.running = threading.Event()
		self.running.set()

		# create worker and start running
		self.worker = threading.Thread(target=self.__cycle)
		self.worker.start()

	def die( self ):
		"""kills the worker watching the target"""
		self.running.clear()
		self.worker.join()

if __name__=='__main__':
	watcher = Watcher('http://rss.cnn.com/rss/edition.rss', filter=filters.cnn, database='sqlite:///articles.db')
	watcher.watch()

	try:
		while True:
			time.sleep(0.1)
	except KeyboardInterrupt:
		print('attempting to close thread')
		watcher.die()
		print('watcher closed')
