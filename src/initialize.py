from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, DateTime, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


import os

Base = declarative_base()

class RecodeChatHistory(Base):
    __tablename__ = 'chat_history'
    history_id = Column(String, primary_key=True)
    chat_titleline = Column(String)
    chat_log = Column(LargeBinary)
    initial_values = Column(LargeBinary)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


def init_app():
    # if env does not exists, create and set default

    # if db does not exists, create database
    engine = create_engine(os.getenv("DB_CONNECTION"), echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    inspector = inspect(engine)
    if not inspector.has_table(RecodeChatHistory.__tablename__):
        Base.metadata.create_all(engine)
