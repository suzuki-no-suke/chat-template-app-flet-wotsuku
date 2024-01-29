import src.chat.i_chat as ichat

import src.data.chat_history as chat_hist

class SquashWall(ichat.IChatSendAndResponse):
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

        return None

    def system_name(self):
        return "squash-wall-bot-v0.0.1"
