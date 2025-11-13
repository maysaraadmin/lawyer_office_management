import flet as ft
from flet import (
    Page, View, AppBar, Text, colors, Theme, ThemeMode,
    CrossAxisAlignment, MainAxisAlignment, IconButton, icons
)
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import pages
from pages.dashboard import DashboardPage
from pages.cases import CasesPage
from pages.appointments import AppointmentsPage
from pages.documents import DocumentsPage
from pages.auth import LoginPage

# Import services
from services.auth_service import AuthService
from services.api_client import APIClient

class LawyerOfficeApp:
    def __init__(self, page: Page):
        self.page = page
        self.page.title = "Lawyer Office Management"
        self.page.theme_mode = ThemeMode.LIGHT
        self.page.padding = 0
        self.page.window_width = 1280
        self.page.window_height = 800
        self.page.window_resizable = True
        
        # Initialize services
        self.api_client = APIClient()
        self.auth_service = AuthService(self.api_client)
        
        # Set up theme
        self._setup_theme()
        
        # Initialize pages
        self.pages = {
            "/login": LoginPage(self),
            "/dashboard": DashboardPage(self),
            "/cases": CasesPage(self),
            "/appointments": AppointmentsPage(self),
            "/documents": DocumentsPage(self),
        }
        
        # Set up navigation
        self.current_page = None
        
        # Check authentication state
        self.page.on_route_change = self._on_route_change
        self.page.on_view_pop = self._on_view_pop
        
        # Initial route
        self.page.go("/login" if not self.auth_service.is_authenticated() else "/dashboard")
    
    def _setup_theme(self):
        """Configure the app's theme"""
        self.page.theme = Theme(
            color_scheme_seed=colors.BLUE,
            visual_density=ft.ThemeVisualDensity.COMFORTABLE,
        )
        
        # Custom theme overrides
        self.page.theme.page_transitions.windows = "cupertino"
        self.page.theme.page_transitions.macos = "cupertino"
        self.page.theme.page_transitions.linux = "cupertino"
        self.page.theme.page_transitions.android = "cupertino"
        self.page.theme.page_transitions.ios = "cupertino"
    
    async def _on_route_change(self, route):
        """Handle route changes"""
        # Check authentication for protected routes
        protected_routes = ["/dashboard", "/cases", "/appointments", "/documents"]
        if route.route in protected_routes and not self.auth_service.is_authenticated():
            self.page.go("/login")
            return
        
        # Handle login redirect
        if route.route == "/login" and self.auth_service.is_authenticated():
            self.page.go("/dashboard")
            return
        
        # Get the page or show 404
        page = self.pages.get(route.route, None)
        
        if not page:
            self._show_404()
            return
        
        # Initialize the page if it hasn't been loaded yet
        if not hasattr(page, 'is_initialized') or not page.is_initialized:
            await page.initialize()
            page.is_initialized = True
        
        # Update the view
        self.page.views.clear()
        self.page.views.append(page.get_view())
        self.current_page = page
        self.page.update()
    
    def _on_view_pop(self, view):
        """Handle back button press"""
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)
    
    def _show_404(self):
        """Show 404 page not found"""
        self.page.views.clear()
        self.page.views.append(
            View(
                "/404",
                [
                    AppBar(title=Text("404 - Page Not Found"), bgcolor=colors.SURFACE_VARIANT),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(icons.ERROR_OUTLINE, size=64, color=colors.RED_400),
                                ft.Text("The page you're looking for doesn't exist.", size=20),
                                ft.ElevatedButton(
                                    "Go to Dashboard",
                                    on_click=lambda _: self.page.go("/dashboard"),
                                ),
                            ],
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.CENTER,
                            expand=True,
                        ),
                        expand=True,
                    ),
                ],
                padding=20,
            )
        )
        self.page.update()

def main(page: Page):
    """Entry point for the Flet app"""
    # Initialize the app
    app = LawyerOfficeApp(page)
    
    # Run the app
    page.update()

if __name__ == "__main__":
    # Run the app
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,  # Use ft.AppView.FLET_APP for mobile
        port=8501,  # Default port for the web app
        assets_dir="assets",
    )
