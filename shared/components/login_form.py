import flet as ft
from typing import Optional, Callable, Dict, Any
from ..auth import auth_service

class LoginForm:
    """
    A reusable login form component that can be used in both web and mobile apps.
    """
    def __init__(
        self,
        on_success: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        self.on_success = on_success
        self.on_error = on_error
        
        # Form fields
        self.username = ft.TextField(
            label="Username",
            hint_text="Enter your username",
            prefix_icon=ft.icons.PERSON,
            autofocus=True,
            on_submit=self._on_login_click,
        )
        
        self.password = ft.TextField(
            label="Password",
            hint_text="Enter your password",
            prefix_icon="LOCK",
            password=True,
            can_reveal_password=True,
            on_submit=self._on_login_click,
        )
        
        self.login_button = ft.ElevatedButton(
            text="Login",
            icon="LOGIN",
            on_click=self._on_login_click,
            expand=True,
        )
        
        self.error_text = ft.Text(
            "",
            color='#F44336',  # Red
            visible=False,
        )
        
        self.loading = ft.ProgressRing(visible=False)
        self.content = self.build()

    async def _on_login_click(self, e=None):
        await self._login()
        
    async def _login(self):
        """Handle login form submission"""
        # Show loading
        self.loading.visible = True
        self.error_text.visible = False
        if hasattr(self, 'page') and self.page:
            await self.page.update_async()
        
        try:
            # Call the authentication service
            result = await auth_service.login(
                self.username.value,
                self.password.value
            )
            
            # Hide loading
            self.loading.visible = False
            if hasattr(self, 'page') and self.page:
                await self.page.update_async()
            
            # Clear form
            self.username.value = ""
            self.password.value = ""
            
            # Call success callback if provided
            if self.on_success:
                if hasattr(self.on_success, '__await__'):
                    await self.on_success(result)
                else:
                    self.on_success(result)
                
        except Exception as e:
            # Show error
            self.loading.visible = False
            self.error_text.value = str(e)
            self.error_text.visible = True
            if hasattr(self, 'page') and self.page:
                await self.page.update_async()
            
            # Call error callback if provided
            if self.on_error:
                if hasattr(self.on_error, '__await__'):
                    await self.on_error(str(e))
                else:
                    self.on_error(str(e))
    
    def build(self):
        """Build the login form UI"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Welcome Back!",
                        size=20,
                        weight="bold",
                    ),
                    ft.Text("Please sign in to continue", style=ft.TextThemeStyle.BODY_MEDIUM),
                    ft.Divider(),
                    self.username,
                    self.password,
                    self.error_text,
                    ft.Row(
                        [self.loading, self.login_button],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
            width=400,
        )
