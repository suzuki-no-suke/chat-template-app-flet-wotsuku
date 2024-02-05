import src.orm.base as orm_base

from sqlalchemy import Column, String, DateTime, Float

class RecodeChatPurchase(orm_base.Base):
    """
    Important : API version indicates its details
    """
    __tablename__ = 'chat_purchase'
    purchase_id = Column(String, primary_key=True)
    log_id = Column(String) # actually foreign key
    purchace_explain = Column(String)   # example : {{unit}} * {{amount}} (in dollar => 150.00 yen/dollar)
    purchace_unit_price = Column(Float)
    purchace_amount = Column(Float)
    sent_at = Column(DateTime)
