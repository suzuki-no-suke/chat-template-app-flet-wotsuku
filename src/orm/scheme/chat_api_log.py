import src.orm.base as orm_base

from sqlalchemy import Column, String, LargeBinary, DateTime, Float

class RecodeChatAPILog(orm_base.Base):
    """
    Important : API version indicates its details
    """
    __tablename__ = 'chat_api_log'
    log_id = Column(String, primary_key=True)
    api_version = Column(String)
    sent_pickle = Column(LargeBinary)   # simple pickle : pickling failure risk
    sent_json = Column(LargeBinary) # json/dict -> pickled
    receive_pickle = Column(LargeBinary)    # simple pic : pickling failure risk
    receive_json = Column(LargeBinary)  # json/dict -> pickled
    sent_at = Column(DateTime)
