import flet as ft
import asyncio
import httpx
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional, Dict, Any

load_dotenv()

# Color constants matching Django web app
BLUE_600 = "#2563EB"
BLUE_500 = "#3B82F6"
BLUE_50 = "#EFF6FF"
BLUE_100 = "#DBEAFE"
GRAY_900 = "#111827"
GRAY_800 = "#1F2937"
GRAY_700 = "#374151"
GRAY_600 = "#4B5563"
GRAY_500 = "#6B7280"
GRAY_400 = "#9CA3AF"
GRAY_300 = "#D1D5DB"
GRAY_200 = "#E5E7EB"
GRAY_100 = "#F3F4F6"
GRAY_50 = "#F9FAFB"
WHITE = "#FFFFFF"
BLACK = "#000000"
GREEN_600 = "#16A34A"
GREEN_500 = "#22C55E"
GREEN_50 = "#F0FDF4"
YELLOW_600 = "#CA8A04"
YELLOW_500 = "#EAB308"
YELLOW_50 = "#FEFCE8"
RED_600 = "#DC2626"
RED_500 = "#EF4444"
RED_50 = "#FEF2F2"

class ProfileView:
    def __init__(self, page: ft.Page, auth_token: Optional[str] = None):
        self.page = page
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.auth_token = auth_token
        self.user_data: Optional[Dict[str, Any]] = None
        self.loading = False
        self.edit_mode = False
        
        # Form fields
        self.first_name_field = ft.TextField(
            label="First Name",
            read_only=True,
            border_color=GRAY_300,
            focused_border_color=BLUE_500,
        )
        self.last_name_field = ft.TextField(
            label="Last Name",
            read_only=True,
            border_color=GRAY_300,
            focused_border_color=BLUE_500,
        )
        self.email_field = ft.TextField(
            label="Email",
            read_only=True,
            border_color=GRAY_300,
            focused_border_color=BLUE_500,
        )
        self.phone_field = ft.TextField(
            label="Phone",
            read_only=True,
            border_color=GRAY_300,
            focused_border_color=BLUE_500,
        )
        self.address_field = ft.TextField(
            label="Address",
            read_only=True,
            border_color=GRAY_300,
            focused_border_color=BLUE_500,
        )
        
        # Buttons
        self.edit_button = ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.EDIT_OUTLINED, size=16),
                    ft.Text("Edit Profile"),
                ],
                spacing=8,
            ),
            style=ft.ButtonStyle(
                bgcolor=BLUE_600,
                color=WHITE,
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
            ),
            on_click=self._toggle_edit_mode,
        )
        
        self.save_button = ft.ElevatedButton(
            content=ft.Text("Save"),
            style=ft.ButtonStyle(
                bgcolor=GREEN_600,
                color=WHITE,
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
            ),
            visible=False,
            on_click=self._save_profile,
        )
        
        self.cancel_button = ft.OutlinedButton(
            content=ft.Text("Cancel"),
            style=ft.ButtonStyle(
                color=GRAY_700,
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
            ),
            visible=False,
            on_click=self._cancel_edit,
        )
        
        # Logout button
        self.logout_button = ft.OutlinedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.LOGOUT_OUTLINED, size=16),
                    ft.Text("Logout"),
                ],
                spacing=8,
            ),
            style=ft.ButtonStyle(
                color=RED_600,
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
            ),
            on_click=self._handle_logout,
        )
        
        # Loading indicator
        self.loading_indicator = ft.ProgressRing(
            visible=False,
            color=BLUE_600,
        )
        
        # Error message
        self.error_message = ft.Container(
            content=ft.Text(
                "",
                color=RED_600,
                size=12,
            ),
            visible=False,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            bgcolor=RED_50,
            border_radius=8,
            margin=ft.margin.only(bottom=16),
        )
        
        # Content container
        self.content = ft.Container()
        
        # Load profile data if token is available
        if self.auth_token:
            asyncio.create_task(self.load_profile())
    
    async def load_profile(self):
        """Load user profile data from API"""
        if not self.auth_token:
            self._show_error("Authentication token not found")
            return
            
        self.loading = True
        self.loading_indicator.visible = True
        self.page.update()
        
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
                    self._show_error("Failed to load profile data")
                    
        except httpx.TimeoutException:
            self._show_error("Connection timeout. Please try again.")
        except httpx.RequestError:
            self._show_error("Network error. Please check your connection.")
        except Exception as e:
            self._show_error("An unexpected error occurred.")
        finally:
            self.loading = False
            self.loading_indicator.visible = False
            self.page.update()
    
    def _update_profile_display(self):
        """Update the profile display with user data"""
        if not self.user_data:
            return
            
        # Update form fields
        self.first_name_field.value = self.user_data.get("first_name", "")
        self.last_name_field.value = self.user_data.get("last_name", "")
        self.email_field.value = self.user_data.get("email", "")
        self.phone_field.value = self.user_data.get("phone", "")
        self.address_field.value = self.user_data.get("address", "")
        
        # Build the profile view
        self.content.content = ft.Column(
            controls=[
                # Header
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.PERSON_OUTLINED,
                                color=BLUE_600,
                                size=32,
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
                            ),
                        ],
                        spacing=16,
                    ),
                    padding=ft.padding.only(bottom=24),
                ),
                
                # Error message
                self.error_message,
                
                # Loading indicator
                ft.Container(
                    content=self.loading_indicator,
                    alignment=ft.alignment.center,
                    padding=ft.padding.all(32),
                    visible=self.loading,
                ),
                
                # Profile form
                ft.Container(
                    content=ft.Column(
                        controls=[
                            # Avatar section
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Container(
                                            content=ft.Icon(
                                                ft.Icons.PERSON,
                                                color=WHITE,
                                                size=48,
                                            ),
                                            width=80,
                                            height=80,
                                            bgcolor=BLUE_600,
                                            border_radius=40,
                                            alignment=ft.alignment.center,
                                        ),
                                        ft.Column(
                                            controls=[
                                                ft.Text(
                                                    f"{self.user_data.get('first_name', '')} {self.user_data.get('last_name', '')}",
                                                    size=18,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=GRAY_900,
                                                ),
                                                ft.Text(
                                                    self.user_data.get("email", ""),
                                                    size=14,
                                                    color=GRAY_500,
                                                ),
                                                ft.Container(
                                                    content=ft.Text(
                                                        self.user_data.get("user_type_display", "User"),
                                                        size=12,
                                                        color=BLUE_600,
                                                        weight=ft.FontWeight.W_500,
                                                    ),
                                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                                    bgcolor=BLUE_50,
                                                    border_radius=4,
                                                ),
                                            ],
                                            spacing=4,
                                        ),
                                    ],
                                    spacing=16,
                                    alignment=ft.MainAxisAlignment.START,
                                ),
                                padding=ft.padding.all(20),
                                bgcolor=WHITE,
                                border_radius=12,
                                border=ft.border.all(1, GRAY_200),
                                margin=ft.margin.only(bottom=24),
                            ),
                            
                            # Personal information
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            "Personal Information",
                                            size=18,
                                            weight=ft.FontWeight.BOLD,
                                            color=GRAY_900,
                                        ),
                                        self.first_name_field,
                                        self.last_name_field,
                                        self.email_field,
                                        self.phone_field,
                                        self.address_field,
                                    ],
                                    spacing=16,
                                ),
                                padding=ft.padding.all(20),
                                bgcolor=WHITE,
                                border_radius=12,
                                border=ft.border.all(1, GRAY_200),
                                margin=ft.margin.only(bottom=24),
                            ),
                            
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
                            
                            # Action buttons
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        self.edit_button,
                                        self.save_button,
                                        self.cancel_button,
                                    ],
                                    spacing=12,
                                ),
                                padding=ft.padding.only(top=24),
                            ),
                            
                            # Logout button
                            ft.Container(
                                content=self.logout_button,
                                padding=ft.padding.only(top=16),
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
            ],
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
        )
        
        self.page.update()
    
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
        self.error_message.content.value = message
        self.error_message.visible = True
        self.page.update()
    
    def build(self):
        """Build the profile view"""
        if not self.content.content:
            # Show loading state if not loaded yet
            return ft.Column(
                controls=[
                    ft.Container(
                        content=self.loading_indicator,
                        alignment=ft.alignment.center,
                        padding=ft.padding.all(32),
                    ),
                ],
                expand=True,
            )
        
        return ft.Column(
            controls=[
                self.content,
            ],
            expand=True,
        )
