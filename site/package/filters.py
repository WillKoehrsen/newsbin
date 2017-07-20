import requests
import logging

from lxml import html
from lxml import etree
from lxml.cssselect import CSSSelector
from lxml.html import HtmlComment
from unidecode import unidecode

log = logging.getLogger('newsbin.engine')

# ------------------------------------------------------------------------------
# Filter Class
#   This class is used to pick article content out of
#   webpages with a css selector.
class Filter:

    def __init__( self, *args, **kwargs ):
        # we need css selectors in order to parse articles
        self.css = CSSSelector( kwargs['css'] )

        # the whitelist is for child elements we want to retain
        # html for
        self.whitelist = kwargs.get('whitelist',('a','b','i','cite','br'))

        # attribute whitelist- other attributes on whitelisted
        # elements are discarded by __process
        self.attr_whitelist = kwargs.get('attr_whitelist',('href'))

    def __call__( self, document, url ):
        """Filter article content from raw html"""
        # turn the raw html into an etree
        root = html.fromstring(document)

        # so that they'll continue to work
        root.make_links_absolute(url)


        content = []

        # if we have a selector and a whitelist
        # then we can work.
        if self.css and self.whitelist:
            etree.strip_tags(root,'img',etree.Comment)  # remove img/comment tags
            try:
                # get each matching block that we want
                # the text from
                for block in self.css(root):

                    # parse out the text and whitelisted html
                    para = self.__parse(block)

                    # if we got something, keep it
                    if para: content.append( para )
            except Exception as e:
                log.exception('{} in filter at: {}'.format(type(e),url))

        # return a list of paragraphs
        return content

    def __parse( self, block ):
        """Parse a single top-level block"""

        # if there is leading text, get it, otherwise empty
        if block.text:
            result = unidecode(block.text)
        else:
            result = ''

        # for each child element in the block-
        for child in block:

            # if we want to keep the html, then strip the attributes (__process)
            # and convert to a string.
            if child.tag in self.whitelist:
                if len(child)>0 or child.text:
                    result += unidecode( etree.tostring( self.__process(child), with_tail=False, encoding='unicode', method='html' ) )
            else:
                if len(child)>0 or child.text:
                    result += child.text_content()

            # if there is trailing text, decode and append it
            if child.tail and child.tail.strip():
                result += unidecode( child.tail )

        return result.strip()

    def __subparse( self, element ):
        pass

    def __process( self, element ):
        """Process attributes of a link"""

        # if we haven't determined that we want
        # the attribute, get rid of it.
        for attr in element.attrib:
            if attr not in self.attr_whitelist:
                element.attrib.pop(attr)

        if element.tag == 'a':
            element.attrib['target'] = '_blank'
            element.attrib['rel'] = 'noopener'

        # return the element
        return element

# ------------------------------------------------------------------------------
# Custom filters
#   Add new filters by finding the css selector necessary
#   to pick out the top-level blocks of the article text.
sources = {
    'cnn':Filter(css='.zn-body__paragraph, #storytext p',),
    'cnbc':Filter(css='div[itemprop=articleBody]>p, .article-body>p',),
    'nytimes':Filter(css='.story-body-text.story-content',),
    'washpo':Filter(css='article[itemprop=articleBody]>p, .row .span8>p:not(.interstitial-link), article.pg-article>p:not(.interstitial-link)',),
    'reuters':Filter(css='#article-text>p, #article-text>.article-prime',),
    'foxnews':Filter(css='.article-text>p, .article-body>p',),
    'wired':Filter(css='article.article-body-component>div>p',),
    'techcrunch':Filter(css='div.article-entry>p',),
}


if __name__=='__main__':
    cnn = sources['cnn']
    response = requests.get('http://money.cnn.com/2017/07/17/technology/culture/sexual-harassment-tech-reaction/index.html?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+rss%2Fmoney_latest+%28CNNMoney%3A+Latest+News%29')
    content, test = cnn(response.text,url='http://www.cnn.com/')
