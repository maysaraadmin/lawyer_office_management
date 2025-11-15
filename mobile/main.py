import flet as ft
import asyncio
import os
from dotenv import load_dotenv
from typing import Optional

# Import views
from src.views.login import LoginView
from src.views.dashboard import MobileDashboardView
from src.views.appointments import MobileAppointmentsView
from src.views.clients import MobileClientsView
from src.views.profile import ProfileView

# Import API client
from src.services.api_client import APIClient

load_dotenv()

# Color constants
BLUE_600 = "#2563EB"
GRAY_900 = "#111827"
GRAY_700 = "#374151"
GRAY_500 = "#6B7280"
GRAY_300 = "#D1D5DB"
GRAY_200 = "#E5E7EB"
WHITE = "#FFFFFF"

class LawyerOfficeMobileApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        
        # Authentication state
        self.auth_token: Optional[str] = None
        self.user_data: Optional[dict] = None
        self.is_authenticated = False
        
        # API client
        self.api_client = APIClient(self.api_base_url)
        
        # Views
        self.login_view = LoginView(page, on_login_success=self._on_login_success)
        self.dashboard_view = MobileDashboardView(page, self.api_client)
        self.appointments_view = MobileAppointmentsView(page, self.api_client)
        self.clients_view = MobileClientsView(page, self.api_client)
        self.profile_view = ProfileView(page)  # Initialize without auth_token first
        
        # Navigation state
        self.current_route = "/"
        self.bottom_nav_index = 0

        self._setup_page()
        self._setup_navigation()
        self._check_authentication()

    def _setup_page(self):
        """Configure the page settings"""
        self.page.title = "Lawyer Office Mobile"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.vertical_alignment = ft.MainAxisAlignment.START

        # Set up the app's theme
        self.page.theme = ft.Theme(
            color_scheme_seed=BLUE_600,
            visual_density=ft.VisualDensity.COMFORTABLE,
        )

        # Set mobile-specific settings
        self.page.window_min_width = 360
        self.page.window_min_height = 640
        self.page.window_width = 390
        self.page.window_height = 844
        self.page.window_resizable = True

    def _setup_navigation(self):
        """Set up navigation handlers"""
        def route_change(e):
            """Handle route changes"""
            route = e.route if hasattr(e, 'route') else str(e)
            self.current_route = route
            
            # Check authentication for protected routes
            if self._is_protected_route(route) and not self.is_authenticated:
                self.page.go("/login")
                return
            
            self._update_bottom_nav()
            self._build_main_view()
            self.page.update()

        def view_pop(view):
            """Handle view pop for back navigation"""
            self.page.views.pop()
            top_view = self.page.views[-1]
            self.page.go(top_view.route)

        self.page.on_route_change = route_change
        self.page.on_view_pop = view_pop

    def _is_protected_route(self, route: str) -> bool:
        """Check if route requires authentication"""
        protected_routes = ["/", "/dashboard", "/appointments", "/clients", "/profile"]
        return route in protected_routes or any(route.startswith(protected_route + "/") for protected_route in protected_routes)

    def _check_authentication(self):
        """Check if user is already authenticated"""
        try:
            stored_token = self.page.client_storage.get("auth_token")
            stored_user = self.page.client_storage.get("user_data")
            
            if stored_token and stored_user:
                self.auth_token = stored_token
                self.user_data = stored_user
                self.is_authenticated = True
                self.api_client.set_auth_token(stored_token)
                
                # Update profile view with token
                self.profile_view.auth_token = stored_token
                
                # Load profile data
                self.page.run_task(self.profile_view.load_profile)
                
                # Go to dashboard if at root
                if self.current_route == "/":
                    self.page.go("/dashboard")
            else:
                # Not authenticated, go to login
                self.page.go("/login")
                
        except Exception as e:
            print(f"Error checking authentication: {e}")
            self.page.go("/login")

    def _on_login_success(self, auth_data: dict):
        """Handle successful login"""
        try:
            self.auth_token = auth_data.get("access")  # Changed from "access_token"
            self.user_data = auth_data.get("user", {})
            self.is_authenticated = True
            
            # Store authentication data
            self.page.client_storage.set("auth_token", self.auth_token)
            self.page.client_storage.set("user_data", self.user_data)
            
            # Set token in API client
            self.api_client.set_auth_token(self.auth_token)
            
            # Update profile view
            self.profile_view.auth_token = self.auth_token
            
            # Navigate to dashboard
            self.page.go("/dashboard")
            
        except Exception as e:
            print(f"Error handling login success: {e}")
            import traceback
            traceback.print_exc()
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Login error: {str(e)}"),
                bgcolor=ft.colors.RED_600
            )
            self.page.snack_bar.open = True
            self.page.update()

    def _update_bottom_nav(self):
        """Update bottom navigation based on current route"""
        if self.current_route == "/" or self.current_route == "/dashboard":    
            self.bottom_nav_index = 0
        elif self.current_route == "/appointments":
            self.bottom_nav_index = 1
        elif self.current_route == "/clients":
            self.bottom_nav_index = 2
        else:
            self.bottom_nav_index = 0

    def _build_main_view(self):
        """Build the main view based on current route"""
        # Clear existing content
        self.page.clean()
        
        # Build content based on route
        if self.current_route == "/login":
            main_content = self.login_view.build()
        elif self.current_route == "/" or self.current_route == "/dashboard":
            main_content = self.dashboard_view.build()
        elif self.current_route == "/appointments":
            main_content = self.appointments_view.build()
        elif self.current_route == "/clients":
            main_content = self.clients_view.build()
        elif self.current_route == "/profile":
            main_content = self.profile_view.build()
        else:
            # 404 page
            main_content = ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(
                                    ft.Icons.ERROR_OUTLINE,
                                    color=GRAY_400,
                                    size=64,
                                ),
                                ft.Text(
                                    "Page Not Found",
                                    size=18,
                                    weight=ft.FontWeight.W_500,
                                    color=GRAY_700,
                                ),
                                ft.Text(
                                    "The page you're looking for doesn't exist.",
                                    size=14,
                                    color=GRAY_500,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=16,
                        ),
                        padding=ft.padding.all(32),
                        expand=True,
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )

        # Build main container
        if self.current_route == "/login":
            # Login page - no bottom navigation
            main_container = main_content
        else:
            # Authenticated pages with bottom navigation
            main_container = ft.Column(
                controls=[
                    # Main content area
                    ft.Container(
                        content=main_content,
                        expand=True,
                    ),
                    # Bottom navigation
                    self._build_bottom_navigation(),
                ],
                expand=True,
            )

        self.page.add(main_container)

    def _build_bottom_navigation(self) -> ft.Container:
        """Build bottom navigation bar"""
        return ft.Container(
            content=ft.Row(
                controls=[
                    self._nav_item(
                        "Dashboard",
                        ft.Icons.DASHBOARD_OUTLINED,
                        ft.Icons.DASHBOARD,
                        0,
                        "/dashboard",
                    ),
                    self._nav_item(
                        "Appointments",
                        ft.Icons.CALENDAR_MONTH_OUTLINED,
                        ft.Icons.CALENDAR_MONTH,
                        1,
                        "/appointments",
                    ),
                    self._nav_item(
                        "Clients",
                        ft.Icons.PEOPLE_OUTLINED,
                        ft.Icons.PEOPLE,
                        2,
                        "/clients",
                    ),
                    self._nav_item(
                        "Profile",
                        ft.Icons.PERSON_OUTLINED,
                        ft.Icons.PERSON,
                        3,
                        "/profile",
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            bgcolor=WHITE,
            border=ft.border.only(top=ft.BorderSide(1, GRAY_200)),
        )

    def _nav_item(self, label: str, outlined_icon, filled_icon, index: int, route: str):
        """Build navigation item"""
        is_selected = self.bottom_nav_index == index

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        filled_icon if is_selected else outlined_icon,
                        color=BLUE_600 if is_selected else GRAY_500,
                        size=24,
                    ),
                    ft.Text(
                        label,
                        size=10,
                        weight=ft.FontWeight.W_500 if is_selected else ft.FontWeight.NORMAL,
                        color=BLUE_600 if is_selected else GRAY_500,
                    ),
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            on_click=lambda e: self.page.go(route),
        )

    async def _load_initial_data(self):
        """Load initial data for all views"""
        try:
            # Load data for all views in parallel
            await asyncio.gather(
                self.dashboard_view.load_data(),
                self.appointments_view.load_data(),
                self.clients_view.load_data(),
                return_exceptions=True
            )
        except Exception as e:
            print(f"Error loading initial data: {e}")

    def logout(self):
        """Handle logout"""
        self.auth_token = None
        self.user_data = None
        self.is_authenticated = False
        
        # Clear stored data
        self.page.client_storage.clear()
        
        # Clear API client token
        self.api_client.set_auth_token(None)
        
        # Go to login
        self.page.go("/login")

def main(page: ft.Page):
    """Main entry point for the Lawyer Office Mobile App"""
    app = LawyerOfficeMobileApp(page)

    # Set initial route - will be redirected based on auth state
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main)
