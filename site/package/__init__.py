# system imports
import sys
import os
import logging

# for config management
from configparser import ConfigParser, ExtendedInterpolation

# to simplify the settings portion of config
from types import SimpleNamespace

from package import database
from package.database import session_scope, db_engine

# set the path to the root directory
root = os.path.dirname( os.path.dirname( os.path.dirname( __file__ ) ) )
sys.path.insert( 1, root )

# get the production environment variable
production = os.environ.get('PRODUCTION',False)

# load the config file from root/config
config = ConfigParser( interpolation=ExtendedInterpolation() )
config.read( os.path.join( root, 'config/newsbin.conf' ) )

settings = SimpleNamespace( **config['production'] ) if production else SimpleNamespace( **config['settings'] )
database.init( settings.database )

# ------------------------------------------------------------------------------
# init the log
site_log = logging.getLogger("newsbin.site")
site_log.setLevel(logging.DEBUG)

eng_log = logging.getLogger("newsbin.engine")
eng_log.setLevel(logging.DEBUG)

# format messages for log
_format = logging.Formatter('[%(asctime)s] %(levelname)s:  %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

# create the file logging handler for the site
file_s = logging.FileHandler( os.path.join( settings.logdir, 'newsbin_site.log' ) )
file_s.setFormatter(_format)

# create the file logging handler for the engine
file_e = logging.FileHandler( os.path.join( settings.logdir, 'newsbin_engine.log' ) )
file_e.setFormatter(_format)

# create the console logging handler
console_h = logging.StreamHandler()
console_h.setFormatter(_format)

# add handlers to log object
site_log.addHandler(file_s)
site_log.addHandler(console_h)
eng_log.addHandler(file_e)
eng_log.addHandler(console_h)
