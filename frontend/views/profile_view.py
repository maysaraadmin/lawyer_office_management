import flet as ft
from typing import Dict, Any, Optional
import asyncio

# Import base view
from .base_view import BaseView

class ProfileView(BaseView):
    """View for user profile and settings"""
    
    def __init__(self, app):
        super().__init__(app)
        self.user_data = {}
        self.is_loading = True
        self.error = None
        self.is_editing = False
    
    async def initialize(self):
        """Initialize the profile data"""
        await self.load_user_data()
    
    async def load_user_data(self):
        """Load user data from the API"""
        self.is_loading = True
        self.error = None
        
        try:
            # Get user data from the API
            response = await self.app.api_client.get('auth/user/')
            self.user_data = response
        except Exception as e:
            logger.error(f"Error loading user data: {str(e)}")
            self.error = str(e)
        finally:
            self.is_loading = False
            await self.page.update_async()
    
    async def save_profile(self, e):
        """Save profile changes"""
        self.is_loading = True
        self.error = None
        await self.page.update_async()
        
        try:
            # Prepare updated data
            updated_data = {
                'first_name': self.first_name_field.value,
                'last_name': self.last_name_field.value,
                'email': self.email_field.value,
                'phone': self.phone_field.value,
            }
            
            # Update user data via API
            await self.app.api_client.patch('auth/user/', data=updated_data)
            
            # Update local user data
            self.user_data.update(updated_data)
            
            # Switch back to view mode
            self.is_editing = False
            
            # Show success message
            await self.show_snackbar("Profile updated successfully", color="#4CAF50")  # Green
            
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            self.error = str(e)
        finally:
            self.is_loading = False
            await self.page.update_async()
    
    def build(self) -> ft.Container:
        """Build the profile view"""
        if self.is_loading and not self.user_data:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.ProgressRing(),
                        ft.Text("Loading profile..."),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
        
        if self.error and not self.user_data:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            "ERROR_OUTLINE",
                            size=48,
                            color="#F44336",  # Red
                        ),
                        ft.Text(
                            "Error loading profile",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="#F44336",  # Red
                        ),
                        ft.Text(
                            self.error,
                            size=14,
                            color="#757575",  # Grey 600
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.ElevatedButton(
                            "Retry",
                            on_click=lambda _: self.initialize(),
                            icon="REFRESH",
                            style=ft.ButtonStyle(
                                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                            ),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=16,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
        
        # Create form fields
        self.first_name_field = ft.TextField(
            label="First Name",
            value=self.user_data.get('first_name', ''),
            disabled=not self.is_editing,
            expand=True,
        )
        
        self.last_name_field = ft.TextField(
            label="Last Name",
            value=self.user_data.get('last_name', ''),
            disabled=not self.is_editing,
            expand=True,
        )
        
        self.email_field = ft.TextField(
            label="Email",
            value=self.user_data.get('email', ''),
            disabled=not self.is_editing,
            keyboard_type=ft.KeyboardType.EMAIL,
        )
        
        self.phone_field = ft.TextField(
            label="Phone",
            value=self.user_data.get('phone', ''),
            disabled=not self.is_editing,
            keyboard_type=ft.KeyboardType.PHONE,
        )
        
        # Create action buttons
        if self.is_editing:
            actions = ft.Row(
                [
                    ft.ElevatedButton(
                        "Save Changes",
                        on_click=self.save_profile,
                        icon="SAVE",
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(horizontal=24, vertical=12),
                        ),
                    ),
                    ft.TextButton(
                        "Cancel",
                        on_click=lambda _: self.toggle_edit_mode(False),
                    ),
                ],
                spacing=8,
            )
        else:
            actions = ft.Row(
                [
                    ft.ElevatedButton(
                        "Edit Profile",
                        on_click=lambda _: self.toggle_edit_mode(True),
                        icon="EDIT",
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(horizontal=24, vertical=12),
                        ),
                    ),
                    ft.ElevatedButton(
                        "Change Password",
                        on_click=self.change_password,
                        icon="LOCK",
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(horizontal=24, vertical=12),
                        ),
                    ),
                ],
                spacing=8,
            )
        
        # Build the profile form
        profile_form = ft.Container(
            content=ft.Column(
                [
                    # Profile header
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon(
                                        "ACCOUNT_CIRCLE",
                                        size=80,
                                        color="#757575",  # Grey 600
                                    ),
                                    padding=8,
                                    border_radius=50,
                                    border=ft.border.all(2, "#E0E0E0"),  # Grey 300
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            f"{self.user_data.get('first_name', '')} {self.user_data.get('last_name', '')}".strip() or "User",
                                            size=24,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            self.user_data.get('email', ''),
                                            size=14,
                                            color="#757575",  # Grey 600
                                        ),
                                        ft.Text(
                                            f"Member since {self.user_data.get('date_joined', '').split('T')[0] if self.user_data.get('date_joined') else 'N/A'}",
                                            size=12,
                                            color="#9E9E9E",  # Grey 500
                                        ),
                                    ],
                                    spacing=4,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                            ],
                            spacing=24,
                        ),
                        padding=ft.padding.only(bottom=32),
                    ),
                    
                    # Profile form
                    ft.Text("Personal Information", size=16, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    
                    # Name fields
                    ft.Row(
                        [
                            self.first_name_field,
                            self.last_name_field,
                        ],
                        spacing=16,
                    ),
                    
                    # Contact information
                    self.email_field,
                    self.phone_field,
                    
                    # Actions
                    ft.Container(
                        content=actions,
                        padding=ft.padding.only(top=16),
                    ),
                    
                    # Error message
                    ft.Text(
                        self.error or "",
                        color="#F44336",  # Red
                        visible=bool(self.error),
                    ),
                    
                    # Loading indicator
                    ft.Container(
                        content=ft.ProgressRing(),
                        visible=self.is_loading,
                        alignment=ft.alignment.center,
                        padding=ft.padding.only(top=16),
                    ),
                ],
                spacing=16,
                expand=True,
            ),
            padding=24,
            bgcolor=ft.colors.WHITE,
            border_radius=8,
            border=ft.border.all(1, "#E0E0E0"),  # Grey 300
        )
        
        return ft.Container(
            content=ft.Column(
                [
                    # Page header
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(
                                    "My Profile",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.padding.only(bottom=24),
                    ),
                    
                    # Main content
                    ft.Row(
                        [
                            # Left column - Profile form
                            ft.Container(
                                content=profile_form,
                                expand=3,
                            ),
                            
                            # Right column - Additional settings
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("Preferences", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Divider(),
                                        
                                        # Theme preference
                                        ft.ListTile(
                                            leading=ft.Icon("BRIGHTNESS_4"),
                                            title=ft.Text("Theme"),
                                            subtitle=ft.Text("System default"),
                                            trailing=ft.PopupMenuButton(
                                                icon=ft.Icon("ARROW_DROP_DOWN"),
                                                items=[
                                                    ft.PopupMenuItem(
                                                        text="Light",
                                                        on_click=lambda _: self.change_theme("light"),
                                                    ),
                                                    ft.PopupMenuItem(
                                                        text="Dark",
                                                        on_click=lambda _: self.change_theme("dark"),
                                                    ),
                                                    ft.PopupMenuItem(
                                                        text="System",
                                                        on_click=lambda _: self.change_theme("system"),
                                                    ),
                                                ],
                                            ),
                                        ),
                                        
                                        # Notifications
                                        ft.ListTile(
                                            leading=ft.Icon("NOTIFICATIONS"),
                                            title=ft.Text("Notifications"),
                                            subtitle=ft.Text("Manage email and push notifications"),
                                            trailing=ft.Icon("CHEVRON_RIGHT"),
                                            on_click=lambda _: self.go_to("/settings/notifications"),
                                        ),
                                        
                                        # Security
                                        ft.ListTile(
                                            leading=ft.Icon("SECURITY"),
                                            title=ft.Text("Security"),
                                            subtitle=ft.Text("Two-factor authentication and more"),
                                            trailing=ft.Icon("CHEVRON_RIGHT"),
                                            on_click=lambda _: self.go_to("/settings/security"),
                                        ),
                                        
                                        # Divider
                                        ft.Divider(),
                                        
                                        # Danger zone
                                        ft.Text("Danger Zone", size=14, weight=ft.FontWeight.BOLD, color="#F44336"),
                                        
                                        # Delete account
                                        ft.ListTile(
                                            leading=ft.Icon("DELETE", color="#F44336"),
                                            title=ft.Text("Delete Account", color="#F44336"),
                                            subtitle=ft.Text("Permanently delete your account and all data"),
                                            on_click=self.confirm_delete_account,
                                        ),
                                    ],
                                    spacing=8,
                                    alignment=ft.MainAxisAlignment.START,
                                ),
                                padding=24,
                                bgcolor=ft.colors.WHITE,
                                border_radius=8,
                                border=ft.border.all(1, "#E0E0E0"),  # Grey 300
                                expand=1,
                                margin=ft.margin.only(left=16),
                            ),
                        ],
                        spacing=0,
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            padding=16,
            expand=True,
        )
    
    async def toggle_edit_mode(self, is_editing: bool):
        """Toggle between edit and view modes"""
        self.is_editing = is_editing
        
        # Update field states
        self.first_name_field.disabled = not is_editing
        self.last_name_field.disabled = not is_editing
        self.email_field.disabled = not is_editing
        self.phone_field.disabled = not is_editing
        
        # If canceling edit, reset fields to original values
        if not is_editing:
            self.first_name_field.value = self.user_data.get('first_name', '')
            self.last_name_field.value = self.user_data.get('last_name', '')
            self.email_field.value = self.user_data.get('email', '')
            self.phone_field.value = self.user_data.get('phone', '')
            self.error = None
        
        await self.page.update_async()
    
    async def change_password(self, e):
        """Navigate to change password view"""
        await self.go_to("/change-password")
    
    async def change_theme(self, theme: str):
        """Change the application theme"""
        # In a real app, we would save this preference and apply the theme
        await self.show_snackbar(f"Theme changed to {theme.capitalize()}")
    
    async def confirm_delete_account(self, e):
        """Show confirmation dialog for account deletion"""
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Delete Account"),
            content=ft.Text(
                "Are you sure you want to delete your account? This action cannot be undone. "
                "All your data will be permanently removed from our servers."
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton(
                    "Delete Account",
                    on_click=self.delete_account,
                    style=ft.ButtonStyle(
                        color="#F44336",  # Red
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        await self.page.update_async()
    
    async def delete_account(self, e):
        """Delete the user's account"""
        self.page.dialog.open = False
        self.is_loading = True
        await self.page.update_async()
        
        try:
            # In a real app, we would call the API to delete the account
            await asyncio.sleep(1)  # Simulate API call
            
            # Show success message and log out
            await self.show_snackbar("Your account has been deleted successfully", color="#4CAF50")
            await self.go_to("/logout")
            
        except Exception as e:
            logger.error(f"Error deleting account: {str(e)}")
            self.error = "Failed to delete account. Please try again."
            self.is_loading = False
            await self.page.update_async()
