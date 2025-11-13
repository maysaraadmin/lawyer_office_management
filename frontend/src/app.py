import flet as ft
import sys
import os
import asyncio
from .login import LoginForm  # Updated to use relative import

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import views
from .views.dashboard import DashboardView
from .views.appointments import AppointmentsView
from .views.clients import ClientsView
from .views.auth import login as login_module
from .views.profile.profile_view import ProfileView

# Import services
from services.storage import Storage

class LawyerOfficeApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Lawyer Office Management"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.window_width = 1280
        self.page.window_height = 800
        self.page.window_resizable = True
        
        # Set page theme with string colors
        self.page.theme = ft.Theme(
            color_scheme_seed="blue"
        )
        
        # Define colors as strings for compatibility
        self.primary_color = "#1976d2"
        self.background_color = "#f5f5f5"
        self.text_color = "#000000"
        
        # Check if user is authenticated
        self.is_authenticated = bool(Storage.get("access_token"))
        
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
            # Call show_login directly since we're already in the event loop
            self.page.clean()
            asyncio.create_task(self.show_login())
    
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
        self.is_authenticated = True
        self.content.content = self.dashboard_view
        self.page.update()
    
    async def show_login(self, e=None):
        print("show_login called")
        try:
            # Clear the page and add the login form directly
            self.page.clean()
            login_form = LoginForm(self.on_login_success)
            self.page.add(
                ft.AppBar(title=ft.Text("Login"), bgcolor="#f5f5f5"),
                ft.Container(
                    content=login_form,
                    alignment=ft.alignment.center,
                    expand=True,
                    padding=20
                )
            )
            self.page.update()
            print("Login form displayed")
            
        except Exception as ex:
            print(f"Error in show_login: {str(ex)}")
            import traceback
            traceback.print_exc()
    
    async def on_logout(self):
        self.is_authenticated = False
        await self.show_login()

async def main(page: ft.Page):
    # Set up app
    app = LawyerOfficeApp(page)
    
    # Handle route changes
    async def route_change(e):
        print(f"Route changed to: {page.route}")
        
        # Clear views
        page.views.clear()
        
        # If not authenticated, always show login regardless of the route
        if not app.is_authenticated:
            print("User not authenticated, showing login form")
            # Create a container for the login form
            login_form = LoginForm(app.on_login_success)
            
            # Create the login view with the form
            login_view = ft.View(
                "/login",
                [
                    ft.AppBar(title=ft.Text("Login"), bgcolor="#f5f5f5"),
                    ft.Container(
                        content=login_form,
                        alignment=ft.alignment.center,
                        expand=True,
                    )
                ],
                padding=20,
                spacing=0,
                scroll=ft.ScrollMode.AUTO
            )
            
            page.views.append(login_view)
            page.update()
            return
            
        # User is authenticated, handle protected routes
            if page.route == "/" or page.route == "/dashboard" or not page.route:
                page.views.append(ft.View(
                    "/dashboard",
                    [
                        ft.AppBar(title=ft.Text("Dashboard"), bgcolor="#f5f5f5"),
                        app.main
                    ]
                ))
            elif page.route == "/login":
                page.go("/dashboard")
                return
            elif page.route == "/profile":
                page.views.append(ft.View(
                    "/profile",
                    [
                        ft.AppBar(title=ft.Text("Profile"), bgcolor="#f5f5f5"),
                        app.main
                    ]
                ))
                if not app.profile_view:
                    app.profile_view = ProfileView(page)
                app.content.content = app.profile_view
            else:
                page.views.append(ft.View(
                    "/not-found",
                    [
                        ft.AppBar(title=ft.Text("Not Found"), bgcolor="#f5f5f5"),
                        ft.Text("Page not found")
                    ]
                ))
        
        page.update()
    
    # Set up route change handler
    page.on_route_change = route_change
    
    # Set initial route
    initial_route = page.route or "/"
    if not app.is_authenticated and initial_route != "/login":
        page.route = "/login"
    elif initial_route == "/":
        page.route = "/dashboard"
    
    # Trigger initial route change
    await route_change(None)

if __name__ == "__main__":
    import asyncio
    
    # Ensure the event loop is properly set up for Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the app
    ft.app(target=main)
