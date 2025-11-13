import flet as ft
import flet_core
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Import from the services package
from services import auth_service, api_client
from services.storage import Storage

# Import navigation utility
from ...utils.navigation import navigate_to

class ProfileView(flet_core.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.user_data = None
        self.loading = True
        self.error = None

    async def did_mount_async(self):
        await self.load_user_data()

    async def load_user_data(self):
        try:
            # Get current user data
            response = await api_client.get("/auth/me/")
            if response.status_code == 200:
                self.user_data = response.json()
                self.loading = False
                await self.update_async()
            else:
                self.error = "Failed to load profile data"
                self.loading = False
                await self.update_async()
        except Exception as e:
            self.error = str(e)
            self.loading = False
            await self.update_async()

    async def logout(self, e):
        await auth_service.logout()
        Storage.remove("access_token")
        Storage.remove("refresh_token")
        await navigate_to(self.page, "/login")

    def build(self):
        if self.loading:
            return ft.Container(
                content=ft.ProgressRing(),
                alignment=ft.alignment.center,
                expand=True,
            )

        if self.error:
            return ft.Container(
                content=ft.Text(f"Error: {self.error}", color=ft.colors.RED),
                alignment=ft.alignment.center,
                expand=True,
            )

        if not self.user_data:
            return ft.Container(
                content=ft.Text("User data not available"),
                alignment=ft.alignment.center,
                expand=True,
            )

        # Format date of birth if available
        dob = ""
        if self.user_data.get("date_of_birth"):
            try:
                dob_obj = datetime.strptime(self.user_data["date_of_birth"], "%Y-%m-%d")
                dob = dob_obj.strftime("%B %d, %Y")
            except:
                dob = self.user_data.get("date_of_birth", "")

        return ft.Container(
            content=ft.Column(
                [
                    # Header
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.icons.ARROW_BACK,
                                on_click=lambda _: self.page.go("/"),
                            ),
                            ft.Text(
                                "My Profile",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                on_click=lambda _: self.page.go("/profile/edit"),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(),
                    
                    # Profile Picture and Basic Info
                    ft.Row(
                        [
                            ft.CircleAvatar(
                                radius=50,
                                background_image=self.user_data.get("profile_picture"),
                                content=ft.Icon(ft.icons.PERSON, size=40)
                                if not self.user_data.get("profile_picture")
                                else None,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        f"{self.user_data.get('first_name', '')} {self.user_data.get('last_name', '')}",
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        self.user_data.get("email", ""),
                                        color=ft.colors.GREY_600,
                                    ),
                                    ft.Text(
                                        self.user_data.get("user_type", "").capitalize(),
                                        color=ft.colors.BLUE_600,
                                    ),
                                ],
                                spacing=5,
                            ),
                        ],
                        spacing=20,
                    ),
                    
                    # User Details
                    ft.Container(height=20),
                    ft.Text("Personal Information", weight=ft.FontWeight.BOLD, size=16),
                    ft.Divider(),
                    
                    # Email
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.EMAIL),
                        title=ft.Text("Email"),
                        subtitle=ft.Text(self.user_data.get("email", "")),
                    ),
                    
                    # Phone
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.PHONE),
                        title=ft.Text("Phone"),
                        subtitle=ft.Text(self.user_data.get("phone") or "Not provided"),
                    ),
                    
                    # Date of Birth
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.CALENDAR_TODAY),
                        title=ft.Text("Date of Birth"),
                        subtitle=ft.Text(dob or "Not provided"),
                    ),
                    
                    # Address
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.HOME),
                        title=ft.Text("Address"),
                        subtitle=ft.Text(self.user_data.get("address") or "Not provided"),
                    ),
                    
                    # Logout Button
                    ft.Container(height=40),
                    ft.ElevatedButton(
                        "Logout",
                        on_click=self.logout,
                        icon=ft.icons.LOGOUT,
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.RED,
                            color=ft.colors.WHITE,
                        ),
                        width=200,
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=20,
            expand=True,
        )
