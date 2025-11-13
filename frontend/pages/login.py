import flet as ft
from ..services.api_client import auth_service
from ..views.login_view import LoginView

class LoginPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.login_view = LoginView(self)
        
    def initialize(self):
        """Initialize the login page"""
        self.page.clean()
        self.page.add(self.login_view.view)
        self.page.update()
    
    async def on_login_success(self):
        """Handle successful login"""
        from .dashboard import DashboardPage
        dashboard = DashboardPage(self.page)
        await dashboard.initialize()
    
    def show_snackbar(self, message: str, color: str = None):
        """Show a snackbar message"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color or ft.colors.BLUE,
        )
        self.page.snack_bar.open = True
        self.page.update()

async def login_page(page: ft.Page):
    """Create and initialize the login page"""
    login = LoginPage(page)
    await login.initialize()
    return login
