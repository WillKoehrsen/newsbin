import re
from bs4 import BeautifulSoup

def cnn( content ):
    soup = BeautifulSoup(content, 'html.parser')

    # find the content
    matches, result = soup.find_all(['div','p'], class_="zn-body__paragraph"), []
    for match in matches:
        result.append( ''.join(match.strings) )

    # find the author
    author_meta = soup.find('meta', {'itemprop':'author'})
    author = author_meta['content'] if author_meta else 'None'

    # find the title
    title_meta = soup.find('meta', {'itemprop':'headline'})
    title = title_meta['content'] if title_meta else 'None'

    # find the section
    section_meta = soup.find('meta', {'itemprop':'articleSection'})
    section = section_meta['content'] if section_meta else 'None'

    return ( section, title, author, result )
