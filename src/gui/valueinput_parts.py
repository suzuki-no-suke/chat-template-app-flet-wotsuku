import flet as ft


class ValueInputView(ft.UserControl):
    def __init__(self, name) -> None:
        self.gui_resource_list = ft.Dropdown(label="select resource")
        self.name = name
        self.input_value = ft.TextField(
            label=self.name,
            multiline=True,
            min_lines=1,
            max_lines=5)

        super().__init__()

    def build(self): 
        return ft.Column([
            self.input_value,
            ft.Row([
                ft.Checkbox(
                    label="Use resource"
                ),
                self.gui_resource_list
            ]),
        ])

    def set_file_list(self, file_fullpath_list):
        pass

    def get_value(self):
        return self.input_value.value