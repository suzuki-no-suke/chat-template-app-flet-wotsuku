from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



def init_app():
    # if env does not exists, create and set default
    Base = declarative_base()

    class ChatTable(Base):
        __tablename__ = 'chat_table'
        id = Column(Integer, primary_key=True)
        text = Column(String)

    engine = create_engine('sqlite:///chat.db', echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # if db does not exists, create database

    # migrate database
