import src.orm.base as orm_base
import src.orm.chat_history as orm_db_chat_history

from dotenv import load_dotenv

load_dotenv()   # TODO : when does not exists, it may cause error.

def init_app():
    # if env does not exists, create and set default

    # if db does not exists, create database
    db = orm_base.SQLFactory.default_env()

    engine = db.get_engine()
    orm_base.Base.metadata.create_all(engine)




if __name__ == '__main__':
    init_app()