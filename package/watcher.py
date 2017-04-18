import requests
from bs4 import BeautifulSoup
from package.models import Article
from package import annotation
from sqlalchemy import exists
from package import utilities

from threading import Thread

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
		found_cnt, new_cnt, ignored_cnt = 0, 0, 0

		try:
			response = requests.get( rss )
			items = BeautifulSoup( response.text, 'html.parser' ).select('item')
			for item in items:
				if item.title and item.link:
					link = item.link.text.strip()
					title = item.title.text.strip()
					pubdate = item.pubDate.text.strip() if item.pubDate else None

					article_exists = self.database.query(exists().where(Article.title == title)).scalar()
					if not article_exists:
						article = Article(title=title,url=link,publish_date=pubdate, filter=self.filter)
						if article.is_valid():
							self.database.add(article)
							self.database.commit()
							new_cnt += 1

						else:
							ignored_cnt += 1
					else:
						found_cnt += 1
		except Exception as e:
			self.log.error('exception while fetching/parsing rss feed',echo=True)
			raise

		self.log.debug('	already found: ' + str(found_cnt) + ' added: ' + str(new_cnt) + ' unparseable: ' + str(ignored_cnt),echo=self.debug)


	def update( self ):
		self.log.debug('checking: {}'.format(self.feed),echo=self.debug)
		self.__get_urls( self.feed )

if __name__=='__main__':
	pass
