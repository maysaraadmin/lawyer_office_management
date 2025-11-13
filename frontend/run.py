import flet as ft
from src.app import main

if __name__ == "__main__":
    # Run the Flet app in web browser mode
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        port=8503,  # Changed to 8503 to ensure no conflicts
        host="127.0.0.1"
    )
