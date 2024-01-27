from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager

import os

class SQLFactory:
    """Class to manage SQLAlchemy connections"""
    def __init__(self, db_uri):
        self.db_uri = db_uri
        self.engine = create_engine(self.db_uri, echo=True)
        self.last_session = None

    @classmethod
    def default_env(cls):
        """Create database (SQL Alchemy) connection object from default environ"""
        db_uri = os.getenv("DB_CONNECTION")
        return cls(db_uri)

    def get_engine(self):
        return self.engine

    def getnew_session(self):
        """Create a new session
        If an old one exists, it will be closed
        """
        if self.last_session is not None:
            self.last_session.close()
            self.last_session = None
        session = sessionmaker(bind=self.engine)()
        self.last_session = session
        return self.last_session

    def close_session(self):
        if self.last_session is not None:
            self.last_session.close()
            self.last_session = None

    @contextmanager
    def session_scope(self):
        """Context manager class manages session scope
        usage:
            with factory.session_scope() as session:
                session.add(some_object)
                session.commit()
        """
        session = self.getnew_session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            self.close_session()
