# system imports
import sys
import os
import logging

# for config management
from configparser import ConfigParser, ExtendedInterpolation

# for database interaction
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# set the path to the root directory so that we can import from shared
root = os.path.dirname( os.path.dirname( os.path.dirname( __file__ ) ) )
sys.path.insert( 1, root )

# to simplify the settings portion of config
from types import SimpleNamespace
from contextlib import contextmanager
from shared import models, filters, defaults

# get the production environment variable
production = os.environ.get('PRODUCTION',False)

# load the config file from root/config
config = ConfigParser( interpolation=ExtendedInterpolation() )
config.read( os.path.join( root, 'config/newsbin.conf' ) )

if production:
    settings = SimpleNamespace( **config['production'] )

    # attach to the database specified in the config file
    db_engine = create_engine( settings.database )
else:
    settings = SimpleNamespace( **config['settings'] )

    # attach to the database specified in the config file
    db_engine = create_engine( settings.database )

session_generator = sessionmaker(bind=db_engine)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = session_generator()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

# ------------------------------------------------------------------------------
# init the log
log = logging.getLogger("newsbin.site")
log.setLevel(logging.DEBUG)

# format messages for log
_format = logging.Formatter('[%(asctime)s] %(levelname)s:  %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

# create the file logging handler
file_h = logging.FileHandler( os.path.join( settings.logdir, 'newsbin_site.log' ) )
file_h.setFormatter(_format)

# add handlers to log object
log.addHandler(file_h)
