import flet as ft
from dotenv import load_dotenv
import ulid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


import os
import pickle
from datetime import datetime

import src.initialize

# -------------------------------------------------------------

class ValueInput(ft.UserControl):
    def build(self):
        return ft.Column([
            ft.TextField(
                label="value",
                max_lines=5
            ),
            ft.Row([
                ft.Checkbox(
                    label="Use file"
                ),
                ft.Dropdown(
                    label="file select",
                    options=[
                        ft.dropdown.Option("file 1"),
                        ft.dropdown.Option("file 2"),
                        ft.dropdown.Option("file 3"),
                    ]
                ),
            ]),
        ])

class ChatInput(ft.UserControl):
    def build(self):
        return ft.Row([
            ft.ElevatedButton("Bot"),
            ft.TextField(label="message"),
            ft.ElevatedButton("Send")
        ])

class ChatMessage(ft.UserControl):
    def __init__(self, role, message, is_right=True, msg_time=datetime.now()):
        self.role = role
        self.message = message
        self.is_right = is_right
        self.msg_time = msg_time

        super().__init__()

    def build(self):
        time_text = self.msg_time.strftime("%H:%M")
        role_text = self.role
        if self.is_right:
            return ft.Row([
                ft.TextField(
                    label=f"{role_text} - {time_text}",
                    multiline=True),
                ft.Icon(name=ft.icons.FAVORITE),
            ])
        else:
            return ft.Row([
                ft.Icon(name=ft.icons.FAVORITE),
                ft.TextField(
                    label=f"{role_text} - {time_text}",
                    multiline=True),
            ])


class ChatHistory(ft.UserControl):
    def build(self):
        return ft.Column([
            ChatMessage("system", "test", False, datetime.now()),
            ChatMessage("assistant", "hello", False, datetime.now()),
            ChatMessage("user", "world", True, datetime.now())
        ])

# -------------------------------------------------------------
# ORM extention

def get_default_db():
    engine = create_engine(os.getenv("DB_CONNECTION"), echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    return session

def gen_id():
    return str(ulid.new())

class DBChatHistory:
    def load_single_chat(self, history_id):
        session = get_default_db()
        chat_history = session.query(ChatHistory).filter(ChatHistory.history_id == history_id).first()
        if chat_history:
            single_chat_history = KeepSingleChatHistory()
            single_chat_history.history_id = chat_history.history_id
            single_chat_history.title = chat_history.chat_titleline
            single_chat_history.chat = pickle.loads(chat_history.chat_log)
            single_chat_history.additional = pickle.loads(chat_history.initial_values)
            return single_chat_history
        else:
            return None

    def save(self, chat_history):
        session = get_default_db()
        history_id = None
        if chat_history.id is None:
            history_id = gen_id()

            # Insert new chat history
            new_chat_history = ChatHistory(
                history_id=history_id,
                chat_log=pickle.dumps(chat_history.chat),
                initial_values=pickle.dumps(chat_history.additional),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(new_chat_history)
        else:
            history_id = chat_history.id

            # Update existing chat history
            update_chat_history = session.query(ChatHistory).filter(ChatHistory.history_id == chat_history.id).first()
            if update_chat_history:
                update_chat_history.chat_log = pickle.dumps(chat_history.chat)
                update_chat_history.initial_values = pickle.dumps(chat_history.additional)
                update_chat_history.updated_at = datetime.now()
        session.commit()

        return history_id

    def load_history_list(self):
        session = get_default_db()
        chat_histories = session.query(ChatHistory.history_id, ChatHistory.chat_titleline).all()
        return [(chat.history_id, chat.chat_titleline) for chat in chat_histories]

# -------------------------------------------------------------
# data control classes
class KeepSingleChatHistory:
    def __init__(self, chat=[], additional={}):
        self.id = None
        self.title = ""
        self.chat = []
        self.additional = {}

    def add_chat(self, role, msg, time):
        self.chat.append(
            {
                "role" : role,
                "message" : msg,
                "time": time
            }
        )
        self.title = time.strftime("%Y-%m-%d %H:%M")

    def save(self, dbobj):
        dbobj.save(self)





# -------------------------------------------------------------
# core code
def main(page: ft.Page):
    page.title = "Chat Template with Flet (Wotsuku)"

    # ---------------------------------------------------------
    # Glue functionarity
    def load_chat_history():
        pass

    def save_chat():
        pass

    def send_chat():
        pass

    def send_chat_as_bot():
        pass

    def generate_template():
        pass

    # ---------------------------------------------------------
    # in tab page functionarity
    # tab - template input
    def set_template_filelist():
        pass

    def select_template_file():
        pass

    # tab - chat message
    def set_chat_history_list():
        pass


    # ---------------------------------------------------------
    # declare GUI event function
    def btn_ev_send_chat(e):
        send_chat()
        save_chat()
        page.update()

    def btn_ev_send_as_bot(e):
        send_chat_as_bot()
        save_chat()
        page.update()

    def drp_ev_select_chat_history(e):
        save_chat()
        load_chat_history()
        page.update()

    # ---------------------------------------------------------
    def initialize_application():
        load_chat_history()
        page.update()

    # ---------------------------------------------------------
    # declare GUI parts
    drp_template_file_selection = ft.Dropdown(
        label="Template file selection",
        options=[
            ft.dropdown.Option("file 1"),
            ft.dropdown.Option("file 2"),
            ft.dropdown.Option("file 3"),
        ]
    )
    txt_template_contents = ft.TextField(
        label="Chat Template",
        multiline=True,
        min_lines=25,
        max_lines=25,
    )
    drp_chat_history_selection = ft.Dropdown(
        label="Chat history",
        options=[],
        on_change=drp_ev_select_chat_history
    )
    drp_template_file_viewer_selection = ft.Dropdown(
        label="Select template",
        options=[
            ft.dropdown.Option("file 1"),
            ft.dropdown.Option("file 2"),
            ft.dropdown.Option("file 3"),
        ]
    )


    # ---------------------------------------------------------
    # building tag contents
    cont_tab_chat_template = ft.Container(
        ft.Row([
            ft.Container(
                content=ft.Column([
                    drp_template_file_selection,
                    txt_template_contents,
                ]),
                expand=True
            ),
            ft.VerticalDivider(),
            ft.Container(
                content=ft.Column([
                    ft.Text("input values"),
                    ValueInput(),
                    ValueInput(),
                    ft.Row([
                        ft.ElevatedButton("Generate")
                    ])
                ])
            )
        ])
    )
    cont_tab_chat_and_history = ft.Container(
        ft.Column([
            drp_chat_history_selection,
            ChatHistory(),
            ft.Row([
                ft.ElevatedButton("Bot", on_click=btn_ev_send_as_bot),
                ft.TextField(label="Chat message"),
                ft.ElevatedButton("Send", on_click=btn_ev_send_chat)
            ])
        ])
    )
    cont_template_edit = ft.Container(
        ft.Column([
            drp_template_file_viewer_selection,
            ft.TextField(
                multiline=True,
                min_lines=3,
            ),
            ft.Row([
                ft.ElevatedButton("Create"),
                ft.ElevatedButton("Reload"),
                ft.ElevatedButton("Save"),
                ft.ElevatedButton("Save as")
            ])
        ])
    )
    cont_resource_viewer = ft.Container(
        ft.Column([
            ft.Row([
                ft.Dropdown(
                    label="folder select",
                    options=[
                        ft.dropdown.Option("file 1"),
                        ft.dropdown.Option("file 2"),
                        ft.dropdown.Option("file 3"),
                    ]
                ),
                ft.ElevatedButton("add folder")
            ]),
            ft.Row([
                ft.Dropdown(
                    label="file select",
                    options=[
                        ft.dropdown.Option("file 1"),
                        ft.dropdown.Option("file 2"),
                        ft.dropdown.Option("file 3"),
                    ]
                ),
                ft.ElevatedButton("Create")
            ]),
            ft.TextField(
                multiline=True,
                min_lines=3,
            ),
            ft.Row([
                ft.ElevatedButton("Reload"),
                ft.ElevatedButton("Save"),
                ft.ElevatedButton("Save as")
            ])
        ])
    )
    cont_edit_config = ft.Container(
        ft.Column([
            ft.Text("configuration editor under construction"),
            ft.ElevatedButton("Migrate data"),
        ])
    )

    # ---------------------------------------------------------
    # building app
    main_tabpages = ft.Tabs(
        scrollable=True,
        expand=True
    )

    tab_chat_template = ft.Tab(
        text="Chat Template",
        content=cont_tab_chat_template)
    tab_chat_and_history = ft.Tab(
        text="Chat & History",
        content=cont_tab_chat_and_history)
    tab_template_edit = ft.Tab(
        text="Template Edit",
        content=cont_template_edit)
    tab_resource_viewer = ft.Tab(
        text="Resource Viewer",
        content=cont_resource_viewer)
    tab_configuration = ft.Tab(
        text="Configuration",
        content=cont_edit_config)
    
    main_tabpages.tabs.append(tab_chat_template)
    main_tabpages.tabs.append(tab_chat_and_history)
    main_tabpages.tabs.append(tab_template_edit)
    main_tabpages.tabs.append(tab_resource_viewer)
    main_tabpages.tabs.append(tab_configuration)
    
    page.add(main_tabpages)

    initialize_application()


if __name__=='__main__':
    load_dotenv()
    src.initialize.init_app()
    ft.app(target=main)