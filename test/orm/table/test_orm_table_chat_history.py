import unittest

from dotenv import load_dotenv

import src.orm.base as orm_base
import src.orm.table.chat_history as orm_chat

from ulid import ULID

class TestORMTableChatHistory(unittest.TestCase):
    """Just test fatal error
    """
    def setUp(self):
        load_dotenv()

    def test_create(self):
        db = orm_base.SQLFactory.default_env()
        history_id = None
        chat_title = "table test"
        chat_log = {
            "version" : "test-v0.0.1",
            "system" : "test-v0.0.1",
            "history" : [
                {"role" : "user", "message" : "chat kind of message", "time" : "2023-01-27 21:44:00"},
            ]
        }
        init_val = {
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
        }

        target = orm_chat.ChatHistoryTable(db)
        target.upsert_history(history_id, chat_title, chat_log, init_val)

    def test_update(self):
        # insert once
        db = orm_base.SQLFactory.default_env()
        history_id = str(ULID())
        chat_title = "table test"
        chat_log = {
            "version" : "test-v0.0.1",
            "system" : "test-v0.0.1",
            "history" : [
                {"role" : "user", "message" : "chat kind of message", "time" : "2023-01-27 21:44"},
            ]
        }
        init_val = {
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
        }

        target = orm_chat.ChatHistoryTable(db)
        target.upsert_history(history_id, chat_title, chat_log, init_val)

        # insert twice
        chat_title = "table test"
        chat_log = {
            "version" : "test-v0.0.1",
            "system" : "test-v0.0.1",
            "history" : [
                {"role" : "user", "message" : "chat kind of message", "time" : "2023-01-27 21:44"},
                {"role" : "user", "message" : "chat kind of message", "time" : "2023-01-27 21:44"},
            ]
        }
        init_val = {
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
        }

        target = orm_chat.ChatHistoryTable(db)
        target.upsert_history(history_id, chat_title, chat_log, init_val)

    def test_get_history(self):
        # insert data
        db = orm_base.SQLFactory.default_env()
        history_id = str(ULID())
        chat_title = "table test"
        chat_log = {
            "version" : "test-v0.0.1",
            "system" : "test-v0.0.1",
            "history" : [
                {"role" : "user", "message" : "chat kind of message", "time" : "2023-01-27 21:44"},
            ]
        }
        init_val = {
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
        }

        target = orm_chat.ChatHistoryTable(db)
        target.upsert_history(history_id, chat_title, chat_log, init_val)

        getdata = target.get_history_recode(history_id)

        self.assertEqual(getdata.history_id, history_id)

