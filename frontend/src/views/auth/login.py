import flet as ft
from flet import icons
import sys
import os
import asyncio
import logging
import traceback
from typing import Optional, Dict, Any, Callable

# Configure logging
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Import from the services package
from services import auth_service, api_client
from services.storage import Storage

class LoginForm(ft.Container):
    def __init__(self, on_login_success: Callable):
        self.on_login_success = on_login_success
        
        # Form fields
        self.email = ft.TextField(
            label="Email",
            hint_text="Enter your email",
            keyboard_type=ft.KeyboardType.EMAIL,
            prefix_icon=ft.icons.EMAIL_OUTLINED,
            border_radius=10,
            width=400,
        )
        
        self.password = ft.TextField(
            label="Password",
            hint_text="Enter your password",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.icons.LOCK_OUTLINED,
            border_radius=10,
            width=400,
        )
        
        self.error_text = ft.Text(
            "",
            color="red",
            visible=False,
        )
        
        self.login_button = ft.ElevatedButton(
            "Login",
            width=400,
            height=50,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=20,
            ),
            on_click=self.login_click,
        )
        
        # Initialize container with form content
        super().__init__(
            content=ft.Column(
                [
                    ft.Text("Login", size=24, weight="bold"),
                    self.email,
                    self.password,
                    self.error_text,
                    ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                    self.login_button,
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=40,
            width=500,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.BLUE_GREY_300,
                offset=ft.Offset(0, 0),
            )
        )
    
    async def login_click(self, e):
        """Handle login button click"""
        try:
            # Validate inputs
            if not self.email.value or not self.password.value:
                self.error_text.value = "Please fill in all fields"
                self.error_text.visible = True
                if hasattr(self, 'update_async'):
                    await self.update_async()
                return

            # Update UI for loading state
            self.error_text.visible = False
            self.login_button.disabled = True
            self.login_button.text = "Logging in..."
            if hasattr(self, 'update_async'):
                await self.update_async()

            try:
                # Make login request to the backend
                response = await api_client.post(
                    'auth/login/',
                    json={
                        'email': self.email.value,
                        'password': self.password.value
                    }
                )

                if response and response.get('access'):
                    # Store tokens and user data
                    Storage.set('access_token', response['access'])
                    if 'refresh' in response:
                        Storage.set('refresh_token', response['refresh'])
                    if 'user' in response:
                        Storage.set('user', response['user'])
                    
                    # Call the success callback
                    if self.on_login_success:
                        if asyncio.iscoroutinefunction(self.on_login_success):
                            await self.on_login_success()
                        else:
                            self.on_login_success()
                else:
                    self.error_text.value = response.get('detail', 'Login failed. Please try again.') if response else 'Login failed. Please try again.'
                    self.error_text.visible = True
                    self.login_button.disabled = False
                    self.login_button.text = "Login"
                    if hasattr(self, 'update_async'):
                        await self.update_async()

            except Exception as e:
                logger.error(f"Login error: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Handle specific error cases
                error_msg = str(e)
                if 'Unable to connect to the server' in error_msg or 'Network' in error_msg:
                    self.error_text.value = "Unable to connect to the server. Please check your internet connection."
                elif '401' in error_msg or '403' in error_msg:
                    self.error_text.value = "Invalid email or password. Please try again."
                else:
                    self.error_text.value = "An unexpected error occurred. Please try again."
                
                # Reset UI state
                self.error_text.visible = True
                self.login_button.disabled = False
                self.login_button.text = "Login"
                if hasattr(self, 'update_async'):
                    await self.update_async()
                    
        except Exception as e:
            logger.error(f"Unexpected error in login_click: {str(e)}")
            logger.error(traceback.format_exc())

# For testing the login form directly
async def main(page: ft.Page):
    page.title = "Login"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    
    async def on_login_success():
        print("Login successful!")
        # In a real app, you would navigate to the main app here
        await page.go("/dashboard")
    
    login_form = LoginForm(on_login_success)
    await page.add_async(login_form)

# Run the app
if __name__ == "__main__":
    ft.app(target=main)
