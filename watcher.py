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
			print('page changed')
			self.etag = header['etag']
			self.__get_urls( self.feed )
		else:
			print('page unchanged')



if __name__=='__main__':
	watcher = Watcher('http://rss.cnn.com/rss/edition.rss', filter=filters.cnn, database='sqlite:///articles.db')
	watcher.update()

	try:
		while True:
			time.sleep(10)
			watcher.update()
	except KeyboardInterrupt:
		pass
