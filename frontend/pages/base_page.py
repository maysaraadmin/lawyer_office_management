import flet as ft
from typing import Optional, Dict, Any
from ..services.api_client import auth_service

class BasePage:
    """Base class for all pages with common functionality"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.padding = 0
        self.page.spacing = 0
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_min_width = 1024
        self.page.window_min_height = 768
        self.page.window_width = 1280
        self.page.window_height = 900
        self.page.window_resizable = True
        self.page.window_maximized = True
        self.page.title = "Lawyer Office Management"
        self.page.fonts = {
            "Roboto": "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap"
        }
        self.page.theme = ft.Theme(
            font_family="Roboto",
            color_scheme_seed=ft.colors.BLUE,
        )
    
    async def check_auth(self) -> bool:
        """Check if user is authenticated"""
        if not auth_service.is_authenticated():
            from .login import LoginPage
            login_page = LoginPage(self.page)
            await login_page.initialize()
            return False
        return True
    
    def navigate_to(self, route: str):
        """Navigate to a route"""
        self.page.go(route)
    
    def show_loading(self, message: str = "Loading..."):
        """Show loading indicator"""
        self.page.clean()
        self.page.add(
            ft.Column(
                [
                    ft.ProgressRing(),
                    ft.Text(message)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
        )
        self.page.update()
    
    def show_error(self, message: str, title: str = "Error"):
        """Show error dialog"""
        def close_dialog(_):
            dlg.open = False
            self.page.update()
        
        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    def show_snackbar(self, message: str, color: str = None):
        """Show a snackbar message"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color or ft.colors.BLUE,
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    async def handle_error(self, error: Exception, default_message: str = "An error occurred"):
        """Handle API errors consistently"""
        error_message = str(error) or default_message
        self.show_error(error_message)
        # Log the error for debugging
        import logging
        logging.error(f"Error: {error}", exc_info=True)
