import flet as ft
from flet_core import UserControl

# Use string colors for compatibility
GREY_600 = "#757575"  # Equivalent to ft.colors.GREY_600

class LoginForm(UserControl):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.username = ft.TextField(
            label="Username",
            hint_text="Enter your username",
            width=400,
        )
        self.password = ft.TextField(
            label="Password",
            hint_text="Enter your password",
            width=400,
            password=True,
            can_reveal_password=True,
        )
        self.error_text = ft.Text("", color="red")
        
    async def login_click(self, e):
        if not self.username.value or not self.password.value:
            self.error_text.value = "Please fill in all fields"
            await self.update_async()
            return
            
        # For now, just log in with any non-empty credentials
        self.on_login_success()
    
    def build(self):
        # Style the form controls
        self.username.border_radius = 5
        self.username.border_color = "#e0e0e0"
        self.username.bgcolor = "#ffffff"
        self.username.text_size = 14
        
        self.password.border_radius = 5
        self.password.border_color = "#e0e0e0"
        self.password.bgcolor = "#ffffff"
        self.password.text_size = 14
        
        login_button = ft.ElevatedButton(
            "Login",
            on_click=self.login_click,
            width=400,
            height=45,
            color="#ffffff",  # White text
            bgcolor="#1e88e5",  # Blue 600
        )
        
        return ft.Container(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Welcome Back!", size=28, weight=ft.FontWeight.BOLD, color="#1a237e"),
                                    ft.Text("Please sign in to continue", color=GREY_600, size=14),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                            ),
                            padding=20,
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    self.username,
                                    ft.Container(height=15),
                                    self.password,
                                    ft.Container(height=5),
                                    self.error_text,
                                    ft.Container(height=15),
                                    login_button,
                                ],
                                spacing=0,
                                width=400,
                            ),
                            padding=ft.padding.symmetric(horizontal=20, vertical=10),
                        ),
                    ],
                    spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor="#ffffff",
                border_radius=10,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color="#cfd8dc",  # Light blue-grey
                    offset=ft.Offset(0, 4),
                ),
                width=480,
            ),
            alignment=ft.alignment.center,
            expand=True,
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=["#e8eaf6", "#c5cae9"],
            ),
        )
