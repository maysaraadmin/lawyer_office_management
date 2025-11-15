import flet as ft
from typing import Optional, Dict, Any
import asyncio
import httpx
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Color constants matching Django web app
BLUE_600 = "#2563EB"
BLUE_500 = "#3B82F6"
BLUE_50 = "#EFF6FF"
BLUE_100 = "#DBEAFE"
GRAY_900 = "#111827"
GRAY_700 = "#374151"
GRAY_500 = "#6B7280"
GRAY_400 = "#9CA3AF"
GRAY_300 = "#D1D5DB"
GRAY_200 = "#E5E7EB"
GRAY_100 = "#F3F4F6"
GRAY_50 = "#F9FAFB"
WHITE = "#FFFFFF"
GREEN_600 = "#059669"
RED_600 = "#DC2626"

class ProfileView:
    def __init__(self, page: ft.Page, auth_token: Optional[str] = None):
        self.page = page
        self.auth_token = auth_token
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.user_data: Dict[str, Any] = {}
        self.loading = True
        
        # Edit mode
        self.edit_mode = False
        self.edit_button = ft.ElevatedButton(
            "Edit Profile",
            icon=ft.Icons.EDIT_OUTLINED,
            bgcolor=BLUE_600,
            color=WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
            ),
            on_click=self._toggle_edit_mode,
        )
        
        # Save/Cancel buttons (hidden by default)
        self.save_button = ft.ElevatedButton(
            "Save",
            icon=ft.Icons.SAVE,
            bgcolor=GREEN_600,
            color=WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
            ),
            on_click=self._save_profile,
            visible=False,
        )
        
        self.cancel_button = ft.ElevatedButton(
            "Cancel",
            icon=ft.Icons.CANCEL_OUTLINED,
            bgcolor=GRAY_300,
            color=GRAY_700,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
            ),
            on_click=self._cancel_edit,
            visible=False,
        )
        
        # Logout button
        self.logout_button = ft.ElevatedButton(
            "Logout",
            icon=ft.Icons.LOGOUT,
            bgcolor=RED_600,
            color=WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
            ),
            on_click=self._handle_logout,
        )
        
        # Profile fields
        self.first_name_field = ft.TextField(
            label="First Name",
            border_radius=6,
            border=ft.border.all(1, GRAY_300),
            focused_border_color=BLUE_600,
            read_only=True,
        )
        
        self.last_name_field = ft.TextField(
            label="Last Name",
            border_radius=6,
            border=ft.border.all(1, GRAY_300),
            focused_border_color=BLUE_600,
            read_only=True,
        )
        
        self.email_field = ft.TextField(
            label="Email Address",
            prefix_icon=ft.Icons.EMAIL_OUTLINED,
            border_radius=6,
            border=ft.border.all(1, GRAY_300),
            focused_border_color=BLUE_600,
            read_only=True,
        )
        
        self.phone_field = ft.TextField(
            label="Phone Number",
            prefix_icon=ft.Icons.PHONE_OUTLINED,
            border_radius=6,
            border=ft.border.all(1, GRAY_300),
            focused_border_color=BLUE_600,
            read_only=True,
        )
        
        self.address_field = ft.TextField(
            label="Address",
            prefix_icon=ft.Icons.HOME_OUTLINED,
            border_radius=6,
            border=ft.border.all(1, GRAY_300),
            focused_border_color=BLUE_600,
            read_only=True,
        )
        
        # Loading indicator
        self.loading_indicator = ft.Column(
            controls=[
                ft.ProgressRing(
                    color=BLUE_600,
                    width=40,
                    height=40,
                ),
                ft.Text(
                    "Loading profile...",
                    color=GRAY_500,
                    size=14,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            visible=True,
        )
        
        # Profile content
        self.profile_content = ft.Column(
            controls=[],
            visible=False,
        )
    
    def build(self) -> ft.Container:
        """Build the profile view"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Header
                    self._build_header(),
                    
                    # Loading indicator
                    self.loading_indicator,
                    
                    # Profile content
                    self.profile_content,
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=0,
                expand=True,
            ),
            bgcolor=GRAY_50,
            expand=True,
        )
    
    def _build_header(self) -> ft.Container:
        """Build profile header"""
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color=GRAY_700,
                        on_click=lambda _: self.page.go("/dashboard"),
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Profile",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=GRAY_900,
                            ),
                            ft.Text(
                                "Manage your personal information",
                                size=14,
                                color=GRAY_500,
                            ),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.all(16),
            bgcolor=WHITE,
        )
    
    async def load_profile(self) -> None:
        """Load user profile data"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/api/auth/profile/",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    self.user_data = response.json()
                    self._update_profile_display()
                else:
                    self._show_error("Failed to load profile")
                    
        except Exception as e:
            self._show_error("Network error")
        finally:
            self.loading = False
            self.loading_indicator.visible = False
            self.profile_content.visible = True
            self.page.update()
    
    def _update_profile_display(self) -> None:
        """Update profile display with user data"""
        # Update field values
        self.first_name_field.value = self.user_data.get("first_name", "")
        self.last_name_field.value = self.user_data.get("last_name", "")
        self.email_field.value = self.user_data.get("email", "")
        self.phone_field.value = self.user_data.get("phone", "")
        self.address_field.value = self.user_data.get("address", "")
        
        # Build profile content
        self.profile_content.controls = [
            # Profile card
            ft.Container(
                content=ft.Column(
                    controls=[
                        # User avatar and basic info
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                ft.Container(
                                                    content=ft.Icon(
                                                        ft.Icons.PERSON_OUTLINED,
                                                        size=48,
                                                        color=WHITE,
                                                    ),
                                                    width=80,
                                                    height=80,
                                                    bgcolor=BLUE_600,
                                                    border_radius=40,
                                                    alignment=ft.alignment.center,
                                                ),
                                                ft.Text(
                                                    f"{self.user_data.get('first_name', '')} {self.user_data.get('last_name', '')}".strip() or "User",
                                                    size=18,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=GRAY_900,
                                                ),
                                                ft.Text(
                                                    self.user_data.get("email", ""),
                                                    size=14,
                                                    color=GRAY_500,
                                                ),
                                            ],
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=8,
                                        ),
                                        expand=True,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            padding=ft.padding.all(20),
                        ),
                        
                        # Action buttons
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    self.edit_button,
                                    self.save_button,
                                    self.cancel_button,
                                    ft.Container(expand=True),
                                    self.logout_button,
                                ],
                                spacing=8,
                            ),
                            padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        ),
                    ],
                    spacing=0,
                ),
                margin=ft.margin.all(16),
                bgcolor=WHITE,
                border_radius=12,
                border=ft.border.all(1, GRAY_200),
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=4,
                    color="#00000010",
                    offset=ft.Offset(0, 1),
                ),
            ),
            
            # Profile details
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Personal Information",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=GRAY_900,
                        ),
                        
                        # Form fields
                        self.first_name_field,
                        self.last_name_field,
                        self.email_field,
                        self.phone_field,
                        self.address_field,
                        
                        # Account information
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "Account Information",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=GRAY_900,
                                    ),
                                    self._build_info_row(
                                        "User Type",
                                        self.user_data.get("user_type_display", "N/A"),
                                        ft.Icons.PERSON_OUTLINED,
                                    ),
                                    self._build_info_row(
                                        "Account Created",
                                        self._format_date(self.user_data.get("date_joined")),
                                        ft.Icons.CALENDAR_TODAY_OUTLINED,
                                    ),
                                    self._build_info_row(
                                        "Last Login",
                                        self._format_date(self.user_data.get("last_login")),
                                        ft.Icons.ACCESS_TIME_OUTLINED,
                                    ),
                                ],
                                spacing=16,
                            ),
                            padding=ft.padding.only(top=24),
                        ),
                    ],
                    spacing=16,
                ),
                padding=ft.padding.all(20),
                margin=ft.margin.symmetric(horizontal=16, vertical=8),
                bgcolor=WHITE,
                border_radius=12,
                border=ft.border.all(1, GRAY_200),
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=4,
                    color="#00000010",
                    offset=ft.Offset(0, 1),
                ),
            ),
        ]
    
    def _build_info_row(self, label: str, value: str, icon: str) -> ft.Container:
        """Build an information row"""
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        icon,
                        color=GRAY_400,
                        size=20,
                    ),
                    ft.Container(
                        content=ft.Text(
                            label,
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=GRAY_700,
                        ),
                        width=120,
                    ),
                    ft.Text(
                        value or "Not provided",
                        size=14,
                        color=GRAY_900,
                        expand=True,
                    ),
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=ft.padding.symmetric(vertical=8),
        )
    
    def _format_date(self, date_str: Optional[str]) -> str:
        """Format date string"""
        if not date_str:
            return "Never"
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime("%b %d, %Y %H:%M")
        except:
            return "Invalid date"
    
    def _toggle_edit_mode(self, e: ft.ControlEvent) -> None:
        """Toggle edit mode"""
        self.edit_mode = not self.edit_mode
        
        if self.edit_mode:
            # Enable editing
            self.first_name_field.read_only = False
            self.last_name_field.read_only = False
            self.phone_field.read_only = False
            self.address_field.read_only = False
            self.email_field.read_only = False
            
            # Show save/cancel, hide edit
            self.edit_button.visible = False
            self.save_button.visible = True
            self.cancel_button.visible = True
        else:
            # Disable editing
            self.first_name_field.read_only = True
            self.last_name_field.read_only = True
            self.phone_field.read_only = True
            self.address_field.read_only = True
            self.email_field.read_only = True
            
            # Show edit, hide save/cancel
            self.edit_button.visible = True
            self.save_button.visible = False
            self.cancel_button.visible = False
        
        self.page.update()
    
    def _cancel_edit(self, e: ft.ControlEvent) -> None:
        """Cancel editing and restore original values"""
        self._toggle_edit_mode(e)
        self._update_profile_display()
        self.page.update()
    
    async def _save_profile(self, e: ft.ControlEvent) -> None:
        """Save profile changes"""
        # Show loading state
        self.save_button.disabled = True
        self.save_button.content = ft.Row(
            controls=[
                ft.ProgressRing(
                    width=16,
                    height=16,
                    color=WHITE,
                ),
                ft.Text("Saving..."),
            ],
            spacing=8,
        )
        self.page.update()
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            data = {
                "first_name": self.first_name_field.value,
                "last_name": self.last_name_field.value,
                "phone": self.phone_field.value,
                "address": self.address_field.value,
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.api_base_url}/api/auth/profile/",
                    headers=headers,
                    json=data,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    # Update local data
                    self.user_data.update(response.json())
                    self._toggle_edit_mode(e)
                    self._update_profile_display()
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Profile updated successfully!"),
                        bgcolor=GREEN_600,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                else:
                    self._show_error("Failed to update profile")
                    
        except Exception as e:
            self._show_error("Network error")
        finally:
            # Reset button state
            self.save_button.disabled = False
            self.save_button.content = ft.Text("Save")
            self.page.update()
    
    def _handle_logout(self, e: ft.ControlEvent) -> None:
        """Handle logout"""
        def confirm_logout(dialog_result):
            if dialog_result == "yes":
                # Clear auth and redirect to login
                self.page.client_storage.clear()
                self.page.go("/login")
        
        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Confirm Logout"),
                content=ft.Text("Are you sure you want to logout?"),
                actions=[
                    ft.TextButton(
                        "Cancel",
                        on_click=lambda _: self.page.close_dialog(),
                    ),
                    ft.TextButton(
                        "Logout",
                        style=ft.ButtonStyle(color=RED_600),
                        on_click=lambda _: confirm_logout("yes"),
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        )
    
    def _show_error(self, message: str):
        """Show error message"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=RED_600
        )
        self.page.snack_bar.open = True
        self.page.update()
