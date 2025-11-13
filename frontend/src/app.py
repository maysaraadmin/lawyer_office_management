import flet as ft
import sys
import os
import asyncio
import logging
import traceback
from pathlib import Path
from typing import Optional, Dict, Any

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
    from services.storage import Storage
except ImportError as e:
    logger.error(f"Import error: {str(e)}")
    raise

class LawyerOfficeApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Lawyer Office Management"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.window_width = 1280
        self.page.window_height = 800
        self.page.window_resizable = True
        
        # Set page theme
        self.page.theme = ft.Theme(
            color_scheme_seed="blue",
            use_material3=True
        )
        
        # Define colors
        self.primary_color = "#1976d2"
        self.background_color = "#f5f5f5"
        self.text_color = "#000000"
        
        # Initialize storage and authentication state
        self.storage = Storage()
        self.is_authenticated = bool(self.storage.get("access_token"))
        self.user_data: Dict[str, Any] = {}
        
        logger.info(f"App initialized. Authenticated: {self.is_authenticated}")
        
        # Initialize views
        self.dashboard_view = DashboardView(self)
        self.appointments_view = AppointmentsView(self)
        self.clients_view = ClientsView(self)
        # Initialize login view
        self.login_view = None
        self.profile_view = None
        
        # Set up navigation
        self.nav_items = [
            ft.NavigationRailDestination(
                icon="dashboard_outlined",
                selected_icon="dashboard",
                label="Dashboard"
            ),
            ft.NavigationRailDestination(
                icon="calendar_today_outlined",
                selected_icon="calendar_today",
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
        self.page.update()
        
        # Initialize login view if not authenticated
        if not self.is_authenticated:
            # We'll show the login form when the page is ready
            self.page.on_resize = lambda _: asyncio.create_task(self.show_login()) if not self.is_authenticated else None
    
    async def navigate(self, e):
        if not self.is_authenticated:
            return
            
        index = e.control.selected_index
        if index == 0:
            self.content.content = self.dashboard_view
        elif index == 1:
            self.content.content = self.appointments_view
        elif index == 2:
            self.content.content = self.clients_view
        elif index == 3:  # Profile
            if not self.profile_view:
                self.profile_view = ProfileView(self.page)
                await self.profile_view.did_mount_async()
            self.content.content = self.profile_view
        
        self.page.update()
    
    async def on_login_success(self):
        """Handle successful login"""
        try:
            if not hasattr(self, 'page') or self.page is None:
                logger.error("Page object is not available in on_login_success")
                return
                
            self.is_authenticated = True
            # Store authentication token (in a real app, this would come from your auth service)
            self.storage.set("access_token", "dummy_token")
            
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
                await self.page.update_async()
            
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
            await self.page.update_async()
            
        except Exception as e:
            logger.error(f"Error showing error dialog: {str(e)}")
            if 'traceback' in globals():
                logger.error(traceback.format_exc())
            
    async def show_login(self, e=None):
        """Show login form"""
        try:
            logger.info("Showing login form")
            
            if not hasattr(self, 'page') or not self.page:
                logger.error("Page not available in show_login")
                return
                
            # Clean up the page
            self.page.controls.clear()
            
            # Create login form with error handling
            try:
                login_form = LoginForm(self.on_login_success)
                
                # Create main container with gradient background
                login_container = ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                content=login_form,
                                padding=40,
                                width=500,
                                bgcolor=ft.colors.WHITE,
                                border_radius=10,
                                shadow=ft.BoxShadow(
                                    spread_radius=1,
                                    blur_radius=15,
                                    color=ft.colors.BLUE_GREY_300,
                                    offset=ft.Offset(0, 0),
                                ),
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                    ),
                    padding=40,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_center,
                        end=ft.alignment.bottom_center,
                        colors=[ft.colors.BLUE_50, ft.colors.WHITE],
                    ),
                    expand=True,
                )
                
                # Add login container to the page
                self.page.add(login_container)
                self.page.route = "/login"
                
                # Update the page
                if hasattr(self.page, 'update_async'):
                    await self.page.update_async()
                else:
                    await self.page.update()
                    
            except Exception as form_error:
                logger.error(f"Error creating login form: {str(form_error)}")
                logger.error(traceback.format_exc())
                await self.show_error("Failed to initialize login form. Please refresh the page.")
                
        except Exception as e:
            error_msg = f"Error in show_login: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            await self.show_error("An error occurred while loading the login page.")

    async def on_logout(self):
        """Handle user logout"""
        self.is_authenticated = False
        await self.show_login()
    
    async def route_change(self, route):
        """Handle route changes"""
        try:
            logger.info(f"Route changed to: {route}")
            
            # Clear existing views
            if hasattr(self.page, 'views'):
                self.page.views.clear()
            
            if route == "/login":
                await self.show_login()
            elif route == "/dashboard":
                if not await self.is_authenticated():
                    logger.info("User not authenticated, showing login form")
                    self.page.route = "/login"
                    await self.show_login()
                    return
                await self.show_dashboard()
            else:
                # 404 Page
                if hasattr(self.page, 'views'):
                    self.page.views.append(
                        ft.View(
                            "/404",
                            [
                                ft.AppBar(title=ft.Text("404"), bgcolor=self.primary_color),
                                ft.Text("Page not found"),
                            ],
                        )
                    )
            
            if hasattr(self.page, 'update_async'):
                await self.page.update_async()
            else:
                await self.page.update()
            
        except Exception as e:
            logger.error(f"Error in route_change: {str(e)}")
            if 'traceback' in globals():
                logger.error(traceback.format_exc())
            await self.show_error(f"An error occurred: {str(e)}")

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
        async def route_change(e):
            try:
                route = e.route if hasattr(e, 'route') else (e if isinstance(e, str) else "/")
                logger.info(f"Route changed to: {route}")
                
                # Clear existing views
                if hasattr(page, 'views'):
                    page.views.clear()
                
                if route == "/login" or route == "/":
                    await app.show_login()
                elif route == "/dashboard":
                    if not app.is_authenticated:
                        logger.info("User not authenticated, redirecting to login")
                        page.route = "/login"
                        await app.show_login()
                        return
                    await app.show_dashboard()
                else:
                    # 404 Page
                    page.views.append(
                        ft.View(
                            "/404",
                            [
                                ft.AppBar(title=ft.Text("404")),
                                ft.Text("Page not found"),
                            ],
                        )
                    )
                
                if hasattr(page, 'update'):
                    await page.update()
                else:
                    page.update()
                    
            except Exception as route_error:
                logger.error(f"Error in route_change: {str(route_error)}")
                if 'traceback' in globals():
                    logger.error(traceback.format_exc())
                if hasattr(page, 'update'):
                    await page.update()
                else:
                    page.update()
        
        # Set up view pop handler
        async def view_pop(view):
            try:
                if hasattr(page, 'views') and len(page.views) > 1:
                    page.views.pop()
                    top_view = page.views[-1]
                    page.route = top_view.route
                    if hasattr(page, 'update'):
                        await page.update()
                    else:
                        page.update()
            except Exception as e:
                logger.error(f"Error in view_pop: {str(e)}")
        
        # Set up event handlers
        page.on_route_change = route_change
        page.on_view_pop = view_pop
        
        # Set initial route
        initial_route = "/login"
        if hasattr(page, 'route') and page.route:
            initial_route = page.route
            
        logger.info(f"Starting with initial route: {initial_route}")
        await route_change(initial_route)
        
    except Exception as app_error:
        logger.error(f"Application initialization error: {str(app_error)}")
        if 'traceback' in globals():
            logger.error(traceback.format_exc())
        
        # Show error to user
        if 'page' in locals() and page is not None:
            try:
                page.clean()
                page.add(ft.Text(f"Application error: {str(app_error)}", color="red"))
                if hasattr(page, 'update'):
                    await page.update()
                else:
                    page.update()
            except Exception as update_error:
                logger.error(f"Failed to update page with error: {str(update_error)}")
                if 'traceback' in globals():
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
        if 'traceback' in globals():
            logger.error(traceback.format_exc())
    finally:
        logger.info("Application shutdown complete")
        
    # If we get here, something went wrong
    if 'page' in locals() and page is not None:
        try:
            page.clean()
            page.add(ft.Text("An unexpected error occurred. Please refresh the page.", color="red"))
            if hasattr(page, 'update'):
                await page.update()
            else:
                page.update()
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
