from src.chat.i_chat import IChatSendAndResponse
from src.data.chat_history import ChatSingleMessage

from src.orm.table.chat_api_log import ChatApiLogTable
from src.orm.table.chat_purchase import ChatPurchaseTable

import openai

import json

class OpenAISimpleBot(IChatSendAndResponse):
    def config(self, config_dict):
        """
        required datas
        - OPENAI_API_KEY
        - db
        """
        self.config = config_dict
        self.client = openai.OpenAI(
            api_key=config_dict["OPENAI_API_KEY"]
        )
        self.db = config_dict["db"]
        if self.db is None:
            raise ValueError("DB is mandatory")
        return self

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

        # call chat api
        response = ChatSingleMessage()
        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=message_list
            )

            print(completion.model_dump_json(indent=2, exclude_unset=True))

            # save log
            api_log = ChatApiLogTable(self.db)
            log_id = api_log.save_api_log(
                "openai-gpt4-v0.0.1",
                message_list, json.dumps(message_list),
                completion, completion.model_dump_json(indent=2, exclude_unset=True))

            # save purchase log
            purchase_log = ChatPurchaseTable(self.db)
            purchase_log.save_purchase(
                log_id,
                "{{rate}} (Rates @ 2024/02/05, Yen-Dollar Rate : almost 155 yen/dollar)",
                0.000001,
                completion.usage.total_tokens)

            # analyse response and errors
            msg = completion.choices[0].message
            # TODO : error handling

            # build response
            response.set_chat(msg.role, msg.content)
        except openai.APIConnectionError as e:
            print("The server could not be reached")
            print(e.__cause__)  # an underlying Exception, likely raised within httpx.
            response.set_chat("API_error", f"Connection failure. detail -> {e.__cause__}")
        except openai.RateLimitError as e:
            print("A 429 status code was received; we should back off a bit.")
            response.set_chat("API_error", f"Failed by Rate limit.")
        except openai.APIStatusError as e:
            print("Another non-200-range status code was received")
            print(e.status_code)
            print(e.response)
            response.set_chat("API_error", f"API Error -> {e.status_code}, {e.response}")
        return response

    def system_name(self):
        return "openai-simple-v0.0.1"
