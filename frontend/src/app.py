import flet as ft
import sys
import os
import asyncio
import logging
import traceback
import httpx
from pathlib import Path
from typing import Optional, Dict, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import views
try:
    from .views.dashboard import DashboardView
    from .views.appointments import AppointmentsView
    from .views.clients import ClientsView
    from .views.profile import ProfileView
    from .login import LoginForm, LoginError
    from src.services.storage import Storage
    from src.services.api_client import api_client
except ImportError as e:
    logger.error(f"Import error: {str(e)}")
    raise

async def safe_page_update(page: ft.Page) -> None:
    """Safely update the page, handling both sync and async update methods."""
    if page is None:
        logger.warning("Attempted to update None page")
        return
    
    # Check if page has been destroyed or is in an invalid state
    if hasattr(page, '_disposed') and page._disposed:
        logger.warning("Attempted to update disposed page")
        return
    
    try:
        # Check if page is still valid before updating
        if hasattr(page, 'window') and page.window is None:
            logger.warning("Attempted to update page with None window")
            return
        
        page.update()
    except Exception as e:
        logger.error(f"Error updating page: {str(e)}")
        try:
            if hasattr(page, 'update_async'):
                await page.update_async()
            else:
                page.update()
        except Exception as e2:
            logger.error(f"Secondary error updating page: {str(e2)}")

class LawyerOfficeApp:
    def __init__(self, page: ft.Page):
        logger.info(f"LawyerOfficeApp.__init__ called with page: {page}")
        self.page = page
        if self.page is None:
            logger.error("Page is None in LawyerOfficeApp.__init__")
            return
        
        logger.info(f"Setting page properties for page id: {id(self.page)}")
        self.page.title = "Lawyer Office Management"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.window_width = 1280
        self.page.window_height = 800
        self.page.window_resizable = True
        
        # Define colors
        self.primary_color = "#1976d2"
        self.background_color = "#f5f5f5"
        self.text_color = "#000000"
        
        # Initialize authentication state
        self.api_base_url = "http://127.0.0.1:8000"
        self.storage = Storage()
        self.is_authenticated = False
        self.access_token = None
        self.user_data: Dict[str, Any] = {}
        
        # Check for existing authentication
        stored_token = self.storage.get("access_token")
        logger.info(f"Stored token found: {stored_token is not None}")
        logger.info(f"Stored token value: {stored_token}")
        if stored_token:
            self.is_authenticated = True
            self.access_token = stored_token
            logger.info("Restored authentication state from storage")
            logger.info(f"Authentication state: {self.is_authenticated}")
            
            # Restore the API client token
            api_client.set_auth_token(self.access_token)
        else:
            logger.info("No stored token found")
            # Try to set and get a test value to verify storage is working
            self.storage.set("test_key", "test_value")
            test_value = self.storage.get("test_key")
            logger.info(f"Storage test - set: test_value, got: {test_value}")
        
        logger.info("App initialized")
        
        # Initialize views
        self.dashboard_view_instance = DashboardView(self)
        self.dashboard_view = self.dashboard_view_instance.build()
        self.appointments_view = AppointmentsView(self).build()
        self.clients_view = ClientsView(self).build()
        self.profile_view = ProfileView(self.page, None).build()  # Initialize with None, will be updated after login
        
        # Set up navigation
        self.nav_items = [
            ft.NavigationRailDestination(
                icon="dashboard_outlined",
                selected_icon="dashboard",
                label="Dashboard"
            ),
            ft.NavigationRailDestination(
                icon="event_note",
                selected_icon="event_available",
                label="Appointments"
            ),
            ft.NavigationRailDestination(
                icon="people_outline",
                selected_icon="people",
                label="Clients"
            ),
            ft.NavigationRailDestination(
                icon="person_outline",
                selected_icon="person",
                label="Profile"
            ),
        ]
        
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            expand=True,
            on_change=self.navigate,
            destinations=self.nav_items
        )
        
        # Main content area
        self.content = ft.Container(
            expand=True,
            padding=20
        )
        
        # Main layout
        self.main = ft.Row(
            [
                self.nav_rail,
                ft.VerticalDivider(width=1),
                self.content,
            ],
            expand=True,
        )
        
        # Set initial view based on authentication
        logger.info("=== INIT START ===")
        logger.info(f"Is authenticated: {self.is_authenticated}")
        logger.info(f"Has dashboard_view: {hasattr(self, 'dashboard_view')}")
        logger.info(f"Has main: {hasattr(self, 'main')}")
        logger.info(f"Has content: {hasattr(self, 'content')}")
        
        if self.is_authenticated:
            self.content.content = self.dashboard_view
            # Restore full main layout with navigation rail
            self.main.controls = [self.nav_rail, ft.VerticalDivider(width=1), self.content]
            logger.info("Initial: Set dashboard view for authenticated user")
        else:
            # For unauthenticated users, show empty content initially
            # Login will be shown via route_change
            self.content.content = ft.Container()
            logger.info("Initial: Set empty container for unauthenticated user")
        
        # Always add the main layout
        logger.info(f"Adding main layout to page (has {len(self.main.controls)} controls)")
        # Clear any existing controls first
        self.page.clean()
        self.page.add(self.main)
        logger.info(f"Page now has {len(self.page.controls)} controls after adding main")
        try:
            self.page.update()
            logger.info("Page updated successfully after init")
        except Exception as e:
            logger.error(f"Error updating page: {str(e)}")
            logger.error(traceback.format_exc())
        
        # Initialize login
        self.login_form = None
        logger.info("=== INIT END ===")
    
    async def navigate(self, e):
        try:
            index = e.control.selected_index
            if index == 0:
                # Use the pre-initialized dashboard view
                self.content.content = self.dashboard_view
                self.content.bgcolor = ft.Colors.GREY_50  # Set visible background
                # Reset dashboard data loading state
                if hasattr(self.dashboard_view_instance, 'data_loaded'):
                    self.dashboard_view_instance.data_loaded = False
                    self.dashboard_view_instance.loading = False
                    logger.info("Reset dashboard data_loaded flag for fresh load")
                self.page.route = "/dashboard"
            elif index == 1:
                appointments_instance = AppointmentsView(self)
                self.content.content = appointments_instance.build()
                # Call did_mount_async to load data
                if hasattr(appointments_instance, 'did_mount_async'):
                    try:
                        await appointments_instance.did_mount_async()
                    except Exception as ex:
                        logger.warning(f"Appointments did_mount_async failed: {str(ex)}")
                self.page.route = "/appointments"
            elif index == 2:
                clients_instance = ClientsView(self)
                self.content.content = clients_instance.build()
                # Call did_mount_async to load data
                if hasattr(clients_instance, 'did_mount_async'):
                    try:
                        await clients_instance.did_mount_async()
                    except Exception as ex:
                        logger.warning(f"Clients did_mount_async failed: {str(ex)}")
                self.page.route = "/clients"
            elif index == 3:
                profile_instance = ProfileView(self.page, self.auth_token if hasattr(self, 'auth_token') else None)
                self.content.content = profile_instance.build()
                self.page.route = "/profile"
            
            # Update the page
            await safe_page_update(self.page)
            
        except Exception as e:
            logger.error(f"Navigation error: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Show error to user
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Error navigating. Please try again.")
            )
            self.page.snack_bar.open = True
            
            # Try to update the page to show the error
            try:
                await safe_page_update(self.page)
            except Exception as update_error:
                logger.error(f"Error showing error message: {str(update_error)}")
                # Last resort - try direct update
                try:
                    self.page.update()
                except Exception as e:
                    logger.error(f"Error updating page: {str(e)}")
    
    async def on_login_success(self):
        """Handle successful login"""
        try:
            logger.info("Login successful")
            
            # Mark as authenticated
            self.is_authenticated = True
            
            # Initialize views after successful login
            if hasattr(self, 'initialize_views'):
                await self.initialize_views()
            
            # Clear any existing views
            if hasattr(self.page, 'views'):
                self.page.views.clear()
            
            # Show dashboard
            await self.show_dashboard()
            
        except Exception as e:
            logger.error(f"Error in on_login_success: {str(e)}")
            logger.error(traceback.format_exc())
            await self.show_error(f"Failed to complete login: {str(e)}")
            self.is_authenticated = False
            self.storage.remove("access_token")
            if hasattr(self, 'page') and self.page is not None:
                await self.show_error("Failed to initialize application")
                await self.show_login()
    
    async def show_error(self, message: str):
        """Show error dialog"""
        try:
            if not self.page:
                logger.error("Cannot show error: page is None")
                return
                
            # Close any existing dialogs
            if hasattr(self.page, 'dialog') and self.page.dialog:
                self.page.dialog.open = False
            
            # Create and show error dialog
            error_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Error"),
                content=ft.Text(message),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: self.close_dialog())
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
            
            self.page.dialog = error_dialog
            error_dialog.open = True
            await safe_page_update(self.page)
            
        except Exception as e:
            logger.error(f"Error showing error dialog: {str(e)}")
            logger.error(traceback.format_exc())
            
    async def handle_login(self, e):
        """Handle login button click"""
        try:
            logger.info("=== HANDLE_LOGIN START ===")
            email = self.email_field.value
            password = self.password_field.value
            
            logger.info(f"Login attempt with email: {email}")
            
            # Disable login button during authentication
            self.login_button.disabled = True
            self.login_button.text = "Signing in..."
            self.page.update()
            
            # Call API for authentication
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/api/v1/auth/login/",
                    json={"email": email, "password": password}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    access_token = data.get("access")
                    
                    if access_token:
                        # Store token
                        self.access_token = access_token
                        self.is_authenticated = True
                        await self.page.client_storage.set_async("auth_token", access_token)
                        
                        # Set token in API client
                        api_client.set_auth_token(access_token)
                        logger.info("API client token set")
                        
                        logger.info("Login successful!")
                        
                        # Navigate to dashboard - route change will handle showing it
                        self.page.go("/dashboard")
                    else:
                        logger.error("No access token in response")
                        self._show_error("Invalid response from server")
                else:
                    logger.error(f"Login failed with status {response.status_code}")
                    self._show_error("Invalid email or password")
                    
        except Exception as ex:
            logger.error(f"Login error: {str(ex)}")
            self._show_error("An error occurred during login")
        finally:
            # Re-enable login button
            self.login_button.disabled = False
            self.login_button.text = "Sign In"
            self.page.update()
            logger.info("=== HANDLE_LOGIN END ===")
    
    def _show_error(self, message):
        """Show error message to user"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_600,
            duration=3000
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    async def show_login(self, e=None):
        """Show login form"""
        try:
            logger.info("=== SHOW_LOGIN START ===")
            logger.info("Showing login form")
            logger.info(f"Page object in show_login: {self.page}")
            logger.info(f"Page id in show_login: {id(self.page) if self.page else 'None'}")
            logger.info(f"Main layout exists: {hasattr(self, 'main')}")
            logger.info(f"Content exists: {hasattr(self, 'content')}")
            logger.info(f"Main controls count: {len(self.main.controls) if hasattr(self, 'main') else 'N/A'}")
            
            if not hasattr(self, 'page') or not self.page:
                logger.error("Page not available in show_login")
                return
                
            # Clear the main layout content
            self.content.content = ft.Container()
            
            # Create login view content directly in the main layout
            self.username_field = ft.TextField(
                label="Email",
                hint_text="Enter your email",
                width=400,
                border_radius=5,
                border_color="#e0e0e0",
                bgcolor="#ffffff",
                text_size=14,
            )
            self.password_field = ft.TextField(
                label="Password",
                hint_text="Enter your password",
                width=400,
                password=True,
                can_reveal_password=True,
                border_radius=5,
                border_color="#e0e0e0",
                bgcolor="#ffffff",
                text_size=14,
            )
            
            # Create login container
            login_container = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Welcome Back!", 
                            size=28, 
                            weight=ft.FontWeight.BOLD, 
                            color="#1976d2"
                        ),
                        ft.Text(
                            "Please sign in to continue", 
                            color="#757575", 
                            size=14
                        ),
                        ft.Container(height=20),
                        self.username_field,
                        ft.Container(height=15),
                        self.password_field,
                        ft.Container(height=25),
                        ft.ElevatedButton(
                            "Login",
                            on_click=self.login_click,
                            width=400,
                            height=45,
                            color="#ffffff",
                            bgcolor="#1976d2",
                        ),
                    ],
                    spacing=0,
                    width=400,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor="#ffffff",
                border_radius=10,
                padding=20,
                alignment=ft.alignment.center,
                width=400,
                height=300,
                border=ft.border.all(2, "#1976d2"),
            )
            logger.info(f"Login container dimensions: width={login_container.width}, height={login_container.height}")
            logger.info(f"Login container bgcolor: {login_container.bgcolor}")
            logger.info(f"Login container border: {login_container.border}")
            
            # Set the login container as content
            self.content.content = login_container
            logger.info(f"Login container set as content: {type(login_container)}")
            logger.info(f"Login container has children: {hasattr(login_container, 'content')}")
            
            # Add a test container to verify visibility
            test_container = ft.Container(
                content=ft.Text("TEST - If you see this, content is working!", size=20, color=ft.Colors.RED),
                bgcolor=ft.Colors.GREEN,
                width=200,
                height=50,
                alignment=ft.alignment.center,
            )
            
            # For debugging, add both test and login
            debug_column = ft.Column(
                [test_container, login_container],
                spacing=20,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
            self.content.content = debug_column
            logger.info("Debug column with test container set as content")
            
            # Make content expand to center the login form
            self.content.expand = True
            self.content.alignment = ft.alignment.center
            self.content.bgcolor = ft.Colors.YELLOW_50
            logger.info(f"Content expand set to: {self.content.expand}")
            logger.info(f"Content alignment set to: {self.content.alignment}")
            logger.info(f"Content bgcolor set to: {self.content.bgcolor}")
            
            # Hide navigation rail for login and center the content
            self.main.controls = [self.content]
            logger.info(f"Main controls updated: {[type(c).__name__ for c in self.main.controls]}")
            # Set a visible background for the main area during login
            self.main.bgcolor = ft.Colors.BLUE_50
            logger.info(f"Main bgcolor set to: {self.main.bgcolor}")
            
            logger.info("Login view created in main layout")
            
            # Try direct approach - add login form directly to page
            self.page.clean()
            
            # Create email and password fields
            email_field = ft.TextField(
                label="Email",
                value="admin@example.com",
                width=300,
                autofocus=True
            )
            password_field = ft.TextField(
                label="Password",
                password=True,
                value="admin123",
                can_reveal_password=True,
                width=300
            )
            
            # Create login button
            login_button = ft.ElevatedButton(
                "Sign In",
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                width=300,
                height=50,
                on_click=self.handle_login
            )
            
            # Create a centered column for login
            login_column = ft.Column(
                [
                    ft.Text("Lawyer Office Login", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Please sign in to continue", size=16, color=ft.Colors.GREY_600),
                    ft.Divider(height=20),
                    email_field,
                    password_field,
                    ft.Divider(height=20),
                    login_button
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
            
            # Store references for login handler
            self.email_field = email_field
            self.password_field = password_field
            self.login_button = login_button
            
            # Wrap in a container for better styling
            login_container = ft.Container(
                content=login_column,
                width=400,
                height=400,
                padding=30,
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.Colors.BLACK26,
                    offset=ft.Offset(0, 5),
                ),
            )
            
            # Center everything
            centered_container = ft.Container(
                content=login_container,
                expand=True,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.GREY_100,
            )
            
            self.page.add(centered_container)
            logger.info("Login form added directly to page")
            
            # Update the page
            try:
                logger.info("Updating page with login view...")
                logger.info(f"Page has {len(self.page.controls)} controls before update")
                for i, control in enumerate(self.page.controls):
                    logger.info(f"  Control {i}: {type(control).__name__} - {control}")
                
                # Check content details
                logger.info(f"Content type: {type(self.content)}")
                logger.info(f"Content expand: {self.content.expand}")
                logger.info(f"Content alignment: {self.content.alignment}")
                logger.info(f"Content bgcolor: {self.content.bgcolor}")
                logger.info(f"Content content type: {type(self.content.content)}")
                if hasattr(self.content.content, 'controls'):
                    logger.info(f"Content content has {len(self.content.content.controls)} controls")
                
                self.page.update()
                
                logger.info(f"Page has {len(self.page.controls)} controls after update")
                for i, control in enumerate(self.page.controls):
                    logger.info(f"  Control {i}: {type(control).__name__} - {control}")
                logger.info("Page updated successfully")
                logger.info("=== SHOW_LOGIN END ===")
            except Exception as update_error:
                logger.error(f"Error updating page: {str(update_error)}")
                logger.error(traceback.format_exc())
                
        except Exception as e:
            error_msg = f"Error in show_login: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            await self.show_error(f"Failed to show login form: {str(e)}")
    
    async def login_click(self, e):
        """Handle login button click"""
        try:
            # Get values from stored fields
            email = self.username_field.value
            password = self.password_field.value
            
            if not email or not password:
                await self.show_error("Please enter both email and password")
                return
            
            # Call API to authenticate (send email as username)
            login_data = await api_client.login(email, password)
            
            # Store the access token
            self.access_token = login_data.get('access')
            self.refresh_token = login_data.get('refresh', '')
            
            # Store in persistent storage
            self.storage.set("access_token", self.access_token)
            self.storage.set("refresh_token", self.refresh_token)
            
            # Set the API client token
            api_client.set_auth_token(self.access_token)
            
            # Mark as authenticated
            self.is_authenticated = True
            
            # Store user data if available
            if 'user' in login_data:
                self.user_data = login_data['user']
            
            # Show success message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Login successful!"),
                bgcolor=ft.Colors.GREEN
            )
            self.page.snack_bar.open = True
            await safe_page_update(self.page)
            
            # Navigate to dashboard
            await self.on_login_success()
            
        except Exception as login_error:
            logger.error(f"Login failed: {str(login_error)}")
            await self.show_error("Invalid email or password")
            await safe_page_update(self.page)
    
    async def show_dashboard(self):
        """Show dashboard view"""
        try:
            logger.info("Showing dashboard")
            
            if not hasattr(self, 'page') or not self.page:
                logger.error("Page not available in show_dashboard")
                return
            
            # Clear page and restore main layout
            self.page.clean()
            
            # Restore full main layout with navigation rail
            self.main.controls = [self.nav_rail, ft.VerticalDivider(width=1), self.content]
            self.main.bgcolor = None  # Reset background color
            
            # Add the main layout to the page
            self.page.add(self.main)
            logger.info(f"Main layout added to page. Page controls: {len(self.page.controls)}")
            
            # Set dashboard content
            self.content.content = self.dashboard_view
            self.content.expand = True  # Should expand to fill available space
            self.content.bgcolor = ft.Colors.GREY_50  # Set visible background
            logger.info(f"Dashboard content set. Content type: {type(self.dashboard_view)}")
            logger.info(f"Content has children: {hasattr(self.dashboard_view, 'content')}")
            
            # Reset dashboard data loading state to force refresh
            if hasattr(self.dashboard_view_instance, 'data_loaded'):
                self.dashboard_view_instance.data_loaded = False
                self.dashboard_view_instance.loading = False
                logger.info("Reset dashboard data_loaded flag for fresh load")
            
            # Update navigation rail selection
            self.nav_rail.selected_index = 0
            
            logger.info("Dashboard view displayed with main layout")
            logger.info(f"Main controls count: {len(self.main.controls)}")
            logger.info(f"Page controls before update: {len(self.page.controls)}")
            
            # Update the page
            try:
                self.page.update()
                logger.info(f"Page controls after update: {len(self.page.controls)}")
                logger.info("Page updated successfully with dashboard")
                
                # Trigger dashboard data loading
                logger.info("Checking if dashboard has did_mount_async method...")
                logger.info(f"Dashboard instance type: {type(self.dashboard_view_instance)}")
                logger.info(f"Dashboard instance methods: {[m for m in dir(self.dashboard_view_instance) if not m.startswith('_')]}")
                if hasattr(self.dashboard_view_instance, 'did_mount_async'):
                    logger.info("Calling did_mount_async to load dashboard data...")
                    await self.dashboard_view_instance.did_mount_async()
                    logger.info("did_mount_async completed")
                else:
                    logger.error("Dashboard view instance does not have did_mount_async method!")
            except Exception as e:
                logger.error(f"Error updating page: {str(e)}")
                logger.error(traceback.format_exc())
                
        except Exception as e:
            error_msg = f"Error in show_dashboard: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            await self.show_error(f"Failed to show dashboard: {str(e)}")
    
    async def on_logout(self):
        """Handle user logout"""
        try:
            self.is_authenticated = False
            self.access_token = None
            self.storage.remove("access_token")
            
            # Clear the API client token
            api_client.clear_auth_token()
            
            await self.show_login()
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Error during logout. Please refresh the page."))
            self.page.snack_bar.open = True
            await safe_page_update(self.page)
    
    async def show_appointments(self):
        """Show appointments view"""
        try:
            logger.info("Showing appointments")
            
            if not hasattr(self, 'page') or not self.page:
                logger.error("Page not available in show_appointments")
                return
                
            # Reset navigation to appointments
            self.nav_rail.selected_index = 1
            
            # Create fresh appointments instance
            appointments_instance = AppointmentsView(self)
            self.content.content = appointments_instance.build()
            
            # Call did_mount_async to load data
            if hasattr(appointments_instance, 'did_mount_async'):
                try:
                    await appointments_instance.did_mount_async()
                except Exception as ex:
                    logger.warning(f"Appointments did_mount_async failed: {str(ex)}")
            
            # Update main layout
            self.main.controls = [self.nav_rail, ft.VerticalDivider(width=1), self.content]
            
            # Update the page
            try:
                self.page.update()
                logger.info("Page updated successfully with appointments view")
            except Exception as e:
                logger.error(f"Error updating page: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in show_appointments: {str(e)}")
            logger.error(traceback.format_exc())
            await self.show_error("Failed to load appointments")
    
    async def show_clients(self):
        """Show clients view"""
        try:
            logger.info("Showing clients")
            
            if not hasattr(self, 'page') or not self.page:
                logger.error("Page not available in show_clients")
                return
                
            # Reset navigation to clients
            self.nav_rail.selected_index = 2
            
            # Create a fresh clients view instance
            clients_instance = ClientsView(self)
            self.content.content = clients_instance.build()
            
            # Call did_mount_async to load data
            if hasattr(clients_instance, 'did_mount_async'):
                try:
                    await clients_instance.did_mount_async()
                except Exception as ex:
                    logger.warning(f"Clients did_mount_async failed: {str(ex)}")
            
            # Update main layout
            self.main.controls = [self.nav_rail, ft.VerticalDivider(width=1), self.content]
            
            # Update the page
            try:
                self.page.update()
                logger.info("Page updated successfully with clients view")
            except Exception as e:
                logger.error(f"Error updating page: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in show_clients: {str(e)}")
            logger.error(traceback.format_exc())
            await self.show_error("Failed to load clients")
    
    async def show_profile(self):
        """Show profile view"""
        try:
            logger.info("Showing profile")
            
            if not hasattr(self, 'page') or not self.page:
                logger.error("Page not available in show_profile")
                return
                
            # Reset navigation to profile
            self.nav_rail.selected_index = 3
            
            # Create a fresh profile view instance
            profile_instance = ProfileView(self)
            self.content.content = profile_instance.build()
            
            # Call did_mount_async to load data
            if hasattr(profile_instance, 'did_mount_async'):
                try:
                    await profile_instance.did_mount_async()
                except Exception as ex:
                    logger.warning(f"Profile did_mount_async failed: {str(ex)}")
            
            # Update main layout
            self.main.controls = [self.nav_rail, ft.VerticalDivider(width=1), self.content]
            
            # Update the page
            try:
                self.page.update()
                logger.info("Page updated successfully with profile view")
            except Exception as e:
                logger.error(f"Error updating page: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in show_profile: {str(e)}")
            logger.error(traceback.format_exc())
            await self.show_error("Failed to load profile")
    
    async def route_change(self, route: str):
        """Handle route changes"""
        try:
            logger.info("=== ROUTE_CHANGE START ===")
            logger.info(f"Route changed to: {route}")
            logger.info(f"Is authenticated: {self.is_authenticated}")
            logger.info(f"Access token exists: {self.access_token is not None}")
            logger.info(f"Page has {len(self.page.controls)} controls")
            
            # Don't clear views anymore since we're using main layout approach
            
            if route == "/login":
                logger.info("Route is /login - showing login form")
                await self.show_login()
            elif route == "/":
                logger.info(f"Root route accessed. is_authenticated: {self.is_authenticated}")
                logger.info(f"Access token exists: {self.access_token is not None}")
                if not self.is_authenticated:
                    logger.info("User not authenticated, showing login form")
                    await self.show_login()
                else:
                    logger.info("User authenticated, redirecting to dashboard")
                    self.page.go("/dashboard")
            elif route == "/dashboard":
                logger.info(f"Dashboard route accessed. is_authenticated: {self.is_authenticated}")
                logger.info(f"Access token exists: {self.access_token is not None}")
                if not self.is_authenticated:
                    logger.info("User not authenticated, showing login form")
                    self.page.go("/login")
                else:
                    await self.show_dashboard()
            elif route == "/appointments":
                logger.info(f"Appointments route accessed. is_authenticated: {self.is_authenticated}")
                logger.info(f"Access token exists: {self.access_token is not None}")
                if not self.is_authenticated:
                    logger.info("User not authenticated, redirecting to login")
                    self.page.go("/login")
                else:
                    await self.show_appointments()
            elif route == "/clients":
                logger.info(f"Clients route accessed. is_authenticated: {self.is_authenticated}")
                logger.info(f"Access token exists: {self.access_token is not None}")
                if not self.is_authenticated:
                    logger.info("User not authenticated, redirecting to login")
                    self.page.go("/login")
                else:
                    await self.show_clients()
            elif route == "/profile":
                logger.info(f"Profile route accessed. is_authenticated: {self.is_authenticated}")
                logger.info(f"Access token exists: {self.access_token is not None}")
                if not self.is_authenticated:
                    logger.info("User not authenticated, showing login form")
                    self.page.go("/login")
                else:
                    await self.show_profile()
            else:
                logger.warning(f"Unknown route: {route}")
                # For unknown routes, redirect to login or dashboard based on auth status
                if not self.is_authenticated:
                    self.page.go("/login")
                else:
                    self.page.go("/dashboard")

        except Exception as e:
            logger.error(f"Error in route_change: {str(e)}")
            logger.error(traceback.format_exc())
            await self.show_error(f"Failed to navigate to {route}")
        finally:
            logger.info("=== ROUTE_CHANGE END ===")

async def main(page: ft.Page):
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    logger.info("Initializing application...")

    try:
        # Set page properties
        page.title = "Lawyer Office Management"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.window_width = 1280
        page.window_height = 800
        page.window_resizable = True
        page.bgcolor = ft.Colors.GREY_100
        
        # Set page theme
        page.theme = ft.Theme(
            color_scheme_seed="blue",
            use_material3=True
        )

        # Initialize the app
        app = LawyerOfficeApp(page)
        
        # Set up route change handler
        def route_change_wrapper(e):
            # Extract route from event
            route = e.route if hasattr(e, 'route') else str(e)
            logger.info(f"Route change wrapper called with: {route}")
            
            # Use a simple approach - just call the method
            try:
                # Check if we're in an async context
                try:
                    loop = asyncio.get_running_loop()
                    # We're in an async context, create a task with a callback
                    task = asyncio.create_task(app.route_change(route))
                    # Add error handling for the task
                    task.add_done_callback(lambda t: logger.error(f"Route change task error: {t.exception()}") if t.exception() else None)
                except RuntimeError:
                    # No running loop, create one and run the coroutine
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(app.route_change(route))
                    loop.close()
            except Exception as ex:
                logger.error(f"Error in route_change_wrapper: {str(ex)}")
        
        page.on_route_change = route_change_wrapper
        
        # Set up view pop handler
        async def view_pop(view):
            try:
                if hasattr(page, 'views') and len(page.views) > 1:
                    page.views.pop()
                    top_view = page.views[-1]
                    page.route = top_view.route
                    # Update page safely
                    try:
                        if page is not None:
                            if hasattr(page, 'update') and callable(getattr(page, 'update')):
                                page.update()
                            elif hasattr(page, 'update_sync') and callable(getattr(page, 'update_sync')):
                                page.update_sync()
                    except Exception as update_error:
                        logger.error(f"Failed to update page: {str(update_error)}")
                        # Don't re-raise, just log the error
            except Exception as e:
                logger.error(f"Error in view_pop: {str(e)}")
        
        # Set up event handlers
        page.on_view_pop = view_pop
        
        # Set initial route
        initial_route = "/"
        if hasattr(page, 'route') and page.route:
            initial_route = page.route
            
        logger.info(f"Starting with initial route: {initial_route}")
        await app.route_change(initial_route)
        
    except Exception as app_error:
        logger.error(f"Application initialization error: {str(app_error)}")
        logger.error(traceback.format_exc())
        
        # Show error to user
        if 'page' in locals() and page is not None:
            try:
                page.clean()
                page.add(ft.Text(f"Application error: {str(app_error)}", color="red"))
                # Update page safely
                try:
                    if page is not None:
                        if hasattr(page, 'update') and callable(getattr(page, 'update')):
                            page.update()
                        elif hasattr(page, 'update_sync') and callable(getattr(page, 'update_sync')):
                            page.update_sync()
                except Exception as update_error:
                    logger.error(f"Failed to update page: {str(update_error)}")
                    # Don't re-raise, just log the error
            except Exception as update_error:
                logger.error(f"Failed to update page with error: {str(update_error)}")
                logger.error(traceback.format_exc())
        
        return  # Exit if we can't initialize the app
        
    # Main application loop
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Application shutdown requested")
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        logger.info("Application shutdown complete")
        
    # If we get here, something went wrong
    if 'page' in locals() and page is not None:
        try:
            page.clean()
            page.add(ft.Text("An unexpected error occurred. Please refresh the page.", color="red"))
            if hasattr(page, 'update'):
                try:
                    page.update()
                except Exception as e:
                    logger.error(f"Error updating page: {str(e)}")
            else:
                try:
                    page.update()
                except Exception as e:
                    logger.error(f"Error updating page: {str(e)}")
        except Exception as e:
            print(f"Failed to show error message: {str(e)}")
            
    return  # Exit the application

if __name__ == "__main__":
    import asyncio
    
    # Ensure the event loop is properly set up for Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the app
    ft.app(target=main)
