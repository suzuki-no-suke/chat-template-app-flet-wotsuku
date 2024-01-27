import unittest

from dotenv import load_dotenv

import src.orm.base as orm_base

class TestOrmBase(unittest.TestCase):
    """Just test fatal error
    """
    def setUp(self):
        load_dotenv()

    def test_base_call(self):
        db = orm_base.SQLFactory.default_env()
        with db.session_scope() as sess:
            # do nothing with session
            sess.commit()
