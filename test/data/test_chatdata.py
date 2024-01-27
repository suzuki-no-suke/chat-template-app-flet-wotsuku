import unittest

import src.data.chat_history as chat_hist
import src.data.chat_template as chat_template

from dotenv import load_dotenv 

class TestChatData(unittest.TestCase):
    """just test systax error
    """

    def setUp(self) -> None:
        load_dotenv()
        return super().setUp()

    def test_chat_history(self):
        hist = chat_hist.ChatHistory()
        msg = chat_hist.ChatSingleMessage()
        msg.set_chat("dummy", "test")
        hist.history.append(msg)
        data = hist.gether_chat()

        self.assertIsNotNone(data)

        loaded = chat_hist.ChatHistory()
        loaded.expand_chat(data)

        self.assertIsNotNone(loaded)
        self.assertGreaterEqual(1, len(loaded.history))

    def test_chat_info_just_input(self):
        init_value = chat_template.InitialValue()
        init_value.set_template_by_text("text desu")
        init_value.add_input_text_embedded("test", "test input")
        
        info = init_value.gether_info()

        self.assertIsNotNone(info)

        loaded = chat_template.InitialValue()
        loaded.expand_info(info)

        self.assertIsNotNone(loaded)
        self.assertIsNotNone(loaded.template.content)
        self.assertGreaterEqual(1, len(loaded.embedded))



