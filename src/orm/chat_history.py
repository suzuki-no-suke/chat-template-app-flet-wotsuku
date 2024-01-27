import src.orm.base as orm_base

from sqlalchemy import Column, String, LargeBinary, DateTime

class RecodeChatHistory(orm_base.Base):
    """
    chat log format (v0.0.1)
    {
        history : [
            {"role" : "system", "message" : "chat kind of message", "time" : "yyyy-mm-dd HH:MM"},
            ...
        ],
        version : "chat-app-v0.0.1",
        system : "rubberduck-v0.0.1",   # test, example are reserved / noname, unknown are use when testing
    }

    initial_values format (v0.0.1)
    {
        template : {
            filename : "...",
            fullpath : "...",
            content : "...",
        },
        embedded : {
            {
                name : "...",
                type : "input", # input, file for now, expand to image, audio, movie,,,
                fullpath : "...",
                content : "...",
            }
        },
        version : "chat-data-v0.0.1",
        system : "template-v0.0.1", # maybe not version update
    }
    """
    __tablename__ = 'chat_history'
    history_id = Column(String, primary_key=True)
    chat_titleline = Column(String)
    chat_log = Column(LargeBinary)  # dict / pickle
    initial_values = Column(LargeBinary)    # dict / pickle
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
