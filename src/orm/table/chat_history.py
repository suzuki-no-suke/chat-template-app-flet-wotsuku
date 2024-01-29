import src.orm.scheme.chat_history as orm_chat

from ulid import ULID
from datetime import datetime
import pickle

class ChatHistoryTable:
    def __init__(self, db):
        self.db = db

    def is_exist(self, history_id):
        exists = False
        with self.db.session_scope() as sess:
            existing_chat_hist = sess.query(orm_chat.RecodeChatHistory).filter_by(history_id=current_chat_history.history_id).first()
            exists = existing_chat_hist
        return exists

    def upsert_history_recode(self, recode : orm_chat.RecodeChatHistory):
        """ID 以外何も書き換えない"""
        history_id = recode.history_id
        with self.db.session_scope() as sess:
            # NOTE : history_id = None でもなんとかしてくれるのでなんか None ハンドリングのないコード
            existing_hist = sess.query(orm_chat.RecodeChatHistory).filter_by(history_id=history_id).first()
            if existing_hist:
                sess.query(orm_chat.RecodeChatHistory).filter_by(history_id=history_id).update(
                    {
                        orm_chat.RecodeChatHistory.chat_titleline : recode.chat_titleline,
                        orm_chat.RecodeChatHistory.chat_log : recode.chat_log,
                        orm_chat.RecodeChatHistory.initial_values : recode.initial_values,
                        orm_chat.RecodeChatHistory.updated_at : recode.updated_at,
                    }
                )
            else:
                if history_id is None:
                    history_id = str(ULID())
                    recode.history_id = history_id
                sess.add(recode)
            sess.commit()
        
        return history_id

    def upsert_history(self, cur_id, title, chatlog, initval, update_at=datetime.now()):
        """
        params
        ------
            cur_id : str | None : 現在のデータのID
            title : str : タイトル表示
            chatlog : dict : chat_history の gether で集めた辞書データ
            initval : dict : chat_template の gether で集めた辞書データ
            update_at : datetime : 基本的に指定する必要なし
        """
        recode = orm_chat.RecodeChatHistory()
        recode.history_id = cur_id
        recode.chat_titleline = title
        recode.chat_log = pickle.dumps(chatlog)
        recode.initial_values = pickle.dumps(initval)
        recode.updated_at = update_at
        return self.upsert_history_recode(recode)

    def get_history_recode(self, history_id):
        copy_of_hist = None
        with self.db.session_scope() as sess:
            existing_hist = sess.query(orm_chat.RecodeChatHistory).filter_by(history_id=history_id).first()
            copy_of_hist = orm_chat.RecodeChatHistory()
            copy_of_hist.history_id = existing_hist.history_id
            copy_of_hist.chat_titleline = existing_hist.chat_titleline
            copy_of_hist.chat_log = existing_hist.chat_log
            copy_of_hist.initial_values = existing_hist.initial_values
            copy_of_hist.created_at = existing_hist.created_at
            copy_of_hist.updated_at = existing_hist.updated_at
        return copy_of_hist


    def get_history_all(self):
        """return history id and title

        Return
        ------
        list(tuple(str, str))   : key = history_id, text = chat_titleline
        """
        data_list = []
        with self.db.session_scope() as sess:
            all_chat_data = sess.query(orm_chat.RecodeChatHistory.history_id, orm_chat.RecodeChatHistory.chat_titleline).all()
            for data in all_chat_data:
                data_list.append(
                    (
                        data.history_id,
                        data.chat_titleline
                    )
                )
        return data_list

    def get_history_range(self, start_index, end_index):
        """
        Get history within the specified range of indices.

        Parameters
        ----------
        start_index : int
            Start index of the range.
        end_index : int
            End index of the range.

        Returns
        -------
        list(tuple(str, str))
            List of history IDs and titles within the specified range.
        """
        data_list = []
        with self.db.session_scope() as sess:
            all_chat_data = sess.query(orm_chat.RecodeChatHistory.history_id, orm_chat.RecodeChatHistory.chat_titleline).slice(start_index, end_index).all()
            for data in all_chat_data:
                data_list.append(
                    (
                        data.history_id,
                        data.chat_titleline
                    )
                )
        return data_list
