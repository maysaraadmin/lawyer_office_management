import flet as ft
import sys
import os
import asyncio
import logging
import traceback
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
    from .views.profile.profile_view import ProfileView
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
        self.dashboard_view = DashboardView(self).build()
        self.appointments_view = AppointmentsView(self).build()
        self.clients_view = ClientsView(self).build()
        # Initialize profile view
        self.profile_view = None
        self.profile_instance = None
        
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
                icon="people_alt",
                selected_icon="groups",
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
        
        # Set initial view based on authentication
        self.content.content = self.dashboard_view if self.is_authenticated else ft.Container()
        
        # Main layout
        self.main = ft.Row(
            [
                self.nav_rail,
                ft.VerticalDivider(width=1),
                self.content,
            ],
            expand=True,
        )
        
        # Set the initial view
        self.page.add(self.main)
        try:
            self.page.update()
        except Exception as e:
            logger.error(f"Error updating page: {str(e)}")
        
        # Initialize login
        self.login_form = None
    
    async def navigate(self, e):
        try:
            index = e.control.selected_index
            if index == 0:
                # Create fresh dashboard view
                dashboard_instance = DashboardView(self)
                self.content.content = dashboard_instance.build()
                # Call did_mount_async to load data
                if hasattr(dashboard_instance, 'did_mount_async'):
                    try:
                        await dashboard_instance.did_mount_async()
                    except Exception as ex:
                        logger.warning(f"Dashboard did_mount_async failed: {str(ex)}")
                self.page.route = "/dashboard"
            elif index == 1:
                self.content.content = self.appointments_view
                self.page.route = "/appointments"
            elif index == 2:
                self.content.content = self.clients_view
                self.page.route = "/clients"
            elif index == 3:  # Profile
                if not self.profile_view:
                    # Create the instance
                    profile_instance = ProfileView(self.page)
                    # Build the view
                    self.profile_view = profile_instance.build()
                    # Store the instance for later use
                    self.profile_instance = profile_instance
                    # Call did_mount_async on the instance
                    if hasattr(profile_instance, 'did_mount_async'):
                        try:
                            await profile_instance.did_mount_async()
                        except Exception as e:
                            logger.warning(f"Profile view did_mount_async failed: {str(e)}")
                self.content.content = self.profile_view
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
            if not hasattr(self, 'page') or self.page is None:
                logger.error("Page object is not available in on_login_success")
                return
                
            self.is_authenticated = True
            # Store authentication token (in a real app, this would come from your auth service)
            self.storage.set("access_token", "dummy_token")
            self.access_token = "dummy_token"
            
            # Set the API client token
            api_client.set_auth_token(self.access_token)
            
            # Initialize views after successful login
            if hasattr(self, 'initialize_views'):
                await self.initialize_views()
            
            logger.info("User logged in successfully")
            
            # Clear any existing views
            if hasattr(self.page, 'views'):
                self.page.views.clear()
            
            # Navigate to dashboard
            if hasattr(self.page, 'go'):
                self.page.go("/dashboard")
            else:
                self.page.route = "/dashboard"
                await safe_page_update(self.page)
            
        except Exception as e:
            error_msg = f"Login success handler error: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
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
            
    async def show_login(self, e=None):
        """Show login form"""
        try:
            logger.info("Showing login form")
            logger.info(f"Page object in show_login: {self.page}")
            logger.info(f"Page id in show_login: {id(self.page) if self.page else 'None'}")
            
            if not hasattr(self, 'page') or not self.page:
                logger.error("Page not available in show_login")
                return
                
            # Create login view
            login_view = ft.View(
                "/login",
                [
                    ft.Container(
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
                                ft.TextField(
                                    label="Username",
                                    hint_text="Enter your username",
                                    width=400,
                                    border_radius=5,
                                    border_color="#e0e0e0",
                                    bgcolor="#ffffff",
                                    text_size=14,
                                ),
                                ft.Container(height=15),
                                ft.TextField(
                                    label="Password",
                                    hint_text="Enter your password",
                                    width=400,
                                    password=True,
                                    can_reveal_password=True,
                                    border_radius=5,
                                    border_color="#e0e0e0",
                                    bgcolor="#ffffff",
                                    text_size=14,
                                ),
                                ft.Container(height=15),
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
                    )
                ],
                bgcolor="#f5f5f5",
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            )
            
            logger.info("Login view created")
            
            # Clear all views and add login view
            self.page.views.clear()
            self.page.views.append(login_view)
            logger.info(f"Login view added. Views count: {len(self.page.views)}")
            
            # Update the page
            try:
                logger.info("Updating page with login view...")
                self.page.update()
                logger.info("Page updated successfully")
            except Exception as update_error:
                logger.error(f"Error updating page: {str(update_error)}")
                
        except Exception as e:
            error_msg = f"Error in show_login: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            await self.show_error(f"Failed to show login form: {str(e)}")
    
    async def login_click(self, e):
        """Handle login button click"""
        try:
            # For now, just simulate successful login
            await self.on_login_success()
        except Exception as ex:
            logger.error(f"Login error: {str(ex)}")
            await self.show_error("Login failed. Please try again.")

    async def show_dashboard(self):
        """Show dashboard view"""
        try:
            logger.info("Showing dashboard")
            
            if not hasattr(self, 'page') or not self.page:
                logger.error("Page not available in show_dashboard")
                return
                
            # Clean up the page
            self.page.views.clear()
            
            # Reset navigation to dashboard
            self.nav_rail.selected_index = 0
            
            # Create the dashboard view
            dashboard_instance = DashboardView(self)
            dashboard_view = dashboard_instance.build()
            logger.info(f"Dashboard view created: {type(dashboard_view)}")
            
            # Update content
            self.content.content = dashboard_view
            logger.info("Content updated with dashboard view")
            
            # Update main layout
            self.main.controls = [self.nav_rail, ft.VerticalDivider(width=1), self.content]
            
            # Create and add the dashboard view
            dashboard_view_full = ft.View(
                "/dashboard",
                [self.main],
                padding=ft.padding.all(0),
                bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.GREY_50)
            )
            self.page.views.append(dashboard_view_full)
            
            # Update the page
            try:
                self.page.update()
                logger.info("Page updated successfully")
                
                # Call did_mount_async after the view is added to the page
                if hasattr(dashboard_instance, 'did_mount_async'):
                    try:
                        await dashboard_instance.did_mount_async()
                        logger.info("Dashboard did_mount_async called successfully")
                    except Exception as e:
                        logger.warning(f"Dashboard view did_mount_async failed: {str(e)}")
            except Exception as e:
                logger.error(f"Error updating page: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in show_dashboard: {str(e)}")
            logger.error(traceback.format_exc())
            await self.show_error("Failed to load dashboard")
    
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
    
    async def show_profile(self):
        """Show profile view"""
        try:
            logger.info("Showing profile")
            logger.info(f"Current page route before show_profile: {getattr(self.page, 'route', 'None')}")
            
            if not hasattr(self, 'page') or not self.page:
                logger.error("Page not available in show_profile")
                return
                
            # Clean up the page
            self.page.views.clear()
            
            # Reset navigation to profile
            self.nav_rail.selected_index = 3
            logger.info("Navigation rail set to profile index 3")
            
            # Create profile view instance if not exists
            profile_instance = None
            if not self.profile_view:
                try:
                    # Create the instance
                    profile_instance = ProfileView(self.page)
                    # Build the view
                    self.profile_view = profile_instance.build()
                    # Store the instance for later use
                    self.profile_instance = profile_instance
                    logger.info("Profile view built successfully")
                except Exception as e:
                    logger.error(f"Error creating profile view: {str(e)}")
                    logger.error(traceback.format_exc())
                    # Show error and return to dashboard
                    await self.show_error("Failed to load profile view")
                    return
            else:
                # Use existing instance if available
                profile_instance = getattr(self, 'profile_instance', None)
                logger.info("Using existing profile view")
            
            # Update content
            self.content.content = self.profile_view
            logger.info("Content updated with profile view")
            
            # Update main layout
            self.main.controls = [self.nav_rail, ft.VerticalDivider(width=1), self.content]
            
            # Create and add the profile view
            profile_view_full = ft.View(
                "/profile",
                [self.main],
                padding=ft.padding.all(0),
                bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.GREY_50)
            )
            self.page.views.append(profile_view_full)
            
            # Update the page
            try:
                self.page.update()
                logger.info("Page updated successfully with profile view")
                
                # Call did_mount_async after the view is added to the page
                if profile_instance and hasattr(profile_instance, 'did_mount_async'):
                    try:
                        await profile_instance.did_mount_async()
                        logger.info("Profile did_mount_async called successfully")
                    except Exception as e:
                        logger.warning(f"Profile view did_mount_async failed: {str(e)}")
            except Exception as e:
                logger.error(f"Error updating page: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in show_profile: {str(e)}")
            logger.error(traceback.format_exc())
            await self.show_error("Failed to load profile")
    
    async def show_appointments(self):
        """Show appointments view"""
        try:
            logger.info("Showing appointments")
            
            if not hasattr(self, 'page') or not self.page:
                logger.error("Page not available in show_appointments")
                return
                
            # Clean up the page
            self.page.views.clear()
            
            # Reset navigation to appointments
            self.nav_rail.selected_index = 1
            
            # Use the pre-built appointments view
            self.content.content = self.appointments_view
            
            # Update main layout
            self.main.controls = [self.nav_rail, ft.VerticalDivider(width=1), self.content]
            
            # Create and add the appointments view
            appointments_view_full = ft.View(
                "/appointments",
                [self.main],
                padding=ft.padding.all(0),
                bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.GREY_50)
            )
            self.page.views.append(appointments_view_full)
            
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
                
            # Clean up the page
            self.page.views.clear()
            
            # Reset navigation to clients
            self.nav_rail.selected_index = 2
            
            # Use the pre-built clients view
            self.content.content = self.clients_view
            
            # Update main layout
            self.main.controls = [self.nav_rail, ft.VerticalDivider(width=1), self.content]
            
            # Create and add the clients view
            clients_view_full = ft.View(
                "/clients",
                [self.main],
                padding=ft.padding.all(0),
                bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.GREY_50)
            )
            self.page.views.append(clients_view_full)
            
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
    
    async def route_change(self, route):
        """Handle route changes"""
        try:
            logger.info(f"Route changed to: {route}")
            
            # Clear existing views
            if hasattr(self.page, 'views'):
                self.page.views.clear()
            
            if route == "/login":
                await self.show_login()
            elif route == "/":
                logger.info(f"Root route accessed. is_authenticated: {self.is_authenticated}")
                logger.info(f"Access token exists: {self.access_token is not None}")
                if not self.is_authenticated:
                    await self.show_login()
                else:
                    await self.show_dashboard()
            elif route == "/dashboard":
                logger.info(f"Dashboard route accessed. is_authenticated: {self.is_authenticated}")
                logger.info(f"Access token exists: {self.access_token is not None}")
                if not self.is_authenticated:
                    logger.info("User not authenticated, showing login form")
                    # Use page.go to navigate to login without triggering route_change again
                    self.page.go("/login")
                else:
                    await self.show_dashboard()
            elif route == "/appointments":
                logger.info(f"Appointments route accessed. is_authenticated: {self.is_authenticated}")
                logger.info(f"Access token exists: {self.access_token is not None}")
                if not self.is_authenticated:
                    logger.info("User not authenticated, redirecting to login")
                    # Use page.go to navigate to login without triggering route_change again
                    self.page.go("/login")
                else:
                    await self.show_appointments()
            elif route == "/clients":
                logger.info(f"Clients route accessed. is_authenticated: {self.is_authenticated}")
                logger.info(f"Access token exists: {self.access_token is not None}")
                if not self.is_authenticated:
                    logger.info("User not authenticated, redirecting to login")
                    # Use page.go to navigate to login without triggering route_change again
                    self.page.go("/login")
                else:
                    await self.show_clients()
            elif route == "/profile":
                logger.info(f"Profile route accessed. is_authenticated: {self.is_authenticated}")
                logger.info(f"Access token exists: {self.access_token is not None}")
                if not self.is_authenticated:
                    logger.info("User not authenticated, redirecting to login")
                    # Use page.go to navigate to login without triggering route_change again
                    self.page.go("/login")
                else:
                    await self.show_profile()
            else:
                # Default to login for unknown routes
                await self.show_login()

        except Exception as e:
            logger.error(f"Error in route_change: {str(e)}")
            logger.error(traceback.format_exc())
            await self.show_error(f"Failed to navigate to {route}")

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
        initial_route = "/login"
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
