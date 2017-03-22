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
		self.etag = ''

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

	def update( self ):
		"""checks to see if the page has changed, possibly updating database"""
		# get a new header
		header = requests.head(self.feed).headers

		# check if etag is different and call notify if so
		if header['etag'] != self.etag:
			print('CHANGED: . . . ' + self.feed)
			self.etag = header['etag']
			self.__get_urls( self.feed )
		else:
			print('	UNCHANGED: . . . ' + self.feed)

class Monitor:
	def __init__( self, *args, **kwargs ):
		self.feeds = kwargs['feeds']
		self.filter = kwargs['filter']
		self.database = kwargs['database']
		self.watchers = []
		for feed in self.feeds:
			watcher = Watcher(feed, filter=self.filter, database=self.database)
			self.watchers.append( watcher )

	def run( self ):
		try:
			while True:
				for watcher in self.watchers:
					watcher.update()
					time.sleep(5)
		except KeyboardInterrupt:
			pass


feed_list = (
	'http://rss.cnn.com/rss/edition.rss',
	'http://rss.cnn.com/rss/cnn_world.rss',
	'http://rss.cnn.com/rss/cnn_us.rss',
	'http://rss.cnn.com/rss/money_latest.rss',
	'http://rss.cnn.com/rss/cnn_allpolitics.rss',
	'http://rss.cnn.com/rss/cnn_tech.rss',
	'http://rss.cnn.com/rss/cnn_health.rss',
	'http://rss.cnn.com/rss/cnn_showbiz.rss',
	'http://rss.cnn.com/rss/cnn_travel.rss',
	'http://rss.cnn.com/rss/cnn_living.rss',
	'http://rss.cnn.com/rss/cnn_freevideo.rss',
	'http://rss.cnn.com/rss/cnn_latest.rss',
)

if __name__=='__main__':
	monitor = Monitor(feeds=feed_list, filter=filters.CNN(), database='sqlite:///articles.db')
	monitor.run()
