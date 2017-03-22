import re
from unidecode import unidecode
from bs4 import BeautifulSoup
from datetime import datetime

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

		return result


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


def lookup( clsname ):
	for child in Filter.__subclasses__():
		if child.source_name == clsname:
			return child()

if __name__=='__main__':
	with open( 'test/test.html', 'r' ) as f:
		cnn = CNN()
		cnn.process( f.read() )
