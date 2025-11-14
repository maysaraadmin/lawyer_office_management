import flet as ft
from ..services.api_client import api_client
from .base_page import BasePage

class ClientsPage(BasePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.page.title = "Clients - Lawyer Office Management"
        self.clients = []
        self.client_list = ft.ListView(expand=True, spacing=10, padding=20)
        self.search_field = ft.TextField(
            label="Search clients...",
            prefix_icon="search",
            on_submit=self.search_clients,
            expand=True
        )
    
    async def initialize(self):
        """Initialize the clients page"""
        if not await self.check_auth():
            return
            
        self.setup_app_bar()
        self.setup_drawer()
        self.show_loading("Loading clients...")
        
        try:
            await self.load_clients()
            await self.build_ui()
        except Exception as e:
            await self.handle_error(e, "Failed to load clients")
    
    async def load_clients(self, search_query: str = None):
        """Load clients from the API"""
        try:
            params = {}
            if search_query:
                params["search"] = search_query
                
            response = await api_client.get("clients/", params=params)
            self.clients = response.get("results", [])
            
        except Exception as e:
            await self.handle_error(e, "Failed to load clients")
            self.clients = []
    
    async def search_clients(self, e):
        """Search for clients"""
        query = self.search_field.value.strip()
        await self.load_clients(query)
        await self.build_ui()
    
    async def build_ui(self):
        """Build the UI components"""
        # Clear existing content
        self.page.clean()
        
        # Rebuild app bar and drawer
        self.setup_app_bar()
        self.setup_drawer()
        
        # Create header
        header = ft.Row(
            [
                ft.Text("Clients", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.ElevatedButton(
                    "Add New Client",
                    icon="person_add",
                    on_click=self.add_new_client,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # Build client list
        self.client_list.controls = []
        if not self.clients:
            self.client_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon("people_alt", size=48),
                            ft.Text("No clients found"),
                            ft.ElevatedButton(
                                "Add New Client",
                                on_click=self.add_new_client,
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=16,
                    ),
                    padding=40,
                    alignment=ft.alignment.center,
                )
            )
        else:
            for client in self.clients:
                self.client_list.controls.append(
                    self._build_client_card(client)
                )
        
        # Build the main content
        content = ft.Column(
            [
                header,
                ft.Row(
                    [
                        self.search_field,
                        ft.IconButton(
                            icon="filter_list",
                            tooltip="Filter clients",
                            on_click=self.show_filters,
                        ),
                    ],
                    spacing=10,
                ),
                ft.Divider(),
                self.client_list,
            ],
            expand=True,
            spacing=20,
        )
        
        # Add content to page
        self.page.add(content)
        self.page.update()
    
    def _build_client_card(self, client: dict) -> ft.Card:
        """Build a client card"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon("person"),
                            title=ft.Text(f"{client.get('first_name', '')} {client.get('last_name', '')}"),
                            subtitle=ft.Text(client.get('email', '')),
                            trailing=ft.PopupMenuButton(
                                icon="more_vert",
                                items=[
                                    ft.PopupMenuItem(
                                        text="View Details",
                                        on_click=lambda _: self.view_client_details(client['id'])
                                    ),
                                    ft.PopupMenuItem(
                                        text="Edit",
                                        on_click=lambda _: self.edit_client(client['id'])
                                    ),
                                ],
                            ),
                        ),
                        ft.Row(
                            [
                                ft.Text(f"Phone: {client.get('phone', 'N/A')}", size=12),
                                ft.Text(f"Cases: {client.get('case_count', 0)}", size=12),
                            ],
                            spacing=20,
                        ),
                    ],
                    spacing=0,
                ),
                padding=10,
                on_click=lambda _: self.view_client_details(client['id']),
            )
        )
    
    async def view_client_details(self, client_id: str):
        """View details of a specific client"""
        self.page.go(f"/clients/{client_id}")
    
    async def edit_client(self, client_id: str):
        """Edit a client"""
        self.page.go(f"/clients/{client_id}/edit")
    
    async def add_new_client(self, _=None):
        """Navigate to add new client page"""
        self.page.go("/clients/new")
    
    async def show_filters(self, _):
        """Show filter dialog"""
        # TODO: Implement filter dialog
        self.show_snackbar("Filter functionality coming soon!")

async def clients_page(page: ft.Page):
    """Create and initialize the clients page"""
    clients = ClientsPage(page)
    await clients.initialize()
    return clients
