import requests
from bs4 import BeautifulSoup

class Watcher:
	def __init__( self, *args, **kwargs ):
		pass

	def __get_urls( rss ):
		response = requests.get( rss )
		links = BeautifulSoup( response.text, 'html.parser' ).select('item link')
		for link in links:
			print(link.string)

if __name__=='__main__':
	pass
	#strip_urls('http://rss.cnn.com/rss/edition.rss')
