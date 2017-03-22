import re
from unidecode import unidecode
from bs4 import BeautifulSoup
from datetime import datetime
import requests

class Filter:
	content_selectors = ()
	author_selectors = ()
	title_selectors = ()
	category_selectors = ()
	date_selectors = ()

	def process( self, content ):
		soup = BeautifulSoup(content, 'html.parser')
		result = {'category':'','title':'','author':'','content':'','publish_date':''}

		for selector in self.content_selectors:
			matches = soup.select( selector )
			if matches:
				for match in matches:
					result['content'] += unidecode( match.text ).strip() + '\n'
				break

		for selector in self.author_selectors:
			matches = soup.select( selector )
			if matches:
				result['author'] = unidecode( matches[0]['content'] ).strip()
				break

		for selector in self.title_selectors:
			matches = soup.select( selector )
			if matches:
				result['title'] = unidecode( matches[0]['content'] ).strip()
				break

		for selector in self.category_selectors:
			matches = soup.select( selector )
			if matches:
				result['category'] = unidecode( matches[0]['content'] ).strip()
				break

		for selector in self.date_selectors:
			matches = soup.select( selector )
			if matches:
				result['publish_date'] = unidecode( matches[0]['content'] ).strip()
				break
			else:
				result['publish_date'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

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

	title_selectors = (
		'meta[itemprop=headline]',
		'meta[name=title]'
	)

	category_selectors = (
		'meta[itemprop=articleSection]',
		'meta[name=section]'
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
	)

	author_selectors = (
		'meta[name=author]',
	)

	title_selectors = (
		'meta[name="twitter:title"]',
	)

	category_selectors = (
		'meta[property="article:section"]',
	)

	date_selectors = (
		'meta[itemprop=dateCreated]',
	)

# ------------------------------------------------------------------------------
# nyt filter
class NYT( Filter ):
	source_name = 'nyt'

	content_selectors = (
		'.story-body-text.story-content',
	)

	author_selectors = (
		'meta[name=author]',
	)

	title_selectors = (
		'meta[property="og:title"]',
	)

	category_selectors = (
		'meta[property="article:section"]',
	)

	date_selectors = (
		'meta[itemprop=datePublished]',
	)


def lookup( clsname ):
	for child in Filter.__subclasses__():
		if child.source_name == clsname:
			return child()

if __name__=='__main__':
	response = requests.get( 'http://www.cnbc.com/2017/03/22/trump-sees-obamacare-replacement-passing-house-vote-needs-to-happen.html' )
	test = CNBC()
	result = test.process( response.content )
	print(result['title'])
	print(result['author'])
	print(result['publish_date'])
	print(result['category'])
	print(result['content'])
