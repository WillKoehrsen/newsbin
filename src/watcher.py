import time, requests
from src import filters
from bs4 import BeautifulSoup
from src.article import Article
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Watcher:
	def __init__( self, *args, **kwargs ):
		self.filter = kwargs['filter']
		self.database = kwargs['database']
		self.feed = kwargs['feed']
		self.log = kwargs['log']
		self.etag = ''

	def __get_urls( self, rss ):
		"""parses urls from feed and updates the database"""
		self.log.debug('updating:')
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

		self.log.debug('	already found: ' + str(found_cnt) + ' added: ' + str(new_cnt) + ' unparseable: ' + str(ignored_cnt), echo=True)


	def update( self ):
		"""checks to see if the page has changed, possibly updating database"""
		# get a new header
		header = requests.head(self.feed).headers

		# check if etag is different and call notify if so
		if header['etag'] != self.etag:
			self.log.debug(self.feed + ' has changed', echo=True)
			self.etag = header['etag']
			self.__get_urls( self.feed )
		else:
			self.log.debug(self.feed + ' has NOT changed', echo=True)

if __name__=='__main__':
	pass
