import flet as ft
import sys
import os
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the main app class
from src.app import LawyerOfficeApp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LawyerOfficeApp:
    """Main application class for Lawyer Office Management"""
    
    def __init__(self, page: Page):
        self.page = page
        self.config = AppConfig()
        
        # Configure page
        self.page.title = self.config.APP_NAME
        self.page.theme_mode = ThemeMode.LIGHT if self.config.APP_THEME == 'light' else ThemeMode.DARK
        self.page.theme = Theme(
            color_scheme_seed=self.config.COLORS['primary'],
            color_scheme=ft.ColorScheme(
                primary=self.config.COLORS['primary'],
                secondary=self.config.COLORS['secondary'],
                surface=self.config.COLORS['surface'],
                background=self.config.COLORS['background'],
                error=self.config.COLORS['error'],
                on_primary=self.config.COLORS['on_primary'],
                on_secondary=self.config.COLORS['on_secondary'],
                on_surface=self.config.COLORS['on_surface'],
            )
        )
        
        # Set window properties
        self.page.window_width = 1280
        self.page.window_height = 800
        self.page.window_min_width = 1024
        self.page.window_min_height = 768
        self.page.window_resizable = True
        self.page.window_maximized = True
        
        # State
        self.current_user = None
        self.routes = {}
        self.drawer_items = []
        self._loading = False
        
        # Initialize views
        self.views: Dict[str, Type[ft.View]] = {
            '/login': LoginView(self),
            '/dashboard': DashboardView(self),
            '/cases': CasesView(self),
            '/clients': ClientsView(self),
            '/appointments': AppointmentsView(self),
            '/billing': BillingView(self),
            '/profile': ProfileView(self),
        }
        
        # Set up routing
        self.setup_routes()
        
        # Handle route changes
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop
        
        # Initialize the app
        self.initialize()
    
    def setup_routes(self):
        """Set up application routes"""
        self.routes = {
            '/': '/dashboard',
            '/login': self.views['/login'].view,
            '/dashboard': self.views['/dashboard'].view,
            '/cases': self.views['/cases'].view,
            '/clients': self.views['/clients'].view,
            '/appointments': self.views['/appointments'].view,
            '/billing': self.views['/billing'].view,
            '/profile': self.views['/profile'].view,
        }
        
        # Set up drawer items
        self.drawer_items = [
            {'route': '/dashboard', 'icon': icons.DASHBOARD, 'label': 'Dashboard'},
            {'route': '/appointments', 'icon': icons.CALENDAR_TODAY, 'label': 'Appointments'},
            {'route': '/cases', 'icon': icons.CASE, 'label': 'Cases'},
            {'route': '/clients', 'icon': icons.PEOPLE, 'label': 'Clients'},
            {'route': '/billing', 'icon': icons.ATTACH_MONEY, 'label': 'Billing'},
            {'divider': True},
            {'route': '/profile', 'icon': icons.PERSON, 'label': 'Profile'},
            {'route': '/logout', 'icon': icons.LOGOUT, 'label': 'Logout'},
        ]
    
    async def initialize(self):
        """Initialize the application"""
        # Check if user is already authenticated
        if auth_service.is_authenticated():
            self.current_user = auth_service.get_user_info()
            await self.go_to('/dashboard')
        else:
            await self.go_to('/login')
        
        # Update the page
        await self.page.update_async()
    
    async def route_change(self, route):
        """Handle route changes"""
        # Ensure user is authenticated for protected routes
        if not auth_service.is_authenticated() and route.route != '/login':
            await self.go_to('/login')
            return
        
        # Handle logout
        if route.route == '/logout':
            await self.logout()
            return
        
        # Get the view for the route
        view = self.routes.get(route.route)
        
        if view is None:
            # Try to find a matching route with parameters
            for route_pattern, view_func in self.routes.items():
                if route_pattern != '/' and route.route.startswith(route_pattern):
                    view = view_func
                    break
            else:
                # Route not found, go to dashboard
                await self.go_to('/dashboard')
                return
        
        # Handle redirects
        if isinstance(view, str):
            await self.go_to(view)
            return
        
        # Update the view
        self.page.views.clear()
        
        # Create the view with app bar and navigation
        if route.route != '/login':
            # Main layout with app bar and navigation
            app_bar = self._create_app_bar()
            navigation_rail = self._create_navigation_rail(route.route)
            
            main_view = View(
                route.route,
                [
                    Row(
                        [
                            # Navigation rail
                            navigation_rail,
                            # Main content
                            ft.VerticalDivider(width=1),
                            ft.Container(
                                content=view,
                                expand=True,
                                padding=20,
                            ),
                        ],
                        expand=True,
                    )
                ],
                appbar=app_bar,
            )
            
            self.page.views.append(main_view)
        else:
            # Login view (no app bar or navigation)
            self.page.views.append(View(route.route, [view]))
        
        await self.page.update_async()
    
    async def view_pop(self, view):
        """Handle view pop (back button)"""
        self.page.views.pop()
        top_view = self.page.views[-1]
        await self.page.go_async(top_view.route)
    
    def _create_app_bar(self) -> AppBar:
        """Create the app bar"""
        return AppBar(
            title=ft.Text(Config.APP_NAME, style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            center_title=False,
            bgcolor=Config.COLORS['primary'],
            actions=[
                # User menu
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            content=ft.Row(
                                [
                                    ft.Icon(icons.PERSON),
                                    ft.Text("Profile"),
                                ],
                                spacing=10,
                            ),
                            on_click=lambda _: self.go_to('/profile'),
                        ),
                        ft.PopupMenuItem(
                            content=ft.Row(
                                [
                                    ft.Icon(icons.SETTINGS),
                                    ft.Text("Settings"),
                                ],
                                spacing=10,
                            ),
                            on_click=lambda _: print("Settings clicked"),
                        ),
                        ft.PopupMenuItem(),  # Divider
                        ft.PopupMenuItem(
                            content=ft.Row(
                                [
                                    ft.Icon(icons.LOGOUT),
                                    ft.Text("Logout"),
                                ],
                                spacing=10,
                            ),
                            on_click=lambda _: self.logout(),
                        ),
                    ],
                    icon=ft.Icon(icons.ACCOUNT_CIRCLE, size=32),
                    tooltip="Account",
                ),
            ],
        )
    
    def _create_navigation_rail(self, current_route: str) -> ft.NavigationRail:
        """Create the navigation rail"""
        rail = ft.NavigationRail(
            selected_index=self._get_selected_index(current_route),
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            leading=ft.FloatingActionButton(
                icon=ft.icons.ADD,
                text="New",
                on_click=self._handle_new_button_click,
                mini=True,
            ),
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=item['icon'],
                    selected_icon=item['icon'],
                    label=item['label'],
                )
                for item in self.drawer_items 
                if not item.get('divider', False) and item['route'] != '/logout' and item['route'] != '/profile'
            ],
            on_change=self._handle_navigation_rail_change,
        )
        
        return rail
    
    def _get_selected_index(self, route: str) -> int:
        """Get the selected index for the navigation rail"""
        for i, item in enumerate(self.drawer_items):
            if not item.get('divider', False) and item['route'] == route:
                return i
        return 0
    
    async def _handle_navigation_rail_change(self, e):
        """Handle navigation rail selection change"""
        selected_index = e.control.selected_index
        route_index = 0
        
        # Find the corresponding route for the selected index
        for i, item in enumerate(self.drawer_items):
            if item.get('divider', False):
                continue
            
            if route_index == selected_index:
                await self.go_to(item['route'])
                return
            
            route_index += 1
    
    async def _handle_new_button_click(self, e):
        """Handle new button click in navigation rail"""
        # Get the current route
        current_route = self.page.route
        
        # Determine the appropriate action based on the current route
        if current_route.startswith('/cases'):
            await self.views['/cases'].create_new_case()
        elif current_route.startswith('/clients'):
            await self.views['/clients'].create_new_client()
        elif current_route.startswith('/appointments'):
            await self.views['/appointments'].create_new_appointment()
        elif current_route.startswith('/billing'):
            await self.views['/billing'].create_new_invoice()
    
    async def go_to(self, route: str):
        """Navigate to a route"""
        await self.page.go_async(route)
    
    async def show_snackbar(self, message: str, color: str = None):
        """Show a snackbar message"""
        if color is None:
            color = Config.COLORS['success']
        
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
        )
        self.page.snack_bar.open = True
        await self.page.update_async()
    
    async def show_loading(self, message: str = "Loading..."):
        """Show a loading dialog"""
        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please wait"),
            content=ft.Column(
                [
                    ft.ProgressRing(),
                    ft.Text(message),
                ],
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        self.page.dialog.open = True
        await self.page.update_async()
    
    async def hide_loading(self):
        """Hide the loading dialog"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.dialog = None
            await self.page.update_async()
    
    async def show_alert(self, title: str, message: str, on_confirm=None):
        """Show an alert dialog"""
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
            if on_confirm:
                asyncio.create_task(on_confirm())
        
        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        await self.page.update_async()
    
    async def show_confirm_dialog(
        self, 
        title: str, 
        message: str, 
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        on_confirm: Callable = None,
        on_cancel: Callable = None,
    ):
        """Show a confirmation dialog"""
        def close_dialog(confirmed: bool):
            self.page.dialog.open = False
            self.page.update()
            
            if confirmed and on_confirm:
                asyncio.create_task(on_confirm())
            elif not confirmed and on_cancel:
                asyncio.create_task(on_cancel())
        
        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton(
                    cancel_text,
                    on_click=lambda _: close_dialog(False),
                ),
                ft.ElevatedButton(
                    confirm_text,
                    on_click=lambda _: close_dialog(True),
                    style=ft.ButtonStyle(
                        bgcolor=Config.COLORS['error'],
                        color=ft.colors.WHITE,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        await self.page.update_async()
    
    async def logout(self):
        """Logout the current user"""
        auth_service.logout()
        self.current_user = None
        await self.go_to('/login')
        await self.show_snackbar("You have been logged out")


async def main(page: ft.Page):
    """Main entry point for the application"""
    try:
        # Initialize the app
        app = LawyerOfficeApp(page)
        
        # Set up event handlers
        page.on_route_change = app.route_change
        page.on_view_pop = app.view_pop
        
        # Check authentication and redirect
        if await auth_service.is_authenticated():
            page.go('/dashboard')
        else:
            page.go('/login')
    except Exception as e:
        print(f"An error occurred: {e}")
        # If the page is already initialized, show an error message
        if hasattr(page, 'show_snackbar'):
            await page.show_snackbar(f"An error occurred: {str(e)}")
        else:
            # If we can't show a snackbar, print to console
            print("Failed to initialize the application:", str(e))

if __name__ == "__main__":
    # Start the application
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        port=8503,
        host="127.0.0.1",
        assets_dir="assets",
        upload_dir="uploads",
        web_renderer="html",
    )
