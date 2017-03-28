import time, requests
from engine import filters
from bs4 import BeautifulSoup
from engine.article import Article
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Watcher:
	def __init__( self, *args, **kwargs ):
		self.filter = kwargs['filter']
		self.database = kwargs['database']
		self.feed = kwargs['feed']
		self.log = kwargs['log']
		self.etag = ''
		self.debug = False

	def __get_urls( self, rss ):
		"""parses urls from feed and updates the database"""
		self.log.debug('updating:',echo=self.debug)
		response = requests.get( rss )
		links = BeautifulSoup( response.text, 'html.parser' ).select('item link')
		found_cnt, new_cnt, ignored_cnt = 0, 0, 0
		for link in links:
			link = link.text
			article = self.database.query(Article).filter(Article.url == link).all()
			if not article:
				article = Article( link, filter=self.filter )
				if article.is_valid():
					self.database.add(article)
					self.database.commit()
					new_cnt += 1
				else:
					ignored_cnt +=1
			else:
				found_cnt +=1

		self.log.debug('	already found: ' + str(found_cnt) + ' added: ' + str(new_cnt) + ' unparseable: ' + str(ignored_cnt),echo=self.debug)


	def update( self ):
		"""checks to see if the page has changed, possibly updating database"""
		# get a new header
		header = requests.head(self.feed).headers

		# check if etag is different and call notify if so
		if 'etag' not in header or header['etag'] != self.etag:
			self.log.debug(self.feed + ' has changed',echo=self.debug)
			self.etag = header['etag'] if 'etag' in header else ''
			self.__get_urls( self.feed )
		else:
			self.log.debug(self.feed + ' has NOT changed',echo=self.debug)

if __name__=='__main__':
	pass
