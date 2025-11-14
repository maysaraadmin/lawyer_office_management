import flet as ft
import flet_core
import sys
import os
import logging
from datetime import datetime
from src.services.api_client import api_client

logger = logging.getLogger(__name__)

# Color constants
WHITE = "#FFFFFF"
GREY_50 = "#FAFAFA"
GREY_100 = "#F5F5F5"
GREY_200 = "#EEEEEE"
GREY_300 = "#E0E0E0"
GREY_400 = "#BDBDBD"
GREY_500 = "#9E9E9E"
GREY_600 = "#757575"
GREY_700 = "#616161"
GREY_800 = "#424242"
GREY_900 = "#212121"
BLUE = "#2196F3"
GREEN = "#4CAF50"
ORANGE = "#FF9800"
RED = "#F44336"

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Import from the services package
from src.services.storage import Storage

class ProfileView(flet_core.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.user_data = None
        self.loading = True
        self.error = None

    async def did_mount_async(self):
        print("DEBUG: did_mount_async called")
        await self.load_user_data()

    async def load_user_data(self):
        """Load user data from API"""
        try:
            print("DEBUG: Starting to load user data...")
            # Try to get user data from API
            user_data = await api_client.get_current_user()
            
            if user_data:
                self.user_data = user_data
                print(f"DEBUG: User data loaded from API: {user_data}")
            else:
                # Fallback to mock data if API returns nothing
                print("DEBUG: API returned no data, using mock data")
                self.user_data = {
                    "id": 1,
                    "email": "lawyer@example.com",
                    "first_name": "John",
                    "last_name": "Smith",
                    "phone": "+1-555-0123",
                    "date_of_birth": "1980-01-01",
                    "address": "123 Main St, City, State 12345",
                    "user_type": "lawyer"
                }
            
            self.loading = False
            print("DEBUG: User data loaded successfully")
            self.update()
            
        except Exception as e:
            print(f"DEBUG: Error loading user data from API: {str(e)}")
            # Use mock data as fallback
            self.user_data = {
                "id": 1,
                "email": "lawyer@example.com",
                "first_name": "John",
                "last_name": "Smith",
                "phone": "+1-555-0123",
                "date_of_birth": "1980-01-01",
                "address": "123 Main St, City, State 12345",
                "user_type": "lawyer"
            }
            self.loading = False
            print("DEBUG: Using mock user data as fallback")
            self.update()

    async def logout(self, e):
        from src.services.storage import Storage
        storage = Storage()
        storage.remove("access_token")
        storage.remove("refresh_token")
        self.page.go("/login")

    def build(self):
        if self.loading:
            return ft.Container(
                content=ft.ProgressRing(),
                alignment=ft.alignment.center,
                expand=True,
            )

        if self.error:
            return ft.Container(
                content=ft.Text(f"Error: {self.error}", color="#F44336"),
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
                                icon="arrow_back",
                                on_click=lambda _: self.page.go("/dashboard"),
                            ),
                            ft.Text(
                                "My Profile",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon="edit",
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
                                content=ft.Icon("person", size=40)
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
                                        color="#757575",
                                    ),
                                    ft.Text(
                                        self.user_data.get("user_type", "").capitalize(),
                                        color="#2196F3",
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
                        leading=ft.Icon("email"),
                        title=ft.Text("Email"),
                        subtitle=ft.Text(self.user_data.get("email", "")),
                    ),
                    
                    # Phone
                    ft.ListTile(
                        leading=ft.Icon("phone"),
                        title=ft.Text("Phone"),
                        subtitle=ft.Text(self.user_data.get("phone") or "Not provided"),
                    ),
                    
                    # Date of Birth
                    ft.ListTile(
                        leading=ft.Icon("calendar_today"),
                        title=ft.Text("Date of Birth"),
                        subtitle=ft.Text(dob or "Not provided"),
                    ),
                    
                    # Address
                    ft.ListTile(
                        leading=ft.Icon("home"),
                        title=ft.Text("Address"),
                        subtitle=ft.Text(self.user_data.get("address") or "Not provided"),
                    ),
                    
                    # Logout Button
                    ft.Container(height=40),
                    ft.ElevatedButton(
                        "Logout",
                        on_click=self.logout,
                        icon="logout",
                        style=ft.ButtonStyle(
                            bgcolor="#F44336",
                            color="#FFFFFF",
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
