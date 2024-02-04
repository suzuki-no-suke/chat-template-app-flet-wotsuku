import flet as ft
from dotenv import load_dotenv
from ulid import ULID
import os
import pickle
from datetime import datetime
import re
import jinja2

import src.orm.base as orm_base
import src.orm.table.chat_history as orm_chat

import src.gui.valueinput_parts as gui_value
import src.gui.chat_parts as gui_chat

import src.data.chat_history as data_history
import src.data.chat_template as data_template

import src.chat.i_chat as chatbot_basics
import src.chat.rubber_duck as chatbot_duck
import src.chat.squash_wall as chatbot_squash_wall
import src.chat.openai_simple as chatbot_openai_simple
import src.chat.openai_gpt4 as chatbot_openai_gpt4
import src.chat.gemini_pro as chatbot_gemini_pro_free

# -------------------------------------------------------------
def main(page: ft.Page):
    page.title = "Chat Template with Flet (Wotsuku)"

    loaded_bots_dict = {}

    current_bot = chatbot_squash_wall.SquashWall()

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

        # check list update need or not
        history_added = False
        if current_chat_history.history_id is None:
            history_added = True

        # save history
        db = orm_base.SQLFactory.default_env()
        saver = orm_chat.ChatHistoryTable(db)
        history_id = saver.upsert_history(
            current_chat_history.history_id,
            current_chat_history.system + " - " + datetime.now().strftime("%Y-%m-%d %H:%M"),
            current_chat_history.gether_chat(),
            initial_info.gether_info(),
        )
        current_chat_history.history_id = history_id

        if history_added:
            load_chat_history()
            # select last added value

    def load_chat_history():
        drp_chat_history_selection.options.clear()
        db = orm_base.SQLFactory.default_env()
        loader = orm_chat.ChatHistoryTable(db)
        all_chat_data = loader.get_history_all()
        drp_chat_history_selection.options = [
            ft.dropdown.Option(key=data[0], text=data[1]) for data in all_chat_data]
        page.update()

    def initialize_app():
        load_chat_history()
        load_template_filelist()
        load_chatbot_list()
        load_edit_target_templates()
    
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
        drp_template_file_selection.options = [
            ft.dropdown.Option(
                key=os.path.join(dir, filename),
                text=filename
            ) for filename in file_list ]

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

    def load_template_edit_target_contents(filepath):
        # load whole contents
        with open(filepath, 'rt', encoding='utf-8') as file:
            file_contents = file.read()
        txt_edit_template.value = file_contents

        page.update()

    def render_template():
        template_text = txt_template_contents.value
        mappings = {iv.name: iv.get_value() for iv in ui_valueinput_variables_view.controls}
        rendered_template = jinja2.Template(template_text).render(mappings)

        ui_chat_message.value = rendered_template

    def load_chatbot_list():
        bots = [
            chatbot_squash_wall.SquashWall(),
            chatbot_basics.EchoBot(),
            chatbot_duck.RubberDuckBot(),
            chatbot_openai_simple.OpenAISimpleBot().config({"OPENAI_API_KEY" : os.getenv("OPENAI_API_KEY")}),
            chatbot_openai_gpt4.OpenAIGPT4Bot().config({"OPENAI_API_KEY" : os.getenv("OPENAI_API_KEY")}),
            chatbot_gemini_pro_free.GeminiProFreeBot().config({"GOOGLE_API_KEY" : os.getenv("GOOGLE_GEMINI_API_KEY")})
        ]

        nonlocal loaded_bots_dict
        loaded_bots_dict = {b.system_name():b for b in bots}

        print(loaded_bots_dict)

        drp_chat_model_selection.options.clear()
        drp_chat_model_selection.options = [
            ft.dropdown.Option(
                key=name,
            )
            for name, _ in loaded_bots_dict.items()
        ]

        page.update()

    def load_edit_target_templates():
        # TODO : out to not .env config
        dir = os.path.abspath(os.getenv("DIR_TEMPLATES"))
        
        # load all .j2 file in dir
        file_list = [f for f in os.listdir(dir) if f.endswith('.j2')]
        print(file_list)

        # set file list to dropdown
        drp_edit_template_selection.options.clear()
        drp_edit_template_selection.options = [
            ft.dropdown.Option(
                key=os.path.join(dir, filename),
                text=filename
            ) for filename in file_list ]

        page.update()

    def send_status_message(msg):
        print(msg)

    def save_template_file_as(filepath, contents):
        with open(filepath, "wt", encoding="utf-8") as f:
            f.write(contents)

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
        print(f"current bot -> {current_bot.system_name()} + {chat_environ}")

        bot_response = current_bot.send(chat_environ)
        if bot_response:
            ui_chat_history.add_chat(bot_response.role, bot_response.message)

        ui_chat_message.value = ""

        # save chat log
        save_current_chatlog()
        
        ui_chat_message.focus()

        page.update()

    def on_click_chat_send_as_bot(e):
        msg = ui_chat_message.value
        if not msg:
            return

        ui_chat_history.add_chat("assistant", msg)

        ui_chat_message.value = ""

        # save chat log
        save_current_chatlog()
        
        ui_chat_message.focus()

        page.update()

    def on_change_drp_chat_history(e):
        key = drp_chat_history_selection.value

        db = orm_base.SQLFactory.default_env()
        reader = orm_chat.ChatHistoryTable(db)
        existing_chat_hist = reader.get_history_recode(key)

        current_chat_history.history_id = existing_chat_hist.history_id
        current_chat_history.expand_chat(pickle.loads(existing_chat_hist.chat_log))

        ui_chat_history.apply_chat_history(current_chat_history.history)
        
        page.update()

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

    def on_change_drp_chatbot(e):
        value = drp_chat_model_selection.value
        nonlocal current_bot
        current_bot = loaded_bots_dict[value]
        print(f"current bot changed = {value} / {current_bot}")

    def on_change_drp_edit_template_select(e):
        value = drp_edit_template_selection.value
        load_template_edit_target_contents(value)
        page.update()

    def on_click_edit_template_clear(e):
        drp_edit_template_selection.value = None
        txt_edit_template.value = ""
        page.update()

    def on_click_edit_relod_template(e):
        value = drp_edit_template_selection.value
        if not value:
            send_status_message("template dosen't saved / loaded file")
            return
        if not os.path.exists(value):
            send_status_message(f"template does not found, deleted. {value}")
            return

        # reload
        load_template_edit_target_contents(value)
        page.update()

    def on_click_edit_save_overwrite(e):
        value = drp_edit_template_selection.value
        if value is None:
            send_status_message("template dosen't saved / loaded file")
            return

        contents = txt_edit_template.value
        filepath = os.path.join(os.path.abspath(os.getenv("DIR_TEMPLATES")), value)
        save_template_file_as(filepath, contents)
        load_template_edit_target_contents(filepath)

        send_status_message(f"file saved as {filepath}")

        page.update()

    def on_click_edit_saveas(e):
        # TODO : if porting to web or other platform, it maybe need change
        overlay_dialog_filesave.save_file(
            dialog_title="Save as template",
            initial_directory=os.path.abspath(os.getenv("DIR_TEMPLATES")))


    def on_result_pick_file_save(e):
        print(overlay_dialog_filesave.result)
        if overlay_dialog_filesave.result.path is not None:
            contents = txt_edit_template.value
            filepath = overlay_dialog_filesave.result.path
            save_template_file_as(filepath, contents)
            load_template_filelist()
            load_edit_target_templates()

            send_status_message(f"file saved as {filepath}")

        page.update()

    def on_result_template_contents_saveas(e):
        print(overlay_dialog_template_content_filesave.result)
        if overlay_dialog_template_content_filesave.result.path is not None:
            contents = txt_template_contents.value
            filepath = overlay_dialog_template_content_filesave.result.path
            save_template_file_as(filepath, contents)
            load_template_filelist()
            load_edit_target_templates()

            send_status_message(f"template content saved as {filepath}")

        page.update()

    def on_click_reload_template_list(e):
        load_template_filelist()
        page.update()

    def on_click_reload_template_file_content(e):
        value = drp_template_file_selection.value
        send_status_message(f"reload template file -> {value}")
        if value and os.path.exists(value):
            load_template_contents(value)
            page.update()

    def on_click_overwrite_loaded_template(e):
        value = drp_template_file_selection.value
        if value is None:
            on_click_saveas_loaded_template(e)
            return

        contents = txt_template_contents.value
        filepath = value
        save_template_file_as(filepath, contents)
        load_template_contents(filepath)

        send_status_message(f"template contents overwrite : saved as {filepath}")

        page.update()

    def on_click_saveas_loaded_template(e):
        # TODO : if porting to web or other platform, it maybe need change
        overlay_dialog_template_content_filesave.save_file(
            dialog_title="Save as other template",
            initial_directory=os.path.abspath(os.getenv("DIR_TEMPLATES")))

    # ---------------------------------------------------------
    # declare GUI parts
    drp_template_file_selection = ft.Dropdown(
        label="Template file selection",
        options=[],
        expand=True,
        on_change=on_change_drp_template_file_select
    )
    txt_template_contents = ft.TextField(
        label="Chat Template",
        multiline=True,
        min_lines=25,
        expand=True,
        text_size=11,
    )
    drp_chat_model_selection = ft.Dropdown(
        label="Select model",
        options=[],
        on_change=on_change_drp_chatbot,
    )
    drp_chat_history_selection = ft.Dropdown(
        label="Chat history",
        options=[],
        on_change=on_change_drp_chat_history,
    )
    ui_chat_message = ft.TextField(label="Chat message", multiline=True, max_lines=5, text_size=11)
    ui_chat_history = gui_chat.ChatHistoryView()
    drp_edit_template_selection = ft.Dropdown(
        label="Select template",
        options=[],
        on_change=on_change_drp_edit_template_select,
    )
    ui_valueinput_variables_view = ft.Column([], scroll=True)
    txt_edit_template = ft.TextField(label="Edit template", multiline=True, min_lines=30, expand=True, text_size=11)
    overlay_dialog_filesave = ft.FilePicker(on_result=on_result_pick_file_save)
    overlay_dialog_template_content_filesave = ft.FilePicker(on_result=on_result_template_contents_saveas)

    # ---------------------------------------------------------
    # building tag contents
    cont_tab_chat_template = ft.Container(
        ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        drp_template_file_selection,
                        ft.ElevatedButton("List Reload", on_click=on_click_reload_template_list),
                        ft.ElevatedButton("File Reload", on_click=on_click_reload_template_file_content),
                    ]),
                    txt_template_contents,
                    ft.Row([
                        ft.ElevatedButton("Overwrite", on_click=on_click_overwrite_loaded_template),
                        ft.ElevatedButton("Save as", on_click=on_click_saveas_loaded_template),
                    ]),
                ]),
                expand=True
            ),
            ft.VerticalDivider(),
            ft.Container(
                content=ft.Column([
                    ft.Text("input values"),
                    ft.ElevatedButton("Generate", on_click=on_click_generate),
                    ui_valueinput_variables_view,
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO)
            )
        ])
    )
    cont_tab_chat_and_history = ft.Container(
        ft.Column([
                ft.Row([
                    drp_chat_model_selection
                    ]),
                ft.ResponsiveRow([
                        ft.Column([
                                ft.ElevatedButton("Clear Chat", on_click=on_click_clear_history),
                            ], col=2,
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Column([
                                drp_chat_history_selection,
                            ], col=10)
                    ],
                    alignment=ft.alignment.center),
                ft.ResponsiveRow([
                        ui_chat_history,
                    ],
                    expand=True),
                ft.ResponsiveRow([
                        ft.Column([
                                ft.ElevatedButton("Bot", on_click=on_click_chat_send_as_bot),
                            ],
                            col=1.5,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Column([
                                ui_chat_message,
                            ],
                            col=9,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Column([
                                ft.ElevatedButton("Send", on_click=on_click_chat_send)
                            ],
                            col=1.5,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    ],
                    alignment=ft.alignment.center)
            ]),
        alignment=ft.alignment.center)
    cont_template_edit = ft.Container(
        ft.Column([
            drp_edit_template_selection,
            txt_edit_template,
            ft.Row([
                ft.ElevatedButton("Clear", on_click=on_click_edit_template_clear),
                ft.ElevatedButton("Reload", on_click=on_click_edit_relod_template),
                ft.ElevatedButton("Save", on_click=on_click_edit_save_overwrite),
                ft.ElevatedButton("Save as", on_click=on_click_edit_saveas)
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

    page.overlay.append(overlay_dialog_filesave)
    page.overlay.append(overlay_dialog_template_content_filesave)

    initialize_app()


if __name__=='__main__':
    load_dotenv()
    ft.app(target=main)