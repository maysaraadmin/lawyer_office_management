import flet as ft
from typing import List, Dict, Any, Optional
import asyncio

# Import base view
from .base_view import BaseView

class ClientsView(BaseView):
    """View for managing clients"""
    
    def __init__(self, app):
        super().__init__(app)
        self.clients = []
        self.is_loading = True
        self.error = None
    
    async def initialize(self):
        """Initialize the clients data"""
        await self.load_clients()
    
    async def load_clients(self):
        """Load clients from the API"""
        self.is_loading = True
        self.error = None
        
        try:
            # Get clients from the API
            response = await self.app.api_client.get('clients/')
            self.clients = response.get('results', [])
        except Exception as e:
            logger.error(f"Error loading clients: {str(e)}")
            self.error = str(e)
        finally:
            self.is_loading = False
            await self.page.update_async()
    
    def build(self) -> ft.Container:
        """Build the clients view"""
        if self.is_loading:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.ProgressRing(),
                        ft.Text("Loading clients..."),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
        
        if self.error:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            "ERROR_OUTLINE",
                            size=48,
                            color="#F44336",  # Red
                        ),
                        ft.Text(
                            "Error loading clients",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="#F44336",  # Red
                        ),
                        ft.Text(
                            self.error,
                            size=14,
                            color="#757575",  # Grey 600
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.ElevatedButton(
                            "Retry",
                            on_click=lambda _: self.initialize(),
                            icon="REFRESH",
                            style=ft.ButtonStyle(
                                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                            ),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=16,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
        
        # Build clients list
        clients_list = ft.ListView(expand=True)
        
        if not self.clients:
            clients_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                "PEOPLE",
                                size=48,
                                color="#9E9E9E",  # Grey 500
                            ),
                            ft.Text(
                                "No clients found",
                                size=16,
                                color="#757575",  # Grey 600
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                "You don't have any clients yet.",
                                size=14,
                                color="#9E9E9E",  # Grey 500
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    padding=40,
                    alignment=ft.alignment.center,
                )
            )
        else:
            for client in self.clients:
                clients_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon("PERSON", size=24),
                                    padding=12,
                                    bgcolor="#E3F2FD",  # Light blue
                                    border_radius=12,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            f"{client.get('first_name', '')} {client.get('last_name', '')}".strip() or "Unnamed Client",
                                            weight=ft.FontWeight.W_500,
                                        ),
                                        ft.Text(
                                            client.get('email', 'No email'),
                                            size=12,
                                            color="#757575",  # Grey 600
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.IconButton(
                                    icon="EDIT",
                                    on_click=lambda e, c=client: self.edit_client(c),
                                    tooltip="Edit client",
                                ),
                            ],
                            spacing=16,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        border=ft.border.only(bottom=ft.border.BorderSide(1, "#E0E0E0")),  # Grey 300
                        on_click=lambda e, c=client: self.view_client(c),
                    )
                )
        
        return ft.Container(
            content=ft.Column(
                [
                    # Header
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(
                                    "Clients",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Container(expand=True),
                                ft.ElevatedButton(
                                    "Add Client",
                                    on_click=lambda _: self.add_client(),
                                    icon="ADD",
                                    style=ft.ButtonStyle(
                                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.only(bottom=24),
                    ),
                    
                    # Search and filter
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.TextField(
                                    label="Search clients",
                                    prefix_icon="SEARCH",
                                    on_change=self.on_search,
                                    expand=True,
                                ),
                                ft.PopupMenuButton(
                                    icon=ft.Icon("FILTER_LIST"),
                                    tooltip="Filter",
                                    items=[
                                        ft.PopupMenuItem(
                                            text="All Clients",
                                            on_click=lambda _: self.apply_filter("all"),
                                        ),
                                        ft.PopupMenuItem(
                                            text="Active",
                                            on_click=lambda _: self.apply_filter("active"),
                                        ),
                                        ft.PopupMenuItem(
                                            text="Inactive",
                                            on_click=lambda _: self.apply_filter("inactive"),
                                        ),
                                    ],
                                ),
                            ],
                            spacing=8,
                        ),
                        padding=ft.padding.only(bottom=16),
                    ),
                    
                    # Clients list
                    ft.Container(
                        content=clients_list,
                        border=ft.border.all(1, "#E0E0E0"),  # Grey 300
                        border_radius=8,
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            padding=16,
            expand=True,
        )
    
    async def on_search(self, e):
        """Handle search input change"""
        search_term = e.control.value.lower()
        # In a real app, we would filter the clients list here
        # For now, we'll just log the search term
        print(f"Searching for: {search_term}")
        await self.page.update_async()
    
    async def apply_filter(self, filter_type):
        """Apply filter to clients list"""
        # In a real app, we would filter the clients list here
        # For now, we'll just log the filter type
        print(f"Applying filter: {filter_type}")
        await self.page.update_async()
    
    async def add_client(self):
        """Navigate to add client form"""
        await self.go_to("/clients/new")
    
    async def view_client(self, client):
        """Navigate to client details"""
        await self.go_to(f"/clients/{client.get('id')}")
    
    async def edit_client(self, client):
        """Navigate to edit client form"""
        await self.go_to(f"/clients/{client.get('id')}/edit")
