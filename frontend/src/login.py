import flet as ft
from flet_core import UserControl
from typing import Callable, Awaitable
import logging

logger = logging.getLogger(__name__)

# Color constants
PRIMARY_COLOR = "#1976d2"
BACKGROUND_COLOR = "#f5f5f5"
TEXT_COLOR = "#000000"
GREY_600 = "#757575"
WHITE = "#ffffff"

class LoginError(Exception):
    """Custom exception for login errors"""
    pass

class LoginForm(UserControl):
    """Login form component"""
    
    def __init__(self, on_login_success: Callable[[], Awaitable[None]], page: ft.Page = None):
        super().__init__()
        self.on_login_success = on_login_success
        self.page = page
        self.error_message = ""
        
        # Form fields
        self.username = ft.TextField(
            label="Email",
            hint_text="Enter your email",
            width=400,
            border_radius=5,
            border_color="#e0e0e0",
            bgcolor=WHITE,
            text_size=14,
        )
        
        self.password = ft.TextField(
            label="Password",
            hint_text="Enter your password",
            width=400,
            password=True,
            can_reveal_password=True,
            border_radius=5,
            border_color="#e0e0e0",
            bgcolor=WHITE,
            text_size=14,
        )
        
        self.error_text = ft.Text(
            "", 
            color="red",
            size=12,
            weight=ft.FontWeight.W_400,
        )
        
    async def validate_credentials(self, username: str, password: str) -> bool:
        """Validate user credentials with API"""
        if not username or not password:
            raise LoginError("Email and password are required")
        
        try:
            from src.services.api_client import api_client
            
            # Call the API login endpoint
            response = await api_client.login(username, password)
            
            if response and "access" in response:
                # Store the token
                api_client.set_auth_token(response["access"])
                
                # Store in app's storage
                if hasattr(self.app, 'storage'):
                    self.app.storage.set("access_token", response["access"])
                    self.app.storage.set("refresh_token", response.get("refresh", ""))
                
                # Set app's access token
                self.app.access_token = response["access"]
                
                return True
            else:
                raise LoginError("Invalid credentials")
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            if "401" in str(e) or "Unauthorized" in str(e):
                raise LoginError("Invalid email or password")
            elif "400" in str(e):
                raise LoginError("Invalid request format")
            elif "500" in str(e):
                raise LoginError("Server error. Please try again later.")
            else:
                raise LoginError(f"Login failed: {str(e)}")
    
    async def login_click(self, e):
        """Handle login button click"""
        try:
            if not self.username.value or not self.password.value:
                raise LoginError("Please fill in all fields")
                
            # Validate credentials
            is_valid = await self.validate_credentials(
                self.username.value.strip(),
                self.password.value
            )
            
            if is_valid:
                self.error_text.value = ""
                await self.update_async()
                await self.on_login_success()
                
        except LoginError as e:
            self.error_text.value = str(e)
            await self.update_async()
        except Exception as e:
            self.error_text.value = "An unexpected error occurred"
            print(f"Login error: {str(e)}")
            await self.update_async()
    
    def build(self):
        try:
            print("Building login form...")
            
            login_button = ft.ElevatedButton(
                "Login",
                on_click=self.login_click,
                width=400,
                height=45,
                color=WHITE,  # White text
                bgcolor=PRIMARY_COLOR,  # Primary color
            )
            print("Login button created")
            
            container = ft.Container(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            "Welcome Back!", 
                                            size=28, 
                                            weight=ft.FontWeight.BOLD, 
                                            color=PRIMARY_COLOR
                                        ),
                                        ft.Text(
                                            "Please sign in to continue", 
                                            color=GREY_600, 
                                            size=14
                                        ),
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
                                padding=20,
                            ),
                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=WHITE,
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
            print("Login form container created")
            return container
        except Exception as e:
            print(f"Error building login form: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return a simple fallback UI
            return ft.Column([
                ft.Text("Login Form Error", color="red"),
                ft.Text(f"Error: {str(e)}", color="red")
            ])
