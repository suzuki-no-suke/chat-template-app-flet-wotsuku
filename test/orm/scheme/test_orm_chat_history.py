import unittest

from dotenv import load_dotenv

import src.orm.base as orm_base
import src.orm.scheme.chat_history as orm_chat

from ulid import ULID
import pickle
from datetime import datetime

class TestOrmChatHistory(unittest.TestCase):
    """Just test fatal error
    """
    def setUp(self):
        load_dotenv()

    def test_save(self):
        db = orm_base.SQLFactory.default_env()
        with db.session_scope() as sess:
            history = orm_chat.RecodeChatHistory()
            history.history_id = str(ULID())
            history.chat_titleline = "test text"
            history.chat_log = pickle.dumps({
                    "version" : "test-v0.0.1",
                    "system" : "test-v0.0.1",
                    "history" : [
                        {"role" : "user", "message" : "chat kind of message", "time" : "2023-01-27 21:44:00"},
                    ]
                })
            history.initial_values = pickle.dumps({
                "version" : "test-v0.0.1",
                "system" : "test-v0.0.1",
                "template" : {
                    "filename" : "test.j2",
                    "fullpath" : "C:\path\to\template\test.j2",
                    "content" : "Chat template with text {{Instruction}}"
                },
                "embedded" : {
                    "Instruction" : "Keep Going",
                }
            })
            created_at = datetime.now()
            updated_at = datetime.now()
            sess.add(history)
            sess.commit()
