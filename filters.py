import re
from unidecode import unidecode
from bs4 import BeautifulSoup

class Filter:
	content_methods = ()
	author_methods = ()
	title_methods = ()
	category_methods = ()
	def process( self, content ):
		soup = BeautifulSoup(content, 'html.parser')
		result = {'category':'','title':'','author':'','content':''}

		for method in self.content_methods:
			matches = soup.find_all( *method )
			if matches:
				for match in matches:
					result['content'] += unidecode( match.text ).strip() + '\n'
				break

		for method in self.author_methods:
			match = soup.find( *method )
			if match:
				result['author'] = unidecode( match['content'] ).strip()
				break

		for method in self.title_methods:
			match = soup.find( *method )
			if match:
				result['title'] = unidecode( match['content'] ).strip()
				break

		for method in self.category_methods:
			match = soup.find( *method )
			if match:
				result['category'] = unidecode( match['content'] ).strip()
				break

		print(result['content'])



class cnn( Filter ):
	content_methods = (
		(['div','p'],{'class':'zn-body__paragraph'}),
		('#storytext p',),
	)
	author_methods = (
		('meta',{'itemprop':'author'}),
		('meta',{'name':'author'}),
	)
	title_methods = (
		('meta', {'itemprop':'headline'}),
		('meta', {'name':'title'}),
	)
	category_methods = (
		('meta', {'itemprop':'articleSection'}),
		('meta', {'name':'section'}),
	)

#def cnn( content ):
#	soup = BeautifulSoup(content, 'html.parser')
#
#	# find the content
#	matches, result = soup.find_all(['div','p'], class_="zn-body__paragraph"), ''
#	if len(matches):
#		for match in matches:
#			inner_text = match.find(text=True, recursive=False)
#			result += unidecode( inner_text ).strip() + '\n' if inner_text else ''
#	else:
#		matches, result = soup.select('#storytext p'), ''
#		for match in matches:
#			inner_text = match.find(text=True, recursive=False)
#			result += unidecode( inner_text ).strip() + '\n' if inner_text else ''
#
#	# find the author
#	author_meta = soup.find('meta',{'itemprop':'author'})
#	author = author_meta['content'].split(',')[0] if author_meta else 'unknown'
#
#	# find the title
#	title_meta = soup.find('meta', {'itemprop':'headline'},{'name':'title'})
#	title = title_meta['content'] if title_meta else ''
#
#	# find the section
#	section_meta = soup.find('meta', {'itemprop':'articleSection'})
#	section = section_meta['content'] if section_meta else ''
#
#	return {'category':section,'title':title,'author':author,'content':result}

if __name__=='__main__':
	with open( 'test/test.html', 'r' ) as f:
		cnnf = cnn()
		cnnf.process( f.read() )
