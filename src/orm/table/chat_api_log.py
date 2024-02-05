import src.orm.scheme.chat_api_log as orm_apilog
import src.orm.base as orm_base

from sqlalchemy import desc

from ulid import ULID
from datetime import datetime
import pickle

class ChatApiLogTable:
    def __init__(self, db : orm_base.Base) -> None:
        self.db = db

    def save_api_log_recode(self, recode : orm_apilog.RecodeChatAPILog) -> str:
        ulid = str(ULID())
        recode.log_id = ulid
        with self.db.session_scope() as sess:
            sess.add(recode)
            sess.commit()
        return ulid

    def save_api_log(self, api_version, sent_raw, sent_json, receive_raw, receive_json, sent_at=datetime.now()) -> str:
        recode = orm_apilog.RecodeChatAPILog()
        recode.api_version = api_version
        recode.sent_pickle = pickle.dumps(sent_raw)
        recode.sent_json = pickle.dumps(sent_json)
        recode.receive_pickle = pickle.dumps(receive_raw)
        recode.receive_json = pickle.dumps(receive_json)
        recode.sent_at = sent_at
        return self.save_api_log_recode(recode)

    def get_single_log_recode(self, log_id):
        copy_of_log = None
        with self.db.session_scope() as sess:
            existing_log = sess.query(orm_apilog.RecodeChatAPILog).filter_by(log_id=log_id).first()
            # copy of data / raw
            copy_of_log = orm_apilog.RecodeChatAPILog()
            copy_of_log.log_id = existing_log.log_id
            copy_of_log.api_version = existing_log.api_version
            copy_of_log.sent_pickle = existing_log.sent_pickle
            copy_of_log.sent_json = existing_log.sent_json
            copy_of_log.receive_pickle = existing_log.receive_pickle
            copy_of_log.receive_json = existing_log.receive_json
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
        list(tuple(str, Datetime))
            list of log ID and sent_at time within the specified range.
        """
        data_list = []
        with self.db.session_scope() as sess:
            all_api_log = sess.query(orm_apilog.RecodeChatAPILog.log_id, orm_apilog.RecodeChatAPILog.sent_at).slice(start_index, end_index).all()
            for log in all_api_log:
                all_api_log.append(
                    (log.log_id, log.sent_at))
        return data_list
