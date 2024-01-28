import flet as ft
from dotenv import load_dotenv
from ulid import ULID

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
import pickle
from datetime import datetime

import src.gui.valueinput_parts as gui_value
import src.gui.chat_parts as gui_chat

import src.chat.rubber_duck as chatbot_duck
import src.chat.openai_simple as chatbot_openai_simple

# -------------------------------------------------------------
def main(page: ft.Page):
    page.title = "Chat Template with Flet (Wotsuku)"

    # current_bot = chatbot_duck.RubberDuckBot()
    current_bot = chatbot_openai_simple.OpenAISimpleBot()
    current_bot.config({"OPENAI_API_KEY" : os.getenv("OPENAI_API_KEY")})


    # ---------------------------------------------------------
    # event handler
    def on_click_chat_send(e):
        msg = ui_chat_message.value
        if not msg:
            return
        
        last_send = ui_chat_history.add_chat("user", msg)

        # build chat_environ
        chat_environ = {
            "last_send" : last_send,
            "history" : ui_chat_history.gether_chat_history()
        }

        # wait for response
        bot = current_bot.send(chat_environ)
        ui_chat_history.add_chat(bot.role, bot.message)

        ui_chat_message.value = ""

        # save chat log

        page.update()

    def on_click_chat_send_as_bot(e):
        msg = ui_chat_message.value
        if not msg:
            return
        
        ui_chat_history.add_chat("assistant", msg)

        ui_chat_message.value = ""

        # save chat log

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
    )
    ui_chat_message = ft.TextField(label="Chat message")
    ui_chat_history = gui_chat.ChatHistoryView()
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
            ui_chat_history,
            ft.Row([
                ft.ElevatedButton("Bot", on_click=on_click_chat_send_as_bot),
                ui_chat_message,
                ft.ElevatedButton("Send", on_click=on_click_chat_send)
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



if __name__=='__main__':
    load_dotenv()
    ft.app(target=main)