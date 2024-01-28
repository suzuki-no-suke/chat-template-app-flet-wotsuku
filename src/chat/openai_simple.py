from src.chat.i_chat import IChatSendAndResponse
from src.data.chat_history import ChatSingleMessage

from openai import OpenAI

class OpenAISimpleBot(IChatSendAndResponse):
    def config(self, config_dict):
        """
        required datas
        - OPENAI_API_KEY
        """
        self.config = config_dict
        self.client = OpenAI(
            api_key=config_dict["OPENAI_API_KEY"]
        )

    def send(self, chat_environ):
        # history to completion api
        history = chat_environ["history"]
        import pprint
        pprint.pprint(history)
        message_list = []
        for m in history:
            chat_role = "assistant"
            if m.role == "user":
                chat_role = "user"
            message_list.append({
                "role" : chat_role,
                "content" : m.message,
            })

        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=message_list
        )

        # analyse response and errors
        msg = completion.choices[0].message
        # TODO : error handling

        # build response
        response = ChatSingleMessage()
        response.set_chat(msg.role, msg.content)
        return response

    def system_name(self):
        return "openai-simple-v0.0.1"
