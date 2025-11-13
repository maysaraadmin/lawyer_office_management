import flet as ft
from typing import List, Dict, Any, Optional
import asyncio

# Import base view and components
from .base_view import BaseView
from components.case_card import CaseCard

# Import services and config
from services.api_client import api_client, auth_service
from config import Config

class CasesView(BaseView):
    """View for managing cases"""
    
    def __init__(self, app):
        super().__init__(app)
        self.cases = []
        self.filtered_cases = []
        self.is_loading = True
        self.error = None
        self.search_query = ""
        self.status_filter = "all"
        self.sort_by = "-created_at"
        
        # Pagination
        self.current_page = 1
        self.page_size = 10
        self.total_pages = 1
        self.total_count = 0
    
    async def initialize(self):
        """Initialize the cases view"""
        await self.load_cases()
    
    async def load_cases(self):
        """Load cases from the API"""
        self.is_loading = True
        self.error = None
        
        try:
            # Build query parameters
            params = {
                'page': self.current_page,
                'page_size': self.page_size,
                'ordering': self.sort_by,
            }
            
            # Add search query if provided
            if self.search_query:
                params['search'] = self.search_query
            
            # Add status filter if not 'all'
            if self.status_filter != 'all':
                params['status'] = self.status_filter
            
            # Make the API request
            response = await api_client.get('cases/', params=params)
            
            # Update state
            self.cases = response.get('results', [])
            self.filtered_cases = self.cases
            
            # Update pagination
            self.total_count = response.get('count', 0)
            self.total_pages = (self.total_count + self.page_size - 1) // self.page_size
            
        except Exception as e:
            logger.error(f"Error loading cases: {str(e)}")
            self.error = str(e)
        finally:
            self.is_loading = False
            await self.page.update_async()
    
    def build_search_bar(self) -> ft.Container:
        """Build the search and filter bar"""
        search_field = ft.TextField(
            hint_text="Search cases...",
            prefix_icon=ft.icons.SEARCH,
            on_submit=lambda e: self.on_search(e.control.value),
            on_change=lambda e: setattr(self, 'search_query', e.control.value),
            expand=True,
            border_radius=8,
            border_color=ft.colors.GREY_300,
            focused_border_color=Config.COLORS['primary'],
            content_padding=12,
        )
        
        status_dropdown = ft.Dropdown(
            value=self.status_filter,
            options=[
                ft.dropdown.Option("all", "All Statuses"),
                ft.dropdown.Option("open", "Open"),
                ft.dropdown.Option("active", "Active"),
                ft.dropdown.Option("pending", "Pending"),
                ft.dropdown.Option("closed", "Closed"),
            ],
            on_change=self.on_status_filter_change,
            border_radius=8,
            border_color=ft.colors.GREY_300,
            focused_border_color=Config.COLORS['primary'],
            content_padding=12,
            width=180,
        )
        
        sort_dropdown = ft.Dropdown(
            value=self.sort_by,
            options=[
                ft.dropdown.Option("-created_at", "Newest First"),
                ft.dropdown.Option("created_at", "Oldest First"),
                ft.dropdown.Option("title", "Title (A-Z)"),
                ft.dropdown.Option("-title", "Title (Z-A)"),
                ft.dropdown.Option("next_court_date", "Next Court Date (Soonest)"),
                ft.dropdown.Option("-next_court_date", "Next Court Date (Latest)"),
            ],
            on_change=self.on_sort_change,
            border_radius=8,
            border_color=ft.colors.GREY_300,
            focused_border_color=Config.COLORS['primary'],
            content_padding=12,
            width=220,
        )
        
        return ft.Container(
            content=ft.Row(
                [
                    # Search field
                    ft.Container(
                        content=search_field,
                        expand=2,
                    ),
                    
                    # Status filter
                    ft.Container(
                        content=status_dropdown,
                        margin=ft.margin.only(left=8, right=8),
                    ),
                    
                    # Sort dropdown
                    ft.Container(
                        content=sort_dropdown,
                    ),
                    
                    # New case button
                    ft.ElevatedButton(
                        "New Case",
                        on_click=lambda _: self.go_to('/cases/new'),
                        icon=ft.icons.ADD,
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(horizontal=20, vertical=14),
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                ],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=12, horizontal=16),
            bgcolor=ft.colors.WHITE,
            border=ft.border.only(
                bottom=ft.border.BorderSide(1, ft.colors.GREY_200)
            ),
        )
    
    def build_cases_list(self) -> ft.Container:
        """Build the list of cases"""
        if self.is_loading and not self.cases:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.ProgressRing(),
                        ft.Text("Loading cases...", size=14, color=ft.colors.GREY_600),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                ),
                alignment=ft.alignment.center,
                padding=40,
            )
        
        if self.error:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.icons.ERROR_OUTLINE, size=48, color=ft.colors.RED_400),
                        ft.Text("Error loading cases", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            self.error,
                            size=14,
                            color=ft.colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.ElevatedButton(
                            "Retry",
                            on_click=self.load_cases,
                            icon=ft.icons.REFRESH,
                            style=ft.ButtonStyle(
                                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                ),
                alignment=ft.alignment.center,
                padding=40,
            )
        
        if not self.cases:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            ft.icons.CASE_OUTLINED,
                            size=64,
                            color=ft.colors.GREY_400,
                        ),
                        ft.Text(
                            "No cases found",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.GREY_600,
                        ),
                        ft.Text(
                            "You don't have any cases yet. Create your first case to get started.",
                            size=14,
                            color=ft.colors.GREY_500,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.ElevatedButton(
                            "Create Case",
                            on_click=lambda _: self.go_to('/cases/new'),
                            icon=ft.icons.ADD,
                            style=ft.ButtonStyle(
                                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                ),
                alignment=ft.alignment.center,
                padding=40,
            )
        
        # Create case cards
        case_cards = [
            CaseCard(
                case=case,
                on_tap=lambda e, c=case: self.go_to(f"/cases/{c['id']}"),
            )
            for case in self.cases
        ]
        
        return ft.Container(
            content=ft.Column(
                case_cards,
                spacing=8,
            ),
            padding=16,
        )
    
    def build_pagination(self) -> ft.Container:
        """Build the pagination controls"""
        if self.total_pages <= 1:
            return ft.Container()
        
        page_buttons = []
        
        # Previous page button
        prev_button = ft.IconButton(
            icon=ft.icons.CHEVRON_LEFT,
            on_click=lambda _: self.on_page_change(self.current_page - 1),
            disabled=self.current_page == 1,
            icon_size=20,
            tooltip="Previous page",
        )
        
        # Next page button
        next_button = ft.IconButton(
            icon=ft.icons.CHEVRON_RIGHT,
            on_click=lambda _: self.on_page_change(self.current_page + 1),
            disabled=self.current_page >= self.total_pages,
            icon_size=20,
            tooltip="Next page",
        )
        
        # Page info text
        page_info = ft.Text(
            f"Page {self.current_page} of {self.total_pages} • {self.total_count} total cases",
            size=12,
            color=ft.colors.GREY_600,
        )
        
        return ft.Container(
            content=ft.Row(
                [
                    prev_button,
                    page_info,
                    next_button,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=16,
            ),
            padding=ft.padding.symmetric(vertical=16),
            border_top=ft.border.all(1, ft.colors.GREY_200),
        )
    
    async def on_search(self, query: str):
        """Handle search"""
        self.search_query = query
        self.current_page = 1  # Reset to first page
        await self.load_cases()
    
    async def on_status_filter_change(self, e):
        """Handle status filter change"""
        self.status_filter = e.control.value
        self.current_page = 1  # Reset to first page
        await self.load_cases()
    
    async def on_sort_change(self, e):
        """Handle sort change"""
        self.sort_by = e.control.value
        await self.load_cases()
    
    async def on_page_change(self, page: int):
        """Handle page change"""
        if 1 <= page <= self.total_pages:
            self.current_page = page
            await self.load_cases()
            # Scroll to top
            await self.page.views[0].controls[0].controls[1].scroll_to(0, 0)
    
    def build(self) -> ft.Control:
        """Build the view"""
        return ft.Column(
            [
                # Header
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                "Cases",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.symmetric(horizontal=24, vertical=16),
                    border_bottom=ft.border.all(1, ft.colors.GREY_200),
                    bgcolor=ft.colors.WHITE,
                ),
                
                # Search and filters
                self.build_search_bar(),
                
                # Cases list
                ft.Container(
                    content=ft.Column(
                        [
                            self.build_cases_list(),
                            self.build_pagination(),
                        ],
                        spacing=0,
                        expand=True,
                    ),
                    expand=True,
                    bgcolor=ft.colors.GREY_50,
                ),
            ],
            spacing=0,
            expand=True,
        )
