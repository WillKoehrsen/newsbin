import re
from unidecode import unidecode
from bs4 import BeautifulSoup

def cnn( content ):
	soup = BeautifulSoup(content, 'html.parser')

	# find the content
	matches, result = soup.find_all(['div','p'], class_="zn-body__paragraph"), ''
	for match in matches:
		inner_text = match.find(text=True, recursive=False)
		result += unidecode( inner_text ).strip() + '\n' if inner_text else ''

	# find the author
	author_meta = soup.find('meta', {'itemprop':'author'})
	author = author_meta['content'].split(',')[0] if author_meta else 'unknown'

	# find the title
	title_meta = soup.find('meta', {'itemprop':'headline'})
	title = title_meta['content'] if title_meta else ''

	# find the section
	section_meta = soup.find('meta', {'itemprop':'articleSection'})
	section = section_meta['content'] if section_meta else ''

	return {'category':section,'title':title,'author':author,'content':result}
