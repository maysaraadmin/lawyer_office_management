import flet as ft
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio

# Color constants matching Django design
WHITE = "#FFFFFF"
GRAY_50 = "#F9FAFB"
GRAY_100 = "#F3F4F6"
GRAY_200 = "#E5E7EB"
GRAY_300 = "#D1D5DB"
GRAY_400 = "#9CA3AF"
GRAY_500 = "#6B7280"
GRAY_600 = "#4B5563"
GRAY_700 = "#374151"
GRAY_800 = "#1F2937"
GRAY_900 = "#111827"
BLUE_50 = "#EFF6FF"
BLUE_100 = "#DBEAFE"
BLUE_200 = "#BFDBFE"
BLUE_300 = "#93C5FD"
BLUE_400 = "#60A5FA"
BLUE_500 = "#3B82F6"
BLUE_600 = "#2563EB"
GREEN_50 = "#F0FDF4"
GREEN_100 = "#DCFCE7"
GREEN_200 = "#BBF7D0"
GREEN_300 = "#86EFAC"
GREEN_400 = "#4ADE80"
GREEN_500 = "#22C55E"
GREEN_600 = "#059669"
YELLOW_50 = "#FFFBEB"
YELLOW_100 = "#FEF3C7"
YELLOW_200 = "#FDE68A"
YELLOW_300 = "#FCD34D"
YELLOW_400 = "#FBBF24"
YELLOW_500 = "#F59E0B"
YELLOW_600 = "#D97706"
RED_50 = "#FEF2F2"
RED_100 = "#FEE2E2"
RED_200 = "#FECACA"
RED_300 = "#FCA5A5"
RED_400 = "#F87171"
RED_500 = "#EF4444"
RED_600 = "#DC2626"
PURPLE_50 = "#F5F3FF"
PURPLE_100 = "#EDE9FE"
PURPLE_200 = "#DDD6FE"
PURPLE_300 = "#C4B5FD"
PURPLE_400 = "#A78BFA"
PURPLE_500 = "#8B5CF6"
PURPLE_600 = "#7C3AED"

class MobileClientsView:
    """Mobile clients view matching Django web app design"""

    def __init__(self, page: ft.Page, api_client):
        self.page = page
        self.api_client = api_client
        self.loading = False
        self.error = None
        self.clients_data = []
        self.filtered_clients = []
        self.search_query = ""
        self.status_filter = "All"
        self.selected_client = None
        self.show_add_dialog = False
        
    def build(self) -> ft.Column:
        """Build the mobile clients view"""
        return ft.Column(
            controls=[
                self._build_header(),
                self._build_filters(),
                self._build_clients_list(),
                self._build_fab(),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
            expand=True,
        )
    
    def _build_header(self) -> ft.Container:
        """Build mobile header matching Django design"""
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Clients",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=GRAY_900,
                            ),
                            ft.Text(
                                f"{len(self.filtered_clients)} clients",
                                size=14,
                                color=GRAY_600,
                            ),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.SEARCH_OUTLINED,
                        icon_color=GRAY_600,
                        icon_size=24,
                        on_click=self._toggle_search,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.all(16),
            bgcolor=WHITE,
        )
    
    def _build_search_bar(self) -> ft.Container:
        """Build search bar"""
        return ft.Container(
            content=ft.TextField(
                hint_text="Search clients...",
                border_color=GRAY_300,
                focused_border_color=BLUE_600,
                text_size=14,
                prefix_icon=ft.Icons.SEARCH_OUTLINED,
                on_change=self._on_search_change,
                on_submit=self._perform_search,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            bgcolor=GRAY_50,
        )
    
    def _build_filters(self) -> ft.Container:
        """Build filters section matching Django design"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Status filter
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    "Status",
                                    size=14,
                                    weight=ft.FontWeight.W_500,
                                    color=GRAY_700,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.ElevatedButton(
                                            text="All",
                                            style=ft.ButtonStyle(
                                                bgcolor=BLUE_600 if self.status_filter == "All" else WHITE,
                                                color=WHITE if self.status_filter == "All" else GRAY_700,
                                                elevation=0,
                                                side=ft.border.all(1, BLUE_600 if self.status_filter == "All" else GRAY_300),
                                                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                            ),
                                            on_click=lambda _: self._set_status_filter("All"),
                                        ),
                                        ft.ElevatedButton(
                                            text="Active",
                                            style=ft.ButtonStyle(
                                                bgcolor=BLUE_600 if self.status_filter == "active" else WHITE,
                                                color=WHITE if self.status_filter == "active" else GRAY_700,
                                                elevation=0,
                                                side=ft.border.all(1, BLUE_600 if self.status_filter == "active" else GRAY_300),
                                                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                            ),
                                            on_click=lambda _: self._set_status_filter("active"),
                                        ),
                                        ft.ElevatedButton(
                                            text="Inactive",
                                            style=ft.ButtonStyle(
                                                bgcolor=BLUE_600 if self.status_filter == "inactive" else WHITE,
                                                color=WHITE if self.status_filter == "inactive" else GRAY_700,
                                                elevation=0,
                                                side=ft.border.all(1, BLUE_600 if self.status_filter == "inactive" else GRAY_300),
                                                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                            ),
                                            on_click=lambda _: self._set_status_filter("inactive"),
                                        ),
                                    ],
                                    spacing=8,
                                    scroll=ft.ScrollMode.AUTO,
                                ),
                            ],
                            spacing=8,
                        ),
                        padding=ft.padding.all(16),
                    ),
                ],
                spacing=0,
            ),
            bgcolor=WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, GRAY_200)),
        )
    
    def _build_clients_list(self) -> ft.Column:
        """Build clients list matching Django design"""
        if self.loading:
            return ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.ProgressRing(color=BLUE_600),
                                ft.Text("Loading clients...", color=GRAY_600),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=16,
                        ),
                        padding=ft.padding.all(32),
                        expand=True,
                    ),
                ],
                expand=True,
            )
        
        if not self.filtered_clients:
            return ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(
                                    ft.Icons.PEOPLE_OUTLINE,
                                    color=GRAY_400,
                                    size=64,
                                ),
                                ft.Text(
                                    "No clients found",
                                    size=18,
                                    weight=ft.FontWeight.W_500,
                                    color=GRAY_700,
                                ),
                                ft.Text(
                                    "Try adjusting your filters or add a new client",
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
                    ),
                ],
                expand=True,
            )
        
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            self._build_client_item(client)
                            for client in self.filtered_clients
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.all(16),
                    expand=True,
                ),
            ],
            expand=True,
        )
    
    def _build_client_item(self, client: Dict[str, Any]) -> ft.Container:
        """Build individual client item matching Django design"""
        name = client.get('name', 'Unknown Client')
        email = client.get('email', '')
        phone = client.get('phone', '')
        is_active = client.get('is_active', True)
        total_cases = client.get('total_cases', 0)
        active_cases = client.get('active_cases', 0)
        
        # Status colors
        status_color = GREEN_600 if is_active else RED_600
        status_bg_color = GREEN_50 if is_active else RED_50
        status_text = "Active" if is_active else "Inactive"

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            name[0].upper() if name else "?",
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                            color=WHITE,
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                width=48,
                                height=48,
                                bgcolor=BLUE_600,
                                border_radius=24,
                                alignment=ft.alignment.center,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text(
                                                name,
                                                size=16,
                                                weight=ft.FontWeight.W_500,
                                                color=GRAY_900,
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    status_text,
                                                    size=10,
                                                    weight=ft.FontWeight.W_500,
                                                    color=status_color,
                                                ),
                                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                                bgcolor=status_bg_color,
                                                border_radius=12,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    ft.Text(
                                        email,
                                        size=14,
                                        color=GRAY_600,
                                    ) if email else ft.Container(),
                                    ft.Text(
                                        phone,
                                        size=12,
                                        color=GRAY_500,
                                    ) if phone else ft.Container(),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Text(
                                                str(total_cases),
                                                size=16,
                                                weight=ft.FontWeight.BOLD,
                                                color=GRAY_900,
                                            ),
                                            ft.Text(
                                                "Total Cases",
                                                size=10,
                                                color=GRAY_600,
                                            ),
                                        ],
                                        spacing=2,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Text(
                                                str(active_cases),
                                                size=16,
                                                weight=ft.FontWeight.BOLD,
                                                color=GREEN_600,
                                            ),
                                            ft.Text(
                                                "Active Cases",
                                                size=10,
                                                color=GRAY_600,
                                            ),
                                        ],
                                        spacing=2,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    expand=True,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.MORE_VERT_OUTLINED,
                                    icon_color=GRAY_400,
                                    icon_size=20,
                                    on_click=lambda _, c=client: self._show_client_menu(c),
                                ),
                            ],
                            spacing=8,
                        ),
                        padding=ft.padding.only(top=8),
                    ),
                ],
                spacing=0,
            ),
            padding=ft.padding.all(16),
            border=ft.border.all(1, GRAY_200),
            border_radius=12,
            bgcolor=WHITE,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color="#00000010",
                offset=ft.Offset(0, 1),
            ),
            on_click=lambda _, c=client: self._view_client_details(c),
        )
    
    def _build_fab(self) -> ft.FloatingActionButton:
        """Build floating action button"""
        return ft.FloatingActionButton(
            icon=ft.Icons.ADD_OUTLINED,
            bgcolor=BLUE_600,
            on_click=self._add_client,
        )
    
    def _toggle_search(self, e):
        """Toggle search bar visibility"""
        # This would toggle search bar visibility
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text("Search functionality coming soon!"),
                bgcolor=BLUE_600,
            )
        )
    
    def _on_search_change(self, e):
        """Handle search input change"""
        self.search_query = e.control.value
        self._apply_filters()
    
    def _perform_search(self, e):
        """Perform search"""
        self._apply_filters()
    
    def _set_status_filter(self, status: str):
        """Set status filter"""
        self.status_filter = status
        self._apply_filters()
    
    def _apply_filters(self):
        """Apply all filters"""
        self.filtered_clients = []
        
        for client in self.clients_data:
            # Status filter
            if self.status_filter != "All":
                if self.status_filter == "active" and not client.get('is_active', True):
                    continue
                if self.status_filter == "inactive" and client.get('is_active', True):
                    continue
            
            # Search filter
            if self.search_query:
                search_lower = self.search_query.lower()
                name = client.get('name', '').lower()
                email = client.get('email', '').lower()
                phone = client.get('phone', '').lower()
                
                if (search_lower not in name and 
                    search_lower not in email and 
                    search_lower not in phone):
                    continue
            
            self.filtered_clients.append(client)
        
        self.page.update()
    
    def _view_client_details(self, client: Dict[str, Any]):
        """View client details"""
        self.selected_client = client
        # This would open a details dialog or navigate to details page
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(f"Viewing: {client.get('name', 'Unknown')}"),
                bgcolor=BLUE_600,
            )
        )
    
    def _show_client_menu(self, client: Dict[str, Any]):
        """Show client options menu"""
        self.selected_client = client
        # This would show a menu with options like Edit, Delete, View Cases
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(f"Options for: {client.get('name', 'Unknown')}"),
                bgcolor=BLUE_600,
            )
        )
    
    def _add_client(self, e):
        """Add new client"""
        self.show_add_dialog = True
        # This would open an add client dialog
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text("Add client form coming soon!"),
                bgcolor=BLUE_600,
            )
        )
    
    async def load_data(self):
        """Load clients data"""
        self.loading = True
        self.page.update()
        
        try:
            # Load clients
            self.clients_data = await self.api_client.get_clients()
            self.filtered_clients = self.clients_data.copy()
            
        except Exception as e:
            print(f"Error loading clients data: {e}")
            # Use mock data as fallback
            self.clients_data = [
                {
                    'id': 1,
                    'name': 'Alice Johnson',
                    'email': 'alice@example.com',
                    'phone': '+1234567890',
                    'is_active': True,
                    'total_cases': 3,
                    'active_cases': 1,
                    'address': '123 Main St, City, State',
                    'company': 'ABC Corporation',
                },
                {
                    'id': 2,
                    'name': 'Bob Smith',
                    'email': 'bob@example.com',
                    'phone': '+0987654321',
                    'is_active': True,
                    'total_cases': 2,
                    'active_cases': 2,
                    'address': '456 Oak Ave, Town, State',
                    'company': 'XYZ Industries',
                },
                {
                    'id': 3,
                    'name': 'Carol Davis',
                    'email': 'carol@example.com',
                    'phone': '+1122334455',
                    'is_active': False,
                    'total_cases': 1,
                    'active_cases': 0,
                    'address': '789 Pine Rd, Village, State',
                    'company': None,
                },
                {
                    'id': 4,
                    'name': 'David Wilson',
                    'email': 'david@example.com',
                    'phone': '+5544332211',
                    'is_active': True,
                    'total_cases': 5,
                    'active_cases': 3,
                    'address': '321 Elm St, City, State',
                    'company': 'Wilson Enterprises',
                },
                {
                    'id': 5,
                    'name': 'Eva Martinez',
                    'email': 'eva@example.com',
                    'phone': '+9988776655',
                    'is_active': True,
                    'total_cases': 1,
                    'active_cases': 1,
                    'address': '654 Maple Dr, Town, State',
                    'company': None,
                }
            ]
            self.filtered_clients = self.clients_data.copy()
        finally:
            self.loading = False
            self.page.update()
