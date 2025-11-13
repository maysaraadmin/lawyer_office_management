import flet as ft
from ..services.api_client import auth_service
from ..views.dashboard_view import DashboardView
from .base_page import BasePage

class DashboardPage(BasePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.dashboard_view = DashboardView(self)
        self.page.title = "Dashboard - Lawyer Office Management"
        
    async def initialize(self):
        """Initialize the dashboard page"""
        if not await self.check_auth():
            return
            
        self.page.clean()
        self.setup_app_bar()
        self.setup_drawer()
        
        # Add loading indicator
        loading = ft.ProgressRing()
        self.page.add(loading)
        self.page.update()
        
        # Initialize the dashboard view
        await self.dashboard_view.initialize()
        
        # Replace loading with dashboard content
        self.page.clean()
        self.setup_app_bar()
        self.setup_drawer()
        self.page.add(self.dashboard_view.view)
        self.page.update()
    
    def setup_app_bar(self):
        """Setup the app bar with user menu"""
        self.page.appbar = ft.AppBar(
            title=ft.Text("Dashboard"),
            center_title=False,
            bgcolor=ft.colors.BLUE_700,
            color=ft.colors.WHITE,
            actions=[
                ft.IconButton(
                    icon=ft.icons.NOTIFICATIONS,
                    icon_color=ft.colors.WHITE,
                    tooltip="Notifications"
                ),
                ft.PopupMenuButton(
                    icon=ft.icons.PERSON,
                    icon_color=ft.colors.WHITE,
                    tooltip="User Menu",
                    items=[
                        ft.PopupMenuItem(
                            text="Profile",
                            icon=ft.icons.ACCOUNT_CIRCLE,
                            on_click=lambda _: self.navigate_to("/profile")
                        ),
                        ft.PopupMenuItem(),  # Divider
                        ft.PopupMenuItem(
                            text="Logout",
                            icon=ft.icons.LOGOUT,
                            on_click=self.logout
                        )
                    ]
                )
            ]
        )
    
    def setup_drawer(self):
        """Setup the navigation drawer"""
        self.page.drawer = ft.NavigationDrawer(
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.DrawerHeader(
                                title=ft.Text("Lawyer Office"),
                                subtitle=ft.Text("Management System"),
                            ),
                            ft.NavigationDrawerDestination(
                                label="Dashboard",
                                icon=ft.icons.DASHBOARD,
                                selected_icon=ft.icons.DASHBOARD_OUTLINED,
                                selected=True
                            ),
                            ft.Divider(),
                            ft.NavigationDrawerDestination(
                                label="Cases",
                                icon=ft.icons.CASES,
                                selected_icon=ft.icons.CASES_OUTLINED,
                            ),
                            ft.NavigationDrawerDestination(
                                label="Clients",
                                icon=ft.icons.PEOPLE,
                                selected_icon=ft.icons.PEOPLE_OUTLINE,
                            ),
                            ft.NavigationDrawerDestination(
                                label="Appointments",
                                icon=ft.icons.CALENDAR_TODAY,
                                selected_icon=ft.icons.CALENDAR_TODAY_OUTLINED,
                            ),
                            ft.NavigationDrawerDestination(
                                label="Billing",
                                icon=ft.icons.PAYMENT,
                                selected_icon=ft.icons.PAYMENT_OUTLINED,
                            ),
                        ],
                        spacing=0,
                    ),
                    padding=ft.padding.all(8),
                )
            ],
            selected_index=0,
            on_change=self.on_drawer_change,
        )
    
    def on_drawer_change(self, e):
        """Handle navigation drawer item selection"""
        routes = {
            0: "/dashboard",
            2: "/cases",
            3: "/clients",
            4: "/appointments",
            5: "/billing",
        }
        
        selected_route = routes.get(e.control.selected_index)
        if selected_route:
            self.navigate_to(selected_route)
    
    async def logout(self, _=None):
        """Handle user logout"""
        auth_service.logout()
        from .login import LoginPage
        login_page = LoginPage(self.page)
        await login_page.initialize()

async def dashboard_page(page: ft.Page):
    """Create and initialize the dashboard page"""
    dashboard = DashboardPage(page)
    await dashboard.initialize()
    return dashboard
