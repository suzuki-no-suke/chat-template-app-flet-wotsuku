import flet as ft


class ValueInputView(ft.UserControl):
    def __init__(self) -> None:
        self.gui_resource_list = ft.Dropdown(label="select resource")

        super().__init__()

    def build(self): 
        return ft.Column([
            ft.TextField(
                label="value",
                max_lines=5
            ),
            ft.Row([
                ft.Checkbox(
                    label="Use resource"
                ),
                self.gui_resource_list
            ]),
        ])

