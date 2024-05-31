import flet as ft
import matplotlib.pyplot as plt
from flet_core.matplotlib_chart import MatplotlibChart


def main(page: ft.Page):
    page.window_width = 900
    def page_resize(e):
        pw.value = f"{page.width} px"
        pw.update()
    txt_number = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    def minus_click(e):
        txt_number.value = str(int(txt_number.value) - 1)
        page.update()

    def plus_click(e):
        txt_number.value = str(int(txt_number.value) + 1)
        page.update()
    page.on_resize = page_resize

    def pick_files_result(e: ft.FilePickerResultEvent):
        selected_files.value = (
            ", ".join(map(lambda f: f.name, e.files)) if e.files else "Cancelled!"
        )
        selected_files.update()

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    selected_files = ft.Text()

    page.overlay.append(pick_files_dialog)
    pw = ft.Text(bottom=50, right=50, style="displaySmall")
    page.overlay.append(pw)
    page.add(
        ft.Row(
            [
                ft.ElevatedButton(
                    "Pick image",
                    icon=ft.icons.UPLOAD_FILE,
                    on_click=lambda _: pick_files_dialog.pick_files(
                        allow_multiple=True
                    ),
                ),
                selected_files,
            ]
        ),
        ft.Row(
            [
                ft.ElevatedButton(
                    "Pick image",
                    icon=ft.icons.UPLOAD_FILE,
                    on_click=lambda _: pick_files_dialog.pick_files(
                        allow_multiple=True
                    ),
                ),
                selected_files,
            ]
        ),
        ft.ResponsiveRow(
            [

                ft.Container(
                    txt_number,
                    padding=5,
                    bgcolor=ft.colors.GREEN,
                    col={"sm": 6, "md": 4, "xl": 2},
                ),
                ft.Container(
                    ft.IconButton(ft.icons.ADD, on_click=plus_click),
                    padding=5,
                    bgcolor=ft.colors.BLUE,
                    col={"sm": 6, "md": 4, "xl": 2},
                ),
                ft.Container(
                    height=500,
                    alignment="left"
                )
            ]
        )
    )
    page_resize(None)


ft.app(main)