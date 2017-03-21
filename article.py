import filters, requests

class Article:
	def __init__( self, *args, **kwargs ):
		self.filter = kwargs['filter']
		self.__read( args[0] )

	def __read( self, url ):
		response = requests.get( url )

		self.url = url
		self.raw_content = response.text
		article = self.__parse( response.text )

		self.title = article['title']
		self.author = article['author']
		self.category = article['category']
		self.content = article['content']

	def __parse( self, content ):
		if self.filter:
			return self.filter( content )



if __name__=='__main__':
	article = Article( 'http://www.cnn.com/2017/03/20/politics/james-comey-hearing-white-house-cloud/index.html', filter=filters.cnn )
	print(article.title)
	print(article.author)
	print(article.category)
	print(article.content)
