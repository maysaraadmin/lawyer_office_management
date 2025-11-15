import flet as ft
from typing import Optional, Callable
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# Color constants matching Django web app
BLUE_600 = "#2563EB"
BLUE_500 = "#3B82F6"
BLUE_50 = "#EFF6FF"
GRAY_900 = "#111827"
GRAY_700 = "#374151"
GRAY_500 = "#6B7280"
GRAY_300 = "#D1D5DB"
GRAY_200 = "#E5E7EB"
GRAY_100 = "#F3F4F6"
WHITE = "#FFFFFF"
RED_50 = "#FEF2F2"
RED_600 = "#DC2626"

class LoginView:
    def __init__(self, page: ft.Page, on_login_success: Optional[Callable] = None):
        self.page = page
        self.on_login_success = on_login_success
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        
        # Form fields
        self.email_field = ft.TextField(
            label="Email address",
            hint_text="Enter your email",
            prefix_icon=ft.Icons.EMAIL_OUTLINED,
            border_radius=8,
            border=ft.border.all(1, GRAY_300),
            focused_border_color=BLUE_600,
            keyboard_type=ft.KeyboardType.EMAIL,
        )
        
        self.password_field = ft.TextField(
            label="Password",
            hint_text="Enter your password",
            prefix_icon=ft.Icons.LOCK_OUTLINED,
            password=True,
            can_reveal_password=True,
            border_radius=8,
            border=ft.border.all(1, GRAY_300),
            focused_border_color=BLUE_600,
        )
        
        self.remember_me = ft.Checkbox(
            label="Remember me",
            value=False,
        )
        
        self.error_message = ft.Container(
            content=ft.Text(
                "Invalid email or password",
                color=RED_600,
                size=14,
            ),
            padding=ft.padding.all(12),
            bgcolor=RED_50,
            border_radius=8,
            border=ft.border.all(1, "#FCA5A5"),
            visible=False,
        )
        
        self.loading_indicator = ft.ProgressBar(
            visible=False,
            color=BLUE_600,
        )
        
        self.login_button = ft.ElevatedButton(
            "Sign in",
            icon=ft.Icons.LOGIN,
            bgcolor=BLUE_600,
            color=WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=24, vertical=12),
            ),
            on_click=self._handle_login,
            disabled=False,
        )
        
        self.forgot_password_link = ft.TextButton(
            "Forgot your password?",
            style=ft.ButtonStyle(
                color=BLUE_600,
            ),
            on_click=self._forgot_password,
        )
    
    def build(self) -> ft.Container:
        """Build the login view"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Logo and title
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Container(
                                    content=ft.Icon(
                                        ft.Icons.BALLOT_OUTLINED,
                                        size=64,
                                        color=BLUE_600,
                                    ),
                                    width=120,
                                    height=120,
                                    bgcolor=BLUE_50,
                                    border_radius=60,
                                    alignment=ft.alignment.center,
                                ),
                                ft.Text(
                                    "Lawyer Office",
                                    size=28,
                                    weight=ft.FontWeight.BOLD,
                                    color=GRAY_900,
                                ),
                                ft.Text(
                                    "Sign in to your account",
                                    size=16,
                                    color=GRAY_500,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=16,
                        ),
                        padding=ft.padding.only(bottom=32),
                    ),
                    
                    # Error message
                    self.error_message,
                    
                    # Login form
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                self.email_field,
                                self.password_field,
                                
                                # Remember me and forgot password
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            self.remember_me,
                                            ft.Container(expand=True),
                                            self.forgot_password_link,
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    padding=ft.padding.symmetric(vertical=8),
                                ),
                                
                                # Loading indicator
                                self.loading_indicator,
                                
                                # Login button
                                self.login_button,
                                
                                # Sign up link
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            ft.Text(
                                                "Don't have an account? ",
                                                color=GRAY_500,
                                                size=14,
                                            ),
                                            ft.TextButton(
                                                "Contact administrator",
                                                style=ft.ButtonStyle(
                                                    color=BLUE_600,
                                                ),
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                    padding=ft.padding.only(top=16),
                                ),
                            ],
                            spacing=16,
                        ),
                        padding=ft.padding.all(24),
                        bgcolor=WHITE,
                        border_radius=12,
                        border=ft.border.all(1, GRAY_200),
                        shadow=ft.BoxShadow(
                            spread_radius=0,
                            blur_radius=8,
                            color="#00000010",
                            offset=ft.Offset(0, 2),
                        ),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=ft.padding.all(24),
            bgcolor="#F9FAFB",  # gray-50
            expand=True,
        )
    
    def _handle_login(self, e):
        """Handle login button click"""
        email = self.email_field.value
        password = self.password_field.value
        
        if not email or not password:
            self.error_message.content.value = "Please enter both email and password"
            self.error_message.visible = True
            self.page.update()
            return
        
        # Clear error
        self.error_message.visible = False
        self.loading_indicator.visible = True
        self.login_button.disabled = True
        self.login_button.text = "Signing in..."
        self.page.update()
        
        # Perform login
        asyncio.run(self._perform_login(email, password))
    
    async def _perform_login(self, email: str, password: str) -> None:
        """Perform API login"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/api/auth/login/",
                    json={"email": email, "password": password},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Store authentication data
                    if self.on_login_success:
                        self.on_login_success(data)
                else:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("detail", "Login failed")
                    self._show_error(error_msg)
                    
        except httpx.TimeoutException:
            self._show_error("Connection timeout. Please try again.")
        except httpx.RequestError:
            self._show_error("Network error. Please check your connection.")
        except Exception as e:
            self._show_error("An unexpected error occurred.")
        finally:
            # Reset loading state
            self.loading_indicator.visible = False
            self.login_button.disabled = False
            self.page.update()
    
    def _show_error(self, message: str) -> None:
        """Show error message"""
        self.error_message.content.value = message
        self.error_message.visible = True
        self.page.update()
    
    def _forgot_password(self, e: ft.ControlEvent) -> None:
        """Handle forgot password click"""
        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Password Reset"),
                content=ft.Text(
                    "Please contact your administrator to reset your password."
                ),
                actions=[
                    ft.TextButton("OK", on_click=lambda _: self.page.close_dialog()),
                ],
            )
        )
    
    def clear_form(self) -> None:
        """Clear the login form"""
        self.email_field.value = ""
        self.password_field.value = ""
        self.remember_me.value = False
        self.error_message.visible = False
        self.page.update()
