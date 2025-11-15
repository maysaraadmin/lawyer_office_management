import flet as ft
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ClientsView:
    def __init__(self, app):
        self.app = app
        self.page = app.page
    
    async def did_mount_async(self):
        """Called when the view is mounted to the page"""
        await self._load_clients()
        self.page.update()
    
    def build(self):
        # Header with title and add button
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "Clients",
                        style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.ElevatedButton(
                        "Add Client",
                        icon="person_add",
                        on_click=self._show_add_client_dialog,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(bottom=20),
        )
        
        # Search and filter bar
        search_bar = ft.Row(
            [
                ft.SearchBar(
                    on_change=self._search_clients,
                    width=400,
                ),
                ft.Container(expand=True),  # Spacer
                ft.Dropdown(
                    label="Sort by",
                    options=[
                        ft.dropdown.Option("Name (A-Z)"),
                        ft.dropdown.Option("Name (Z-A)"),
                        ft.dropdown.Option("Recently Added"),
                        ft.dropdown.Option("Most Active"),
                    ],
                    value="Name (A-Z)",
                    width=180,
                ),
                ft.Dropdown(
                    label="Filter by",
                    options=[
                        ft.dropdown.Option("All Clients"),
                        ft.dropdown.Option("Active"),
                        ft.dropdown.Option("Inactive"),
                        ft.dropdown.Option("Individual"),
                        ft.dropdown.Option("Business"),
                    ],
                    value="All Clients",
                    width=150,
                ),
            ],
            spacing=10,
        )
        
        # Clients list
        self.clients_list = ft.ListView(expand=True, spacing=10)
        
        # Main content column
        return ft.Column(
            [
                header,
                search_bar,
                ft.Divider(height=20, color="transparent"),
                self.clients_list,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
    
    async def _load_clients(self):
        """Load clients from API"""
        # Clear existing items
        self.clients_list.controls.clear()
        
        # Get clients from API
        clients = await self._get_clients()
        
        if clients:
            for client in clients:
                self.clients_list.controls.append(
                    self._build_client_card(client)
                )
        else:
            self.clients_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                "people_outline",
                                size=48,
                                color="#BDBDBD",
                            ),
                            ft.Text(
                                "No clients found",
                                style=ft.TextThemeStyle.TITLE_MEDIUM,
                                color="#757575",
                            ),
                            ft.Text(
                                "Add your first client to get started",
                                color="#9E9E9E",
                            ),
                            ft.ElevatedButton(
                                "Add Client",
                                icon="add",
                                on_click=self._show_add_client_dialog,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=40,
                    alignment=ft.alignment.center,
                )
            )
        
        self.page.update()
    
    def _build_client_card(self, client):
        # Handle both combined name field and separate first/last name fields
        if 'name' in client:
            client_name = client['name']
        else:
            client_name = f"{client.get('first_name', '')} {client.get('last_name', '')}".strip()
        
        # Determine status color
        status_color = "#4CAF50" if client.get("is_active", True) else "#9E9E9E"
        
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        # Client avatar
                        ft.Container(
                            content=ft.Text(
                                client_name[0].upper() if client_name else "C",
                                style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                                color="#FFFFFF",
                                weight=ft.FontWeight.BOLD,
                            ),
                            width=60,
                            height=60,
                            border_radius=30,
                            bgcolor="#2196F3",
                            alignment=ft.alignment.center,
                        ),
                        ft.VerticalDivider(width=20, color="transparent"),
                        # Client info
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(
                                            client_name,
                                            style=ft.TextThemeStyle.BODY_LARGE,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Container(
                                            content=ft.Text(
                                                client.get("user_type", "client"),
                                                size=12,
                                                color="#FFFFFF",
                                            ),
                                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                            border_radius=10,
                                            bgcolor=(
                                                "#2196F3" 
                                                if client.get("user_type") == "lawyer" 
                                                else "#9C27B0"
                                            ),
                                        ),
                                    ],
                                    spacing=8,
                                ),
                                ft.Text(
                                    client.get("email", ""),
                                    style=ft.TextThemeStyle.BODY_MEDIUM,
                                ),
                                ft.Row(
                                    [
                                        ft.Icon(
                                            "phone",
                                            size=14,
                                            color="#757575",
                                        ),
                                        ft.Text(
                                            client.get("phone", ""),
                                            style=ft.TextThemeStyle.BODY_SMALL,
                                            color="#757575",
                                        ),
                                        ft.Container(width=20),  # Spacer
                                        ft.Icon(
                                            "circle",
                                            size=8,
                                            color=status_color,
                                        ),
                                        ft.Text(
                                            "Active" if client.get("is_active", True) else "Inactive",
                                            style=ft.TextThemeStyle.BODY_SMALL,
                                            color="#757575",
                                        ),
                                    ],
                                    spacing=4,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=4,
                        ),
                        ft.Container(expand=True),  # Spacer
                        # Actions
                        ft.PopupMenuButton(
                            items=[
                                ft.PopupMenuItem(
                                    text="View Profile",
                                    icon="person",
                                    on_click=lambda e, c=client: self._view_client(c),
                                ),
                                ft.PopupMenuItem(
                                    text="Edit",
                                    icon="edit",
                                    on_click=lambda e, c=client: self._edit_client(c),
                                ),
                                ft.PopupMenuItem(),  # Divider
                                ft.PopupMenuItem(
                                    text="New Appointment",
                                    icon="add_alarm",
                                    on_click=lambda e, c=client: self._new_appointment(c),
                                ),
                                ft.PopupMenuItem(
                                    text="Send Message",
                                    icon="email",
                                    on_click=lambda e, c=client: self._send_message(c),
                                ),
                            ]
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=15,
                on_click=lambda e, c=client: self._view_client(c),
            ),
            elevation=1,
            shadow_color="#EEEEEE",
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    
    async def _get_clients(self):
        """Get clients from API"""
        try:
            from src.services.api_client import api_client
            clients_response = await api_client.get_clients()
            
            # Handle both dict with 'results' and direct list responses
            if isinstance(clients_response, dict) and 'results' in clients_response:
                return clients_response['results']
            elif isinstance(clients_response, list):
                return clients_response
            else:
                return []
        except Exception as e:
            logger.error(f"Error loading clients: {str(e)}")
            return []
    
    def _search_clients(self, e):
        # TODO: Implement search functionality
        print(f"Searching clients: {e.control.value}")
    
    def _show_add_client_dialog(self, e):
        """Show dialog to add a new client"""
        # Create form fields
        first_name_field = ft.TextField(
            label="First Name",
            autofocus=True,
            width=300
        )
        
        last_name_field = ft.TextField(
            label="Last Name",
            width=300
        )
        
        email_field = ft.TextField(
            label="Email",
            width=300
        )
        
        phone_field = ft.TextField(
            label="Phone",
            width=300
        )
        
        address_field = ft.TextField(
            label="Address",
            width=300
        )
        
        city_field = ft.TextField(
            label="City",
            width=300
        )
        
        state_field = ft.TextField(
            label="State",
            width=300
        )
        
        postal_code_field = ft.TextField(
            label="Postal Code",
            width=300
        )
        
        country_field = ft.TextField(
            label="Country",
            value="United States",
            width=300
        )
        
        date_of_birth_field = ft.TextField(
            label="Date of Birth (YYYY-MM-DD)",
            width=300
        )
        
        occupation_field = ft.TextField(
            label="Occupation",
            width=300
        )
        
        company_field = ft.TextField(
            label="Company",
            width=300
        )
        
        is_active_field = ft.Checkbox(
            label="Active",
            value=True
        )
        
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        async def save_client(e):
            """Save the new client"""
            try:
                # Validate required fields
                if not first_name_field.value or not last_name_field.value or not email_field.value:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Please fill in all required fields"),
                        bgcolor=ft.Colors.RED
                    )
                    self.page.snack_bar.open = True
                    await self.page.update_async()
                    return
                
                # Prepare client data
                client_data = {
                    "first_name": first_name_field.value,
                    "last_name": last_name_field.value,
                    "email": email_field.value,
                    "phone": phone_field.value or "",
                    "address": address_field.value or "",
                    "city": city_field.value or "",
                    "state": state_field.value or "",
                    "postal_code": postal_code_field.value or "",
                    "country": country_field.value or "",
                    "occupation": occupation_field.value or "",
                    "company": company_field.value or "",
                    "is_active": is_active_field.value
                }
                
                # Only include date_of_birth if it's provided
                if date_of_birth_field.value:
                    try:
                        # Try to parse the date and format it as YYYY-MM-DD
                        from datetime import datetime
                        dob = datetime.strptime(date_of_birth_field.value, "%Y-%m-%d")
                        client_data["date_of_birth"] = dob.strftime("%Y-%m-%d")
                    except:
                        # If parsing fails, don't include the field
                        pass
                
                # Create client via API
                from src.services.api_client import api_client
                result = await api_client.create_client(client_data)
                
                # Show success message
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Client created successfully!"),
                    bgcolor=ft.Colors.GREEN
                )
                self.page.snack_bar.open = True
                
                # Close dialog
                self.page.dialog.open = False
                
                # Refresh the clients list
                await self.did_mount_async()
                
                await self.page.update_async()
                
            except Exception as ex:
                logger.error(f"Error creating client: {str(ex)}")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Failed to create client: {str(ex)}"),
                    bgcolor=ft.Colors.RED
                )
                self.page.snack_bar.open = True
                await self.page.update_async()
        
        # Create dialog with tabs for better organization
        tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(
                    text="Basic Info",
                    content=ft.Column(
                        [
                            first_name_field,
                            last_name_field,
                            email_field,
                            phone_field,
                            is_active_field
                        ],
                        tight=True,
                        height=300,
                        scroll=ft.ScrollMode.AUTO
                    )
                ),
                ft.Tab(
                    text="Address",
                    content=ft.Column(
                        [
                            address_field,
                            city_field,
                            state_field,
                            postal_code_field,
                            country_field
                        ],
                        tight=True,
                        height=300,
                        scroll=ft.ScrollMode.AUTO
                    )
                ),
                ft.Tab(
                    text="Additional",
                    content=ft.Column(
                        [
                            date_of_birth_field,
                            occupation_field,
                            company_field
                        ],
                        tight=True,
                        height=300,
                        scroll=ft.ScrollMode.AUTO
                    )
                )
            ],
            height=400,
            expand=True
        )
        
        # Create dialog
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add New Client"),
            content=tabs,
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Save", on_click=save_client),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _view_client(self, client):
        # TODO: Implement client detail view
        # Handle both combined name field and separate first/last name fields
        if 'name' in client:
            client_name = client['name']
        else:
            client_name = f"{client.get('first_name', '')} {client.get('last_name', '')}".strip()
        print(f"Viewing client: {client_name}")
    
    def _edit_client(self, client):
        # TODO: Implement edit client
        # Handle both combined name field and separate first/last name fields
        if 'name' in client:
            client_name = client['name']
        else:
            client_name = f"{client.get('first_name', '')} {client.get('last_name', '')}".strip()
        print(f"Editing client: {client_name}")
    
    def _new_appointment(self, client):
        # TODO: Implement new appointment for client
        # Handle both combined name field and separate first/last name fields
        if 'name' in client:
            client_name = client['name']
        else:
            client_name = f"{client.get('first_name', '')} {client.get('last_name', '')}".strip()
        print(f"New appointment for: {client_name}")
    
    def _send_message(self, client):
        # TODO: Implement send message to client
        # Handle both combined name field and separate first/last name fields
        if 'name' in client:
            client_name = client['name']
        else:
            client_name = f"{client.get('first_name', '')} {client.get('last_name', '')}".strip()
        print(f"Sending message to: {client_name}")
