from flask import Flask, request, render_template
from engine import filters
from engine.article import Article
from newsanno import NewsAnno
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configparser import ConfigParser, ExtendedInterpolation
from types import SimpleNamespace
import threading

collector = None
session = None

app = Flask(__name__)

def setup():
    # create a config parser and find newsanno.conf in local dir
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read('newsanno.conf')

    # unwrap settings into a namespace for ease of use
    settings = SimpleNamespace(**config['settings'])

    # build sources dict to scrape for articles
    sources = {}
    for source in ( item for item in config['sources'] if item not in config.defaults() ):
    	sources[source] = [ item.strip() for item in config['sources'][source].split(',') if item ]

    # get the engine
    db_engine = create_engine(settings.database)

    # get the sessionmaker
    Session = sessionmaker(bind=db_engine)

    # launch news anno
    newsanno = NewsAnno(settings=settings,sources=sources,sessionmaker=Session)

    collector = threading.Thread(target=newsanno.run)
    collector.daemon = True
    collector.start()

    return Session()

@app.route("/")
@app.route("/<source>")
def index( source=None ):
    sources = filters.all()

    articles = []
    if source:
        articles = session.query(Article).filter(Article.source == source.upper()).all()
    else:
        articles = session.query(Article).all()
        
    return render_template('index.html', sources=sources, articles=articles)

if __name__ == "__main__":
    session = setup()
    app.run()
