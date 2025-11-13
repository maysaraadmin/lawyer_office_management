import flet as ft
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio

# Import base view
from .base_view import BaseView

class BillingView(BaseView):
    """View for managing billing and invoices"""
    
    def __init__(self, app):
        super().__init__(app)
        self.invoices = []
        self.is_loading = True
        self.error = None
        self.selected_filter = "all"
    
    async def initialize(self):
        """Initialize the billing data"""
        await self.load_invoices()
    
    async def load_invoices(self):
        """Load invoices from the API"""
        self.is_loading = True
        self.error = None
        
        try:
            # Get invoices from the API
            params = {
                'status': self.selected_filter if self.selected_filter != 'all' else None,
                'ordering': '-issue_date',
            }
            
            # Remove None values from params
            params = {k: v for k, v in params.items() if v is not None}
            
            response = await self.app.api_client.get('invoices/', params=params)
            self.invoices = response.get('results', [])
        except Exception as e:
            logger.error(f"Error loading invoices: {str(e)}")
            self.error = str(e)
        finally:
            self.is_loading = False
            await self.page.update_async()
    
    async def apply_filter(self, filter_type):
        """Apply filter to invoices list"""
        self.selected_filter = filter_type
        await self.load_invoices()
    
    def build(self) -> ft.Container:
        """Build the billing view"""
        if self.is_loading:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.ProgressRing(),
                        ft.Text("Loading invoices..."),
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
                            "Error loading invoices",
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
        
        # Build invoices list
        invoices_list = ft.ListView(expand=True)
        
        if not self.invoices:
            invoices_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                "RECEIPT",
                                size=48,
                                color="#9E9E9E",  # Grey 500
                            ),
                            ft.Text(
                                "No invoices found",
                                size=16,
                                color="#757575",  # Grey 600
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                "You don't have any invoices yet.",
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
            for invoice in self.invoices:
                # Determine status color and text
                status = invoice.get('status', '').lower()
                if status == 'paid':
                    status_color = "#4CAF50"  # Green
                    status_text = "Paid"
                elif status == 'overdue':
                    status_color = "#F44336"  # Red
                    status_text = "Overdue"
                else:
                    status_color = "#FFC107"  # Amber
                    status_text = "Pending"
                
                # Format amount
                amount = float(invoice.get('amount', 0))
                formatted_amount = f"${amount:,.2f}"
                
                # Format date
                issue_date = datetime.strptime(invoice.get('issue_date', ''), "%Y-%m-%d").strftime("%b %d, %Y")
                due_date = datetime.strptime(invoice.get('due_date', ''), "%Y-%m-%d").strftime("%b %d, %Y")
                
                invoices_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Text(
                                        f"#{invoice.get('invoice_number', '')}",
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    width=100,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            invoice.get('client', {}).get('name', 'No client'),
                                            weight=ft.FontWeight.W_500,
                                        ),
                                        ft.Text(
                                            f"Issued: {issue_date} • Due: {due_date}",
                                            size=12,
                                            color="#757575",  # Grey 600
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        formatted_amount,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    width=100,
                                    alignment=ft.alignment.center,
                                ),
                                ft.Container(
                                    content=ft.Container(
                                        content=ft.Text(
                                            status_text,
                                            color=ft.colors.WHITE,
                                            size=12,
                                            weight=ft.FontWeight.W_500,
                                        ),
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                        border_radius=4,
                                        bgcolor=status_color,
                                    ),
                                    width=100,
                                ),
                                ft.IconButton(
                                    icon="MORE_VERT",
                                    on_click=lambda e, i=invoice: self.show_invoice_menu(i),
                                    tooltip="Actions",
                                ),
                            ],
                            spacing=16,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        border=ft.border.only(bottom=ft.border.BorderSide(1, "#E0E0E0")),  # Grey 300
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
                                    "Billing",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Container(expand=True),
                                ft.ElevatedButton(
                                    "New Invoice",
                                    on_click=lambda _: self.add_invoice(),
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
                    
                    # Stats cards
                    ft.Container(
                        content=ft.Row(
                            [
                                self._build_stat_card(
                                    "Total Revenue",
                                    "$12,345.67",
                                    "TRENDING_UP",
                                    "#4CAF50",  # Green
                                    "+12% from last month",
                                ),
                                self._build_stat_card(
                                    "Outstanding",
                                    "$3,456.78",
                                    "WARNING",
                                    "#FFC107",  # Amber
                                    "3 invoices overdue",
                                ),
                                self._build_stat_card(
                                    "Average Invoice",
                                    "$1,234.56",
                                    "BAR_CHART",
                                    "#2196F3",  # Blue
                                    "+5% from last month",
                                ),
                            ],
                            spacing=16,
                        ),
                        padding=ft.padding.only(bottom=24),
                    ),
                    
                    # Filters
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(
                                    "Filter:",
                                    size=14,
                                    color="#757575",  # Grey 600
                                    weight=ft.FontWeight.W_500,
                                ),
                                ft.Container(width=8),
                                ft.FilterChip(
                                    label=ft.Text("All"),
                                    selected=self.selected_filter == "all",
                                    on_select=lambda _: self.apply_filter("all"),
                                ),
                                ft.Container(width=8),
                                ft.FilterChip(
                                    label=ft.Text("Paid"),
                                    selected=self.selected_filter == "paid",
                                    on_select=lambda _: self.apply_filter("paid"),
                                    selected_color="#4CAF50",  # Green
                                ),
                                ft.Container(width=8),
                                ft.FilterChip(
                                    label=ft.Text("Pending"),
                                    selected=self.selected_filter == "pending",
                                    on_select=lambda _: self.apply_filter("pending"),
                                    selected_color="#FFC107",  # Amber
                                ),
                                ft.Container(width=8),
                                ft.FilterChip(
                                    label=ft.Text("Overdue"),
                                    selected=self.selected_filter == "overdue",
                                    on_select=lambda _: self.apply_filter("overdue"),
                                    selected_color="#F44336",  # Red
                                ),
                                ft.Container(expand=True),
                                ft.TextField(
                                    label="Search invoices",
                                    prefix_icon="SEARCH",
                                    on_change=self.on_search,
                                    width=250,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            wrap=True,
                        ),
                        padding=ft.padding.only(bottom=16),
                    ),
                    
                    # Invoices list
                    ft.Container(
                        content=ft.Column(
                            [
                                # Header row
                                ft.Container(
                                    content=ft.Row(
                                        [
                                            ft.Text(
                                                "INVOICE #",
                                                size=12,
                                                weight=ft.FontWeight.BOLD,
                                                color="#757575",  # Grey 600
                                            ),
                                            ft.Container(width=16),
                                            ft.Text(
                                                "CLIENT",
                                                size=12,
                                                weight=ft.FontWeight.BOLD,
                                                color="#757575",  # Grey 600
                                                expand=True,
                                            ),
                                            ft.Text(
                                                "AMOUNT",
                                                size=12,
                                                weight=ft.FontWeight.BOLD,
                                                color="#757575",  # Grey 600
                                                width=100,
                                                text_align=ft.TextAlign.RIGHT,
                                            ),
                                            ft.Text(
                                                "STATUS",
                                                size=12,
                                                weight=ft.FontWeight.BOLD,
                                                color="#757575",  # Grey 600
                                                width=100,
                                                text_align=ft.TextAlign.CENTER,
                                            ),
                                            ft.Container(width=40),  # Spacer for actions
                                        ],
                                        spacing=16,
                                    ),
                                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                    border_bottom=ft.border.all(1, "#E0E0E0"),  # Grey 300
                                    bgcolor="#F5F5F5",  # Grey 100
                                ),
                                # Invoices list
                                invoices_list,
                            ],
                            spacing=0,
                        ),
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
    
    def _build_stat_card(self, title: str, value: str, icon: str, color: str, description: str = ""):
        """Build a stat card"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(
                            icon,
                            size=24,
                            color=ft.colors.WHITE,
                        ),
                        padding=12,
                        bgcolor=color,
                        border_radius=8,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                title,
                                size=12,
                                color="#757575",  # Grey 600
                            ),
                            ft.Text(
                                value,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                description,
                                size=10,
                                color="#9E9E9E",  # Grey 500
                            ) if description else None,
                        ],
                        spacing=2,
                    ),
                ],
                spacing=12,
            ),
            padding=ft.padding.all(16),
            bgcolor=ft.colors.WHITE,
            border_radius=8,
            border=ft.border.all(1, "#E0E0E0"),  # Grey 300
            expand=True,
        )
    
    async def on_search(self, e):
        """Handle search input change"""
        search_term = e.control.value.lower()
        # In a real app, we would filter the invoices list here
        # For now, we'll just log the search term
        print(f"Searching for: {search_term}")
        await self.page.update_async()
    
    async def add_invoice(self):
        """Navigate to add invoice form"""
        await self.go_to("/invoices/new")
    
    async def view_invoice(self, invoice):
        """Navigate to invoice details"""
        await self.go_to(f"/invoices/{invoice.get('id')}")
    
    async def edit_invoice(self, invoice):
        """Navigate to edit invoice form"""
        await self.go_to(f"/invoices/{invoice.get('id')}/edit")
    
    async def show_invoice_menu(self, invoice):
        """Show invoice context menu"""
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        self.page.dialog = ft.AlertDialog(
            title=ft.Text(f"Invoice #{invoice.get('invoice_number', '')}"),
            content=ft.Text(f"What would you like to do with this invoice?"),
            actions=[
                ft.TextButton("View", on_click=lambda _: self.view_invoice(invoice)),
                ft.TextButton("Edit", on_click=lambda _: self.edit_invoice(invoice)),
                ft.TextButton("Send", on_click=close_dialog),
                ft.TextButton("Download", on_click=close_dialog),
                ft.TextButton("Print", on_click=close_dialog),
                ft.TextButton("Cancel", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        await self.page.update_async()
