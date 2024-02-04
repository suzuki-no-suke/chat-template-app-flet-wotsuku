import src.chat.i_chat as ichat

import src.data.chat_history as chat_hist

import pathlib
import textwrap
import google.generativeai as genai

class GeminiProFreeBot(ichat.IChatSendAndResponse):
    """
    Rubberduck never says, only you can talk to rubberduck
    """
    def config(self, config_dict):
        """
        config 
            - GOOGLE_API_KEY
        """
        self.config = config_dict
        genai.configure(
            api_key=self.config["GOOGLE_API_KEY"]
        )
        self.client = genai.GenerativeModel('gemini-pro')
        print(f"gemini pro -> {self.client}")
        return self

    def send(self, chat_environ):
        # build multi-turn messages
        history = chat_environ["history"]
        message_list = []
        for m in history:
            chat_role = "model"
            if m.role == "user":
                chat_role = "user"
            message_list.append({
                "role" : chat_role,
                "parts" : m.message,
            })

        generated_content = self.client.generate_content(message_list)

        print(generated_content)

        # anarlyse response and errors
        # TODO _ error handling

        # build response
        response = ichat.ChatSingleMessage()
        response.set_chat("assistant", generated_content.text)

        return response

    def system_name(self):
        return "gemini-pro-free-nonvision-v0.0.1"
