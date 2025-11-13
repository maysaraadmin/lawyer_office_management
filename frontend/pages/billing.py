import flet as ft
from datetime import datetime, timedelta
from ..services.api_client import api_client
from .base_page import BasePage

class BillingPage(BasePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.page.title = "Billing - Lawyer Office Management"
        self.invoices = []
        self.time_entries = []
        self.current_tab = "invoices"
        
        # Create tabs
        self.tabs = ft.Tabs(
            selected_index=0,
            on_change=self.on_tab_change,
            tabs=[
                ft.Tab(text="Invoices"),
                ft.Tab(text="Time Entries"),
                ft.Tab(text="Payments"),
                ft.Tab(text="Reports"),
            ],
            expand=True,
        )
        
        # Create content containers
        self.content = ft.Container(
            content=ft.Column(
                [
                    self._build_header(),
                    ft.Divider(),
                    ft.Container(expand=True)  # Placeholder for tab content
                ],
                expand=True,
                spacing=0,
            ),
            padding=20,
            expand=True,
        )
    
    async def initialize(self):
        """Initialize the billing page"""
        if not await self.check_auth():
            return
            
        self.setup_app_bar()
        self.setup_drawer()
        self.show_loading("Loading billing information...")
        
        try:
            await self.load_data()
            await self.build_ui()
        except Exception as e:
            await self.handle_error(e, "Failed to load billing information")
    
    async def load_data(self):
        """Load billing data from the API"""
        try:
            # Load invoices
            invoice_response = await api_client.get("billing/invoices/")
            self.invoices = invoice_response.get("results", [])
            
            # Load time entries
            time_response = await api_client.get("billing/time-entries/")
            self.time_entries = time_response.get("results", [])
            
        except Exception as e:
            await self.handle_error(e, "Failed to load billing data")
            self.invoices = []
            self.time_entries = []
    
    def _build_header(self):
        """Build the page header"""
        return ft.Row(
            [
                ft.Text("Billing", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Create Invoice",
                            icon=ft.icons.ADD,
                            on_click=self.create_invoice,
                        ),
                        ft.PopupMenuButton(
                            icon=ft.icons.MORE_VERT,
                            items=[
                                ft.PopupMenuItem(
                                    text="Record Time",
                                    on_click=self.record_time,
                                ),
                                ft.PopupMenuItem(
                                    text="Record Payment",
                                    on_click=self.record_payment,
                                ),
                            ],
                        ),
                    ],
                    spacing=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
    
    async def build_ui(self):
        """Build the UI components"""
        # Clear existing content
        self.page.clean()
        
        # Rebuild app bar and drawer
        self.setup_app_bar()
        self.setup_drawer()
        
        # Update tab content based on selection
        await self.update_tab_content()
        
        # Add content to page
        self.page.add(
            ft.Column(
                [
                    self.tabs,
                    self.content,
                ],
                expand=True,
                spacing=0,
            )
        )
        
        self.page.update()
    
    async def on_tab_change(self, e):
        """Handle tab change"""
        self.current_tab = ["invoices", "time_entries", "payments", "reports"][e.control.selected_index]
        await self.update_tab_content()
        self.page.update()
    
    async def update_tab_content(self):
        """Update the content based on the selected tab"""
        if self.current_tab == "invoices":
            content = await self._build_invoices_tab()
        elif self.current_tab == "time_entries":
            content = await self._build_time_entries_tab()
        elif self.current_tab == "payments":
            content = await self._build_payments_tab()
        else:  # reports
            content = await self._build_reports_tab()
        
        # Replace the content container
        self.content.content.controls[2] = content
    
    async def _build_invoices_tab(self):
        """Build the invoices tab content"""
        if not self.invoices:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.icons.RECEIPT, size=48, color=ft.colors.GREY_400),
                        ft.Text("No invoices found"),
                        ft.ElevatedButton(
                            "Create Your First Invoice",
                            on_click=self.create_invoice,
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                ),
                padding=40,
                alignment=ft.alignment.center,
                expand=True,
            )
        
        # Create invoice list
        invoice_rows = []
        for invoice in self.invoices:
            status_color = {
                'draft': ft.colors.ORANGE,
                'sent': ft.colors.BLUE,
                'paid': ft.colors.GREEN,
                'overdue': ft.colors.RED,
            }.get(invoice.get('status', 'draft').lower(), ft.colors.GREY)
            
            invoice_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"INV-{invoice.get('id', '')}")),
                        ft.DataCell(ft.Text(invoice.get('client_name', 'N/A'))),
                        ft.DataCell(ft.Text(invoice.get('invoice_date', ''))),
                        ft.DataCell(ft.Text(f"${invoice.get('amount', 0):.2f}")),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    invoice.get('status', '').title(),
                                    color=ft.colors.WHITE,
                                    weight=ft.FontWeight.BOLD,
                                    size=12,
                                ),
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=4,
                                bgcolor=status_color,
                            )
                        ),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.REMOVE_RED_EYE,
                                        icon_color=ft.colors.BLUE,
                                        tooltip="View",
                                        on_click=lambda e, id=invoice.get('id'): self.view_invoice(id),
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        icon_color=ft.colors.ORANGE,
                                        tooltip="Edit",
                                        on_click=lambda e, id=invoice.get('id'): self.edit_invoice(id),
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.PRINT,
                                        icon_color=ft.colors.GREEN,
                                        tooltip="Print",
                                        on_click=lambda e, id=invoice.get('id'): self.print_invoice(id),
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ],
                    on_select_changed=lambda e, id=invoice.get('id'): self.view_invoice(id),
                )
            )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.TextField(
                                label="Search invoices...",
                                prefix_icon=ft.icons.SEARCH,
                                expand=True,
                            ),
                            ft.Dropdown(
                                label="Status",
                                options=[
                                    ft.dropdown.Option("All"),
                                    ft.dropdown.Option("Draft"),
                                    ft.dropdown.Option("Sent"),
                                    ft.dropdown.Option("Paid"),
                                    ft.dropdown.Option("Overdue"),
                                ],
                                value="All",
                                width=150,
                            ),
                            ft.Dropdown(
                                label="Date Range",
                                options=[
                                    ft.dropdown.Option("This Month"),
                                    ft.dropdown.Option("Last Month"),
                                    ft.dropdown.Option("This Year"),
                                    ft.dropdown.Option("Custom"),
                                ],
                                value="This Month",
                                width=150,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Container(
                        content=ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("Invoice #")),
                                ft.DataColumn(ft.Text("Client")),
                                ft.DataColumn(ft.Text("Date")),
                                ft.DataColumn(ft.Text("Amount")),
                                ft.DataColumn(ft.Text("Status")),
                                ft.DataColumn(ft.Text("Actions")),
                            ],
                            rows=invoice_rows,
                            heading_row_height=40,
                            data_row_height=60,
                            show_checkbox_column=True,
                        ),
                        margin=ft.margin.only(top=20),
                        expand=True,
                    ),
                ],
                expand=True,
            ),
            padding=20,
            expand=True,
        )
    
    async def _build_time_entries_tab(self):
        """Build the time entries tab content"""
        if not self.time_entries:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.icons.ACCESS_TIME, size=48, color=ft.colors.GREY_400),
                        ft.Text("No time entries found"),
                        ft.ElevatedButton(
                            "Record Time Entry",
                            on_click=self.record_time,
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                ),
                padding=40,
                alignment=ft.alignment.center,
                expand=True,
            )
        
        # Create time entries list
        time_entries = []
        for entry in self.time_entries:
            time_entries.append(
                ft.ListTile(
                    leading=ft.Icon(ft.icons.ACCESS_TIME),
                    title=ft.Text(entry.get('description', 'No description')),
                    subtitle=ft.Text(f"{entry.get('case_name', 'No case')} • {entry.get('duration_hours', 0)} hours"),
                    trailing=ft.Text(f"${entry.get('billing_rate', 0) * entry.get('duration_hours', 0):.2f}"),
                    on_click=lambda e, id=entry.get('id'): self.view_time_entry(id),
                )
            )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.TextField(
                                label="Search time entries...",
                                prefix_icon=ft.icons.SEARCH,
                                expand=True,
                            ),
                            ft.Dropdown(
                                label="Date Range",
                                options=[
                                    ft.dropdown.Option("This Week"),
                                    ft.dropdown.Option("This Month"),
                                    ft.dropdown.Option("Last Month"),
                                    ft.dropdown.Option("Custom"),
                                ],
                                value="This Week",
                                width=150,
                            ),
                            ft.Dropdown(
                                label="Billable",
                                options=[
                                    ft.dropdown.Option("All"),
                                    ft.dropdown.Option("Billable"),
                                    ft.dropdown.Option("Non-billable"),
                                ],
                                value="All",
                                width=150,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.ListView(
                        controls=time_entries,
                        expand=True,
                    ),
                ],
                expand=True,
            ),
            padding=20,
            expand=True,
        )
    
    async def _build_payments_tab(self):
        """Build the payments tab content"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Payments", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                    ft.Text("Payments functionality coming soon!"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            ),
            padding=40,
            expand=True,
        )
    
    async def _build_reports_tab(self):
        """Build the reports tab content"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Reports", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                    ft.Text("Reports functionality coming soon!"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            ),
            padding=40,
            expand=True,
        )
    
    async def create_invoice(self, _=None):
        """Navigate to create invoice page"""
        self.page.go("/billing/invoices/new")
    
    async def view_invoice(self, invoice_id: str):
        """View invoice details"""
        self.page.go(f"/billing/invoices/{invoice_id}")
    
    async def edit_invoice(self, invoice_id: str):
        """Edit an invoice"""
        self.page.go(f"/billing/invoices/{invoice_id}/edit")
    
    async def print_invoice(self, invoice_id: str):
        """Print an invoice"""
        self.show_snackbar(f"Printing invoice {invoice_id}...")
    
    async def record_time(self, _=None):
        """Record a new time entry"""
        self.page.go("/billing/time-entries/new")
    
    async def view_time_entry(self, entry_id: str):
        """View time entry details"""
        self.page.go(f"/billing/time-entries/{entry_id}")
    
    async def record_payment(self, _=None):
        """Record a new payment"""
        self.page.go("/billing/payments/new")

async def billing_page(page: ft.Page):
    """Create and initialize the billing page"""
    billing = BillingPage(page)
    await billing.initialize()
    return billing
