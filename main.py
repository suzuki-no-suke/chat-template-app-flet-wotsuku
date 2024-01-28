import flet as ft
from dotenv import load_dotenv
from ulid import ULID
import os
import pickle
from datetime import datetime
import re
import jinja2

import src.orm.base as orm_base
import src.orm.chat_history as orm_chat

import src.gui.valueinput_parts as gui_value
import src.gui.chat_parts as gui_chat

import src.data.chat_history as data_history
import src.data.chat_template as data_template

import src.chat.rubber_duck as chatbot_duck
import src.chat.openai_simple as chatbot_openai_simple

# -------------------------------------------------------------
def main(page: ft.Page):
    page.title = "Chat Template with Flet (Wotsuku)"

    current_bot = chatbot_duck.RubberDuckBot()
    # current_bot = chatbot_openai_simple.OpenAISimpleBot()
    # current_bot.config({"OPENAI_API_KEY" : os.getenv("OPENAI_API_KEY")})

    current_chat_history = data_history.ChatHistory()
    
    # ---------------------------------------------------------
    # intermediate
    def save_current_chatlog():
        # TODO : build adapter class
        chatlog = ui_chat_history.gether_chat_history()
        current_chat_history.history = chatlog
        current_chat_history.system = current_bot.system_name()
        initial_info = data_template.InitialValue()
        initial_info.set_template_by_text("dummy content")
        initial_info.add_input_text_embedded("dummy", "dummy content")

        # build chat history recode
        history_added = False
        if current_chat_history.history_id is None:
            history_added = True
        
        db = orm_base.SQLFactory.default_env()
        with db.session_scope() as sess:
            existing_chat_hist = sess.query(orm_chat.RecodeChatHistory).filter_by(history_id=current_chat_history.history_id).first()
            if existing_chat_hist:
                existing_chat_hist.chat_titleline = current_chat_history.system + datetime.now().strftime("%Y-%m-%d %H:%M")
                existing_chat_hist.chat_log = pickle.dumps(current_chat_history.gether_chat())
                existing_chat_hist.initial_values = pickle.dumps(initial_info.gether_info())
                existing_chat_hist.updated_at = datetime.now()
            else:
                chat_hist = orm_chat.RecodeChatHistory()
                if current_chat_history.history_id is None:
                    current_chat_history.history_id = str(ULID())
                chat_hist.history_id = current_chat_history.history_id
                chat_hist.chat_titleline = current_chat_history.system + datetime.now().strftime("%Y-%m-%d %H:%M")
                chat_hist.chat_log = pickle.dumps(current_chat_history.gether_chat())
                chat_hist.initial_values = pickle.dumps(initial_info.gether_info())
                chat_hist.created_at = datetime.now()
                sess.add(chat_hist)
            sess.commit()

        if history_added:
            load_chat_history()
            # select last added value

    def load_chat_history():
        drp_chat_history_selection.options.clear()
        db = orm_base.SQLFactory.default_env()
        with db.session_scope() as sess:
            all_chat_data = sess.query(orm_chat.RecodeChatHistory.history_id, orm_chat.RecodeChatHistory.chat_titleline).all()
            for data in all_chat_data:
                hist_opt = ft.dropdown.Option(
                    key=data.history_id,
                    text=data.chat_titleline
                )
                drp_chat_history_selection.options.append(hist_opt)
        page.update()

    def initialize_app():
        load_chat_history()
        load_template_filelist()
    
    def clear_chat():
        # TODO : clear method
        current_chat_history.history_id = None
        current_chat_history.history = []

        ui_chat_history.clear()

        drp_chat_history_selection.value = None

        page.update()

    def load_template_filelist():
        # TODO : out to not .env config
        dir = os.path.abspath(os.getenv("DIR_TEMPLATES"))
        
        # load all .j2 file in dir
        file_list = [f for f in os.listdir(dir) if f.endswith('.j2')]
        print(file_list)

        # set file list to dropdown
        drp_template_file_selection.options.clear()
        # TODO : usual appending to list can <internal list directive(?)>
        for filename in file_list:
            fullpath = os.path.join(dir, filename)

            drp_template_file_selection.options.append(
                ft.dropdown.Option(
                    key=fullpath,
                    text=filename
                )
            )

        page.update()

    def load_template_contents(filepath):
        # load whole contents
        with open(filepath, 'rt', encoding='utf-8') as file:
            file_contents = file.read()
        txt_template_contents.value = file_contents
        
        # analysis all jinja2 variable
        variable_names = re.findall(r'{{(.*?)}}', file_contents)
        variable_names = [name.strip() for name in variable_names]

        # set variable input view
        ui_valueinput_variables_view.controls.clear()
        for var in variable_names:
            var_input = gui_value.ValueInputView(var)
            ui_valueinput_variables_view.controls.append(var_input)

        page.update()

    def render_template():
        template_text = txt_template_contents.value
        mappings = {}
        for iv in ui_valueinput_variables_view.controls:
            mappings[iv.name] = iv.get_value()
        rendered_template = jinja2.Template(template_text).render(mappings)

        ui_chat_message.value = rendered_template

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
        save_current_chatlog()

        page.update()

    def on_click_chat_send_as_bot(e):
        msg = ui_chat_message.value
        if not msg:
            return
        
        ui_chat_history.add_chat("assistant", msg)

        ui_chat_message.value = ""

        # save chat log
        save_current_chatlog()

        page.update()

    def on_change_drp_chat_history(e):
        value = drp_chat_history_selection.value

        db = orm_base.SQLFactory.default_env()
        with db.session_scope() as sess:
            existing_chat_hist = sess.query(orm_chat.RecodeChatHistory).filter_by(history_id=value).first()

            current_chat_history.history_id = existing_chat_hist.history_id
            current_chat_history.expand_chat(pickle.loads(existing_chat_hist.chat_log))

            ui_chat_history.apply_chat_history(current_chat_history.history)

    def on_click_clear_history(e):
        clear_chat()
        page.update()

    def on_change_drp_template_file_select(e):
        value = drp_template_file_selection.value
        load_template_contents(value)
        page.update()

    def on_click_generate(e):
        render_template()
        main_tabpages.selected_index = 1
        page.update()

    # ---------------------------------------------------------
    # declare GUI parts
    drp_template_file_selection = ft.Dropdown(
        label="Template file selection",
        options=[],
        on_change=on_change_drp_template_file_select
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
        on_change=on_change_drp_chat_history,
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
    ui_valueinput_variables_view = ft.Column([])

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
                    ft.ElevatedButton("Generate", on_click=on_click_generate),
                    ui_valueinput_variables_view,
                ])
            )
        ])
    )
    cont_tab_chat_and_history = ft.Container(
        ft.Column([
            ft.Row([
                ft.ElevatedButton("Clear Chat", on_click=on_click_clear_history),
                drp_chat_history_selection,
            ]),
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

    initialize_app()


if __name__=='__main__':
    load_dotenv()
    ft.app(target=main)