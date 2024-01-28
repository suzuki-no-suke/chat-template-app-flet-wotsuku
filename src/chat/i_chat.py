from abc import ABC, abstractmethod

class IChatSendAndResponse(ABC):
    """send and resonse type chatbot
    """

    @abstractmethod
    def config(self, config_dict):
        pass

    # TODO : be async
    @abstractmethod
    def send(self, chat_environ):
        """
        chat environ is dictonary. must have below data
        {
            "last_send" : ChatSingleMessage
            "history" : [
                ChatSingleMessage,
                ChatSingleMessage,
                ...
            ]
        }
        
        resonse uses ChatSingleMessage
        """
        pass

    @abstractmethod
    def system_name(self):
        pass

from src.data.chat_history import ChatSingleMessage

class EchoBot(IChatSendAndResponse):
    def config(self, config_dict):
        pass

    def send(self, chat_environ):
        # get last send
        last_send = chat_environ["last_send"]
        last_message = last_send.message

        # build echo
        response = ChatSingleMessage()
        response.set_chat("assistant", last_message)

        return response

    def system_name(self):
        return "echobot-v0.0.1"
