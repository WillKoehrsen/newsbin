import filters, requests

class Article:
    def __init__( self, *args, **kwargs ):
        self.__read( args[0] )

    def __read( self, url ):
        response = requests.get( url )

        self.url = url
        self.raw_content = response.text
        self.content = self.__parse( response.text )

    def __parse( self, content ):
        return filters.cnn( content )


if __name__=='__main__':
    article = Article( 'http://www.cnn.com/2017/03/20/politics/james-comey-hearing-white-house-cloud/index.html' )
