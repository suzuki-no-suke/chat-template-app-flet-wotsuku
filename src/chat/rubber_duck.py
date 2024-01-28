import src.chat.i_chat as ichat

import src.data.chat_history as chat_hist

class RubberDuckBot(ichat.IChatSendAndResponse):
    """
    Rubberduck never says, only you can talk to rubberduck
    """
    def config(self, config_dict):
        """
        config 
            - Nothing
        """
        self.config = config_dict

    def send(self, chat_environ):
        # build response
        response = chat_hist.ChatSingleMessage()
        response.set_chat("rubberduck", "...")

        return response

    def system_name(self):
        return "rubber-duck-bot-v0.0.1"
