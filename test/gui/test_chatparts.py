import unittest

import src.gui.chat_parts as gui_chat

class TestGUIChatParts(unittest.TestCase):

    def test_build(self):
        chatview = gui_chat.ChatHistoryView()
