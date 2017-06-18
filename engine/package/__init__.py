# system imports
import sys
import os

# running under debug/production
production = os.environ.get('PRODUCTION',False)

# for config management
from configparser import ConfigParser, ExtendedInterpolation

# to simplify the settings portion of config
from types import SimpleNamespace

# for database interaction
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# set the path to the root directory so that we can import from shared
root = os.path.dirname( os.path.dirname( os.path.dirname( __file__ ) ) )
sys.path.insert( 1, root )

# import everything from shared
from shared import models
from contextlib import contextmanager
from shared import filters
from shared import defaults

# load the config file from root/config
config = ConfigParser( interpolation=ExtendedInterpolation() )
config.read( os.path.join( root, 'config/newsbin.conf' ) )

if production:
    settings = SimpleNamespace( **config['production'] )

    # attach to the database specified in the config file
    db_engine = create_engine( config['production']['database'] )
else:
    settings = SimpleNamespace( **config['settings'] )

    # attach to the database specified in the config file
    db_engine = create_engine( config['settings']['database'] )

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
