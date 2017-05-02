# system imports
import sys
import os

# for config management
from configparser import ConfigParser, ExtendedInterpolation

# for database interaction
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# set the path to the root directory so that we can import from shared
root = os.path.dirname( os.path.dirname( os.path.dirname( __file__ ) ) )
sys.path.insert( 1, root )

# import everything from shared
from shared import models, filters

# load the config file from root/config
config = ConfigParser( interpolation=ExtendedInterpolation() )
config.read( os.path.join( root, 'config/newsbin.conf' ) )

# attach to the database specified in the config file
db_engine = create_engine( config['settings']['database'] )
session_generator = sessionmaker(bind=db_engine)
session = session_generator()
