from datetime import datetime

class ChatSingleMessage:
    """Single chat history object
    """
    def __init__(self) -> None:
        self.role = ""
        self.message = ""
        self.time = None

    def set_chat(self, role, message):
        self.role = role
        self.message = message
        self.time = datetime.now()

    def gether_chat(self):
        return {
            "role" : self.role,
            "message" : self.message,
            "time" : self.time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def expand_chat(self, chat):
        self.role = chat["role"]
        self.message = chat["message"]
        self.time = datetime.strptime(chat["time"], "%Y-%m-%d %H:%M:%S")


class ChatHistory:
    """Data Adapter Class of chat history
    """
    def __init__(self) -> None:
        self.history_id = None
        self.title = None
        self.system = None
        self.history = []

    def gether_chat(self):
        history_data = []
        for c in self.history:
            history_data.append(c.gether_chat())

        # build chat dict
        return {
            "history" : history_data,
            "version" : "chat-app-v0.0.1",
            "system" : self.system
        }


    def expand_chat(self, history):
        # TODO : version check

        # expand chat dict
        self.system = history["system"]
        self.history = []
        chat = history["history"]
        for c in chat:
            one_chat = ChatSingleMessage()
            one_chat.expand_chat(c)
            self.history.append(one_chat)


