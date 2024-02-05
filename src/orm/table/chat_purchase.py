import src.orm.scheme.chat_purchase as orm_chatpurchase
import src.orm.base as orm_base

from sqlalchemy import desc

from ulid import ULID
from datetime import datetime
import pickle

class ChatPurchaseTable:
    def __init__(self, db : orm_base.Base) -> None:
        self.db = db

    def save_api_log_recode(self, recode : orm_chatpurchase.RecodeChatPurchase) -> str:
        ulid = str(ULID())
        recode.purchase_id = ulid
        with self.db.session_scope() as sess:
            sess.add(recode)
            sess.commit()
        return ulid

    def save_purchase(self, api_log_id, purchace_explain, purchace_unit_price, purchace_amount, sent_at=datetime.now()) -> str:
        recode = orm_chatpurchase.RecodeChatPurchase()
        recode.log_id = api_log_id
        recode.purchace_explain = purchace_explain
        recode.purchace_unit_price = purchace_unit_price
        recode.purchace_amount = purchace_amount
        recode.sent_at = sent_at
        return self.save_api_log_recode(recode)

    def get_single_log_recode(self, purchace_id):
        copy_of_log = None
        with self.db.session_scope() as sess:
            existing_log = sess.query(orm_chatpurchase.RecodeChatPurchase).filter_by(purchace_id=purchace_id).first()
            # copy of data / raw
            copy_of_log = orm_chatpurchase.RecodeChatPurchase()
            copy_of_log.log_id = existing_log.log_id
            copy_of_log.purchace_explain = existing_log.purchace_explain
            copy_of_log.purchace_unit_price = existing_log.purchace_unit_price
            copy_of_log.purchace_amount = existing_log.purchace_amount
            copy_of_log.sent_at = existing_log.sent_at
        return copy_of_log
    
    def get_log_list(self, start_index=0, end_index=-1):
        """
        Get histry within the specified range of indeces.

        Parameters
        ----------
        start_index : int
            Start index of the range (0 origin)
        end_index : int
            End index of the range (start < end or python slice like minus value (ex: -1))
        
        Returns
        -------
        list(tuple(str, str, Datetime))
            list of purchase ID, log ID and sent_at time within the specified range.
        """
        data_list = []
        with self.db.session_scope() as sess:
            purchase_log = sess.query(
                    orm_chatpurchase.RecodeChatPurchase.purchase_id,
                    orm_chatpurchase.RecodeChatPurchase.log_id,
                    orm_chatpurchase.RecodeChatPurchase.sent_at) \
                .slice(start_index, end_index).all()
            for log in purchase_log:
                purchase_log.append(
                    (log.log_id, log.sent_at))
        return data_list
