import flet as ft
# Icons are used directly as strings in this version of Flet
# Using direct color values instead of flet.colors
from typing import Dict, Any, Callable, Optional
import asyncio
import logging

# Import base view
from .base_view import BaseView

# Import shared components
from shared.auth import auth_service
from shared.components.login_form import LoginForm

# Configure logging
logger = logging.getLogger(__name__)

class LoginView(BaseView):
    """Login view for user authentication"""
    
    def __init__(self, app):
        super().__init__(app)
        self.login_form = LoginForm(
            on_success=self._on_login_success,
            on_error=self._on_login_error
        )
    
    def build(self) -> ft.Control:
        """Build the login view"""
        # Create a responsive container
        content = ft.Container(
            content=ft.Column(
                [
                    # Header
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(
                                    name="GAVEL",
                                    size=48,
                                    color='#1976D2'  # Blue 700
                                ),
                                ft.Text(
                                    "Lawyer Office",
                                    size=32,
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Text(
                                    "Sign in to access your account",
                                    size=16,
                                    color='#757575',  # Grey 600
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        margin=ft.margin.only(bottom=40),
                    ),
                    
                    # Login form
                    ft.Card(
                        content=ft.Container(
                            content=self.login_form,
                            padding=40,
                            width=400,
                        ),
                        elevation=8,
                    ),
                    
                    # Footer
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text("Don't have an account?"),
                                ft.TextButton(
                                    text="Contact Admin",
                                    on_click=self._contact_admin,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        margin=ft.margin.only(top=20),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
            expand=True,
            alignment=ft.alignment.center,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[
                    ft.colors.BLUE_50,
                    ft.colors.WHITE,
                ],
            ),
        )
        
        return content
    
    async def _on_login_success(self, user_data: Dict[str, Any]):
        """Handle successful login"""
        logger.info(f"User {user_data.get('username')} logged in successfully")
        await self.app.go_to('/dashboard')
        await self.show_snackbar("Login successful!", "success")
    
    async def _on_login_error(self, error: str):
        """Handle login error"""
        logger.error(f"Login error: {error}")
        await self.show_snackbar(f"Login failed: {error}", "error")
    
    async def _contact_admin(self, e):
        """Handle contact admin button click"""
        await self.show_snackbar("Please contact your system administrator for account access.", "info")

# For testing the view directly
if __name__ == "__main__":
    async def main(page: ft.Page):
        # Configure page
        page.title = "Lawyer Office - Login"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.window_width = 1200
        page.window_height = 800
        
        # Create a mock app for testing
        class MockApp:
            def __init__(self, page):
                self.page = page
            
            async def go_to(self, route):
                print(f"Navigating to: {route}")
            
            async def show_snackbar(self, message, color=None):
                await self.page.show_snackbar(
                    ft.SnackBar(
                        content=ft.Text(message),
                        bgcolor=color or '#2196F3',  # Blue 500
                    )
                )
        
        # Initialize and add the login view
        login_view = LoginView(MockApp(page))
        await login_view.initialize()
        page.add(login_view.view)
        await page.update_async()
    

    ft.app(target=main)
