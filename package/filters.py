import regex
from unidecode import unidecode
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.parser import parse
import requests

class Filter:
	source_name = ''

	content_selectors = ()
	author_selectors = ()
	date_selectors = ()

	def process( self, content ):
		soup = BeautifulSoup(content, 'html.parser')
		result = {'keywords':'','author':'','content':'','publish_date':datetime.now()}

		for selector in self.content_selectors:
			matches = soup.select( selector )
			if matches:
				for match in matches:
					result['content'] += '{}\n\n'.format( unidecode( match.text ) )
				break

		for selector in self.author_selectors:
			matches = soup.select( selector )
			if matches:
				result['author'] = unidecode( matches[0]['content'] ).strip()
				break

		for selector in self.date_selectors:
			matches = soup.select( selector )
			if matches:
				try:
					result['publish_date'] = parse( unidecode( matches[0]['content'] ).strip(), default=datetime.now())
				except:
					pass
				break

		result['content'] = result['content'].strip()
		return result

# ------------------------------------------------------------------------------
# cnn filter
class CNN( Filter ):
	source_name = 'cnn'

	content_selectors = (
		'.zn-body__paragraph',
		'#storytext p'
	)

	author_selectors = (
		'meta[itemprop=author]',
		'meta[name=author]'
	)

	date_selectors = (
		'meta[itemprop=datePublished]',
	)

# ------------------------------------------------------------------------------
# cnbc filter
class CNBC( Filter ):
	source_name = 'cnbc'

	content_selectors = (
		'div[itemprop="articleBody"] p',
		'.article-body p',
	)

	author_selectors = (
		'meta[name=author]',
	)

	date_selectors = (
		'meta[itemprop=dateCreated]',
		'meta[name="DC.date.issued"]',
	)

# ------------------------------------------------------------------------------
# nyt filter
class NYTimes( Filter ):
	source_name = 'nytimes'

	content_selectors = (
		'.story-body-text.story-content',
	)

	author_selectors = (
		'meta[name=author]',
	)

	date_selectors = (
		'meta[itemprop=datePublished]',
	)

class WashingtonPost( Filter ):
	source_name = 'washingtonpost'

	content_selectors = (
		'article[itemprop=articleBody] p',
	)

	author_selectors = (
	)

	date_selectors = (
		'meta[itemprop=datePublished]',
	)

class Reuters( Filter ):
	source_name = 'reuters'

	content_selectors = (
		'#article-text p',
	)

	author_selectors = (
		'meta[name=Author]',
	)

	date_selectors = (
		'meta[property="og:article:published_time"]',
	)

class FoxNews( Filter ):
	source_name = 'foxnews'

	content_selectors = (
		'.article-text p',
	)

	author_selectors = (
		'meta[name="dc.creator"]',
	)

	date_selectors = (
		'meta[name="dcterms.created"]',
	)

def all():
	return [ child.source_name for child in Filter.__subclasses__() if child.source_name ]

def lookup( clsname ):
	for child in Filter.__subclasses__():
		if child.source_name == clsname:
			return child()

def exists( clsname ):
	for child in Filter.__subclasses__():
		if child.source_name == clsname:
			return True
	return False

if __name__=='__main__':
	response = requests.get( 'http://www.cnbc.com/2017/03/22/trump-sees-obamacare-replacement-passing-house-vote-needs-to-happen.html' )
	test = CNBC()
	result = test.process( response.content )
	print(result['title'])
	print(result['author'])
	print(result['publish_date'])
	print(result['keywords'])
	print(result['content'])
