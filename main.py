import flet as ft
from datetime import datetime

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
            ChatMessage("assistant", "hello", True, datetime.now()),
            ChatMessage("user", "world", True, datetime.now())
        ])

# -------------------------------------------------------------
# core code
def main(page: ft.Page):
    page.title = "Chat Template with Flet (Wotsuku)"

    # ---------------------------------------------------------
    # declare GUI event function

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
        options=[
            ft.dropdown.Option("history 1"),
            ft.dropdown.Option("history 2"),
            ft.dropdown.Option("history 3"),
        ]
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
        ft.Row([
            drp_chat_history_selection,
            ChatHistory()
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
            ft.Text("configuration editor under construction")
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
    ft.app(target=main)