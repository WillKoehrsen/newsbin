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
        """Filter article text from news websites.

        This class should be initialized with a string containing a comma separated
        series of valid CSS3 selectors that represent the top-level blocks from which
        to capture plain text.

        Keyword arguments:
            (str)   css:            CSS3 selector   (required)
            (tuple) whitelist:      HTML tags       (optional)
            (tuple) attr_whitelist: Attribute names (optional)

        """

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

        # because who needs React-generated comments
        etree.strip_tags(root,etree.Comment)

        content = []

        # if we have a selector and a whitelist
        # then we can work.
        if self.css and self.whitelist:

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
                result += unidecode( etree.tostring( self.__process(child), with_tail=False, encoding='unicode', method='html' ) )
            else:
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
    'cnn':Filter(css='.zn-body__paragraph, #storytext p'),
    'cnbc':Filter(css='div[itemprop=articleBody]>p, .article-body>p'),
    'nytimes':Filter(css='.story-body-text.story-content'),
    'washpo':Filter(css='article[itemprop=articleBody]>p, .row .span8>p:not(.interstitial-link), article.pg-article>p:not(.interstitial-link)'),
    'reuters':Filter(css='#article-text>p, #article-text>.article-prime'),
    'foxnews':Filter(css='.article-text>p, .article-body>p'),
    'wired':Filter(css='article.article-body-component>div>p'),
}


if __name__=='__main__':
    import defaults
    import feedparser

    limit = 20
    count = 0
    links = {}
    for source, feed, tags in defaults.sources:
        if source not in links:
            links[source] = []

        if source in sources:
            data = feedparser.parse(feed)
            for item in data['items']:
                links[source].append( (item['link'],item['title'],'item{}'.format(count)) )
                count += 1

    with open('/home/mhouse/Projects/python/output.html','w') as out:
        out.write('<style>div{ width:500px; margin:10px auto 10px auto; }</style>')

        out.write('<div>')
        for source in links:
            if source in sources:
                out.write('<h1>{}</h1>'.format(source))
                for idx, item in enumerate(links[source]):
                    link, title, tag = item
                    if idx <= limit:
                        out.write( '<a href="#{}">{}</a><br/><br/>'.format(tag,title) )

        out.write('</div>')
        out.write('<br/><hr/><br/>')

        for source in links:
            if source in sourcelist:
                for idx, item in enumerate(links[source]):
                    link, title, tag = item
                    if idx <= limit:
                        doc = requests.get(link).text
                        content = ''.join([ '<p>{}</p>'.format(p) for p in sourcelist[source]( doc, link ) ])
                        out.write('<div><a name="{}"></a><hr/><a href="{}" target="_blank"><h3>{}</h3></a>{}<hr/></div>'.format(tag,link,title,content))
