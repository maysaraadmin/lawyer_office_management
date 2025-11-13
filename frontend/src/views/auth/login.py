import flet as ft
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Import from the services package
from services.storage import Storage
from services import auth_service

async def main(page: ft.Page):
    page.title = "Login"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Initialize controls
    email = ft.TextField(
        label="Email",
        hint_text="Enter your email",
        keyboard_type=ft.KeyboardType.EMAIL,
        prefix_icon="email_outlined",
        border_radius=10,
        width=400,
    )
    
    password = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        password=True,
        can_reveal_password=True,
        prefix_icon="lock_outline",
        border_radius=10,
        width=400,
    )
    
    error_text = ft.Text(
        "",
        color="red",
        visible=False,
    )
    
    login_button = ft.ElevatedButton(
        "Login",
        width=400,
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=20,
        ),
    )

    async def login_click(e):
        if not email.value or not password.value:
            error_text.value = "Please fill in all fields"
            error_text.visible = True
            page.update()
            return

        error_text.visible = False
        login_button.disabled = True
        login_button.text = "Logging in..."
        page.update()

        try:
            success, message = await auth_service.login(
                email.value, password.value
            )

            if success:
                # Navigate to dashboard on successful login
                page.go("/dashboard")
            else:
                error_text.value = message or "Invalid email or password"
                error_text.visible = True
                login_button.disabled = False
                login_button.text = "Login"
                page.update()
                
        except Exception as e:
            error_text.value = f"An error occurred: {str(e)}"
            error_text.visible = True
            login_button.disabled = False
            login_button.text = "Login"
            page.update()
    
    # Set the click handler
    login_button.on_click = login_click

    # Clear the page first
    page.clean()
    
    # Build the page
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Welcome Back!",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Please sign in to continue",
                        size=16,
                        color="grey600",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=40),
                    email,
                    ft.Container(height=20),
                    password,
                    ft.Container(height=10),
                    ft.Row(
                        [
                            ft.Checkbox(value=True, fill_color="blue"),
                            ft.Text("Remember me"),
                            ft.Container(expand=True),
                            ft.TextButton("Forgot Password?"),
                        ],
                        width=400,
                    ),
                    error_text,
                    ft.Container(height=20),
                    login_button,
                    ft.Container(height=20),
                    ft.Row(
                        [
                            ft.Text("Don't have an account?"),
                            ft.TextButton("Sign Up"),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
    )

# Run the app
if __name__ == "__main__":
    ft.app(target=main)
