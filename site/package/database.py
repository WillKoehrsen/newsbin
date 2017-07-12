from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

session_generator = None
db_engine = None

def init( location ):
    global session_generator
    global db_engine

    # attach to the database specified in the config file
    db_engine = create_engine( location )
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
