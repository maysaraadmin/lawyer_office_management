import flet as ft
from flet import (
    Container, Column, Row, Card, ElevatedButton, Text, Icon, 
    IconTheme, Divider, CircleAvatar, TextField, PopupMenuButton,
    PopupMenuItem, IconButton, Colors, Border, BorderRadius, margin,
    padding, alignment, MainAxisAlignment, CrossAxisAlignment, TextStyle
)
from datetime import datetime, timedelta
import logging
from src.services.api_client import api_client

logger = logging.getLogger(__name__)

# Color constants matching Django web app
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
BLUE_400 = "#60A5FA"
BLUE_500 = "#3B82F6"
BLUE_600 = "#2563EB"
GREEN_50 = "#ECFDF5"
GREEN_500 = "#10B981"
RED_50 = "#FEF2F2"
RED_500 = "#EF4444"
YELLOW_50 = "#FFFBEB"
YELLOW_500 = "#F59E0B"
PURPLE_500 = "#8B5CF6"
INDIGO_500 = "#6366F1"

class DashboardView:
    def __init__(self, app):
        self.app = app
        self.page = app.page
        self.controls = []  # Store child controls
        self.data_loaded = False
        self.loading = True
        self.error = None
        self.stats_data = {}
        self.appointments_data = []
    
    def build(self):
        """Build the dashboard view matching Django web app design"""
        self.controls = []
        
        # Check if we're on mobile (width < 768px)
        page_width = self.app.page.width if hasattr(self.app, 'page') and self.app.page else 1200
        is_mobile = page_width < 768
        
        if is_mobile:
            # Mobile layout: vertical stack with collapsible sidebar
            main_content = ft.Column(
                controls=[
                    # Mobile header with menu toggle
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.IconButton(
                                    "menu",
                                    icon_color=GRAY_600,
                                    on_click=self._toggle_mobile_sidebar,
                                ),
                                ft.Text(
                                    "Lawyer Office",
                                    size=18,
                                    weight=ft.FontWeight.W_700,
                                    color=GRAY_900,
                                ),
                                ft.Container(expand=True),
                                ft.IconButton(
                                    "notifications_outline",
                                    icon_color=GRAY_600,
                                    tooltip="Notifications",
                                ),
                            ],
                            spacing=8,
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        bgcolor=WHITE,
                        border=ft.border.only(bottom=ft.BorderSide(1, GRAY_200)),
                    ),
                    # Mobile sidebar (hidden by default)
                    ft.Container(
                        content=self._build_mobile_sidebar(),
                        visible=False,
                        expand=True,
                        bgcolor=WHITE,
                    ),
                    # Main content area
                    ft.Column(
                        controls=[
                            # Dashboard content (mobile optimized)
                            self._build_mobile_dashboard_content(),
                        ],
                        expand=True,
                        spacing=0,
                    ),
                ],
                expand=True,
                spacing=0,
            )
        else:
            # Desktop layout: sidebar + main content
            main_content = ft.Row(
                controls=[
                    # Sidebar
                    self._build_sidebar(),
                    # Main content area
                    ft.Column(
                        controls=[
                            # Header
                            self._build_header(),
                            # Dashboard content
                            self._build_dashboard_content(),
                        ],
                        expand=True,
                        spacing=0,
                    ),
                ],
                expand=True,
                spacing=0,
            )
        self.controls.append(main_content)
        return ft.Column(self.controls, expand=True, spacing=0)
    
    def _build_sidebar(self):
        """Build navigation sidebar matching Django web app"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Logo/Brand
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    "business_center",
                                    color=BLUE_600,
                                    size=24,
                                ),
                                ft.Text(
                                    "Lawyer Office",
                                    size=16,
                                    weight=ft.FontWeight.W_700,
                                    color=GRAY_900,
                                ),
                            ],
                            spacing=8,
                        ),
                        padding=ft.padding.symmetric(horizontal=20, vertical=16),
                        border=ft.border.only(bottom=ft.BorderSide(1, GRAY_200)),
                    ),
                    
                    # Navigation Menu
                    ft.Container(
                        content=ft.Column(
                            controls=[
                            self._nav_item(
                                "dashboard_outline",
                                "Dashboard",
                                True,
                                BLUE_600,
                            ),
                            self._nav_item(
                                "people_outline",
                                "Clients",
                                False,
                                GRAY_600,
                            ),
                            self._nav_item(
                                "calendar_month_outline",
                                "Appointments",
                                False,
                                GRAY_600,
                            ),
                            self._nav_item(
                                "description_outline",
                                "Cases",
                                False,
                                GRAY_600,
                            ),
                            self._nav_item(
                                "payment_outline",
                                "Billing",
                                False,
                                GRAY_600,
                            ),
                            self._nav_item(
                                "report_outline",
                                "Reports",
                                False,
                                GRAY_600,
                            ),
                        ],
                        spacing=4,
                    )),
                    
                    ft.Container(
                        expand=True
                    ),  # Spacer
                    
                    # User section
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Divider(color=GRAY_200),
                                ft.Row(
                                    controls=[
                                        ft.CircleAvatar(
                                            content=ft.Text("A", size=20),
                                            radius=20,
                                            bgcolor=BLUE_500,
                                        ),
                                        ft.Column(
                                            controls=[
                                                ft.Text(
                                                    "Admin User",
                                                    size=14,
                                                    weight=ft.FontWeight.W_500,
                                                    color=GRAY_900,
                                                ),
                                                ft.Text(
                                                    "admin@lawfirm.com",
                                                    size=12,
                                                    color=GRAY_500,
                                                ),
                                            ],
                                            spacing=2,
                                        ),
                                    ],
                                    spacing=12,
                                ),
                                ft.Container(
                                    content=ft.ElevatedButton(
                                        "Logout",
                                        bgcolor=RED_500,
                                        color=WHITE,
                                        on_click=self._logout,
                                        height=36,
                                    ),
                                    margin=ft.margin.only(top=12),
                                ),
                            ],
                        ),
                        padding=ft.padding.all(20),
                    ),
                ],
                spacing=0,
            ),
            width=280,
            bgcolor=WHITE,
            border=ft.border.only(right=ft.BorderSide(1, GRAY_200)),
        )
    
    def _toggle_mobile_sidebar(self, e):
        """Toggle mobile sidebar visibility"""
        if hasattr(self.app, 'page') and self.app.page:
            # Find the mobile sidebar container and toggle its visibility
            for control in self.controls[0].controls:
                if isinstance(control, ft.Container) and len(control.controls) > 1:
                    # This is likely the mobile sidebar container
                    mobile_sidebar = control.controls[1]
                    mobile_sidebar.visible = not mobile_sidebar.visible
                    self.app.page.update_async()
                    break
    
    def _build_mobile_sidebar(self):
        """Build mobile-optimized sidebar"""
        return ft.Column(
            controls=[
                # Logo/Brand
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                "business_center",
                                color=BLUE_600,
                                size=24,
                            ),
                            ft.Text(
                                "Lawyer Office",
                                size=16,
                                weight=ft.FontWeight.W_700,
                                color=GRAY_900,
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(
                                "close",
                                icon_color=GRAY_600,
                                on_click=self._toggle_mobile_sidebar,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.symmetric(horizontal=20, vertical=16),
                    border=ft.border.only(bottom=ft.BorderSide(1, GRAY_200)),
                ),
                
                # Navigation Menu
                ft.Container(
                    content=ft.Column(
                        controls=[
                        self._nav_item(
                            "dashboard_outline",
                            "Dashboard",
                            True,
                            BLUE_600,
                        ),
                        self._nav_item(
                            "people_outline",
                            "Clients",
                            False,
                            GRAY_600,
                        ),
                        self._nav_item(
                            "calendar_month_outline",
                            "Appointments",
                            False,
                            GRAY_600,
                        ),
                        self._nav_item(
                            "description_outline",
                            "Cases",
                            False,
                            GRAY_600,
                        ),
                        self._nav_item(
                            "payment_outline",
                            "Billing",
                            False,
                            GRAY_600,
                        ),
                        self._nav_item(
                            "report_outline",
                            "Reports",
                            False,
                            GRAY_600,
                        ),
                    ],
                    spacing=4,
                )),
                
                ft.Container(
                    expand=True
                ),  # Spacer
                
                # User section
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Divider(color=GRAY_200),
                            ft.Row(
                                controls=[
                                    ft.CircleAvatar(
                                        background_image_url=f"https://picsum.photos/seed/user123/100/100",
                                        radius=20,
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                "Admin User",
                                                size=14,
                                                weight=ft.FontWeight.W_500,
                                                color=GRAY_900,
                                            ),
                                            ft.Text(
                                                "admin@lawfirm.com",
                                                size=12,
                                                color=GRAY_500,
                                            ),
                                        ],
                                        spacing=2,
                                    ),
                                ],
                                spacing=12,
                            ),
                            ft.Container(
                                content=ft.ElevatedButton(
                                    "Logout",
                                    bgcolor=RED_500,
                                    color=WHITE,
                                    on_click=self._logout,
                                    height=36,
                                ),
                                margin=ft.margin.only(top=12),
                            ),
                        ],
                    ),
                    padding=ft.padding.all(20),
                ),
            ],
            spacing=0,
        )
    
    def _build_mobile_dashboard_content(self):
        """Build mobile-optimized dashboard content matching web app responsive design"""
        if self.loading:
            return self._build_loading_state()
        
        if self.error:
            return self._build_error_state()
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Mobile Stats Cards - 2x2 grid like web app md:grid-cols-2
                    ft.Column(
                        controls=[
                            # Row 1: Total Clients, Today's Appointments
                            ft.Row(
                                controls=[
                                    self._build_mobile_stat_card(
                                        "Total Clients",
                                        str(self.stats_data.get('total_clients', 0)),
                                        BLUE_600,
                                        "people",
                                    ),
                                    self._build_mobile_stat_card(
                                        "Today's Appointments",
                                        str(self.stats_data.get('today_appointments', 0)),
                                        GREEN_500,
                                        "calendar_today",
                                    ),
                                ],
                                spacing=12,
                            ),
                            # Row 2: Pending Cases, Monthly Revenue
                            ft.Row(
                                controls=[
                                    self._build_mobile_stat_card(
                                        "Pending Cases",
                                        str(self.stats_data.get('pending_cases', 0)),
                                        YELLOW_500,
                                        "pending_actions",
                                    ),
                                    self._build_mobile_stat_card(
                                        "Monthly Revenue",
                                        f"${self.stats_data.get('monthly_revenue', 0):,.0f}",
                                        GREEN_500,
                                        "trending_up",
                                    ),
                                ],
                                spacing=12,
                            ),
                        ],
                        spacing=12,
                    ),
                    
                    # Recent Appointments - Full width on mobile
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    "Recent Appointments",
                                    size=18,
                                    weight=ft.FontWeight.W_700,
                                    color=GRAY_900,
                                ),
                                ft.Container(
                                    content=self._build_appointments_list(),
                                    margin=ft.margin.only(top=16),
                                ),
                            ],
                            spacing=0,
                        ),
                        padding=ft.padding.all(16),
                        bgcolor=WHITE,
                        border_radius=12,
                        border=ft.border.all(1, GRAY_200),
                        margin=ft.margin.only(top=16),
                    ),
                    
                    # Quick Actions - Vertical stack on mobile
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    "Quick Actions",
                                    size=18,
                                    weight=ft.FontWeight.W_700,
                                    color=GRAY_900,
                                ),
                                ft.Column(
                                    controls=[
                                        self._action_button(
                                            "Add New Client",
                                            "person_add",
                                            BLUE_600,
                                        ),
                                        self._action_button(
                                            "Schedule Appointment",
                                            "add_calendar",
                                            GREEN_500,
                                        ),
                                        self._action_button(
                                            "Create Case",
                                            "add_box",
                                            PURPLE_500,
                                        ),
                                        self._action_button(
                                            "Generate Report",
                                            "assignment",
                                            INDIGO_500,
                                        ),
                                    ],
                                    spacing=8,
                                    margin=ft.margin.only(top=16),
                                ),
                            ],
                            spacing=0,
                        ),
                        padding=ft.padding.all(16),
                        bgcolor=WHITE,
                        border_radius=12,
                        border=ft.border.all(1, GRAY_200),
                        margin=ft.margin.only(top=16),
                    ),
                ],
                spacing=0,
            ),
            padding=ft.padding.all(16),
            bgcolor=GRAY_50,
            expand=True,
        )
    
    def _build_mobile_stat_card(self, title: str, value: str, color: str, icon_name):
        """Build mobile-optimized statistics card"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(
                                    icon_name,
                                    color=WHITE,
                                    size=20,
                                ),
                                width=40,
                                height=40,
                                bgcolor=color,
                                border_radius=8,
                                alignment=ft.alignment.center,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            value,
                                            size=20,
                                            weight=ft.FontWeight.W_700,
                                            color=GRAY_900,
                                        ),
                                        ft.Text(
                                            title,
                                            size=12,
                                            color=GRAY_600,
                                        ),
                                    ],
                                    spacing=2,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
            ),
            padding=ft.padding.all(16),
            bgcolor=WHITE,
            border_radius=12,
            border=ft.border.all(1, GRAY_200),
            expand=True,
        )
    
    def _nav_item(self, icon, text, is_active, color):
        """Build navigation item"""
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        icon,
                        color=color,
                        size=20,
                    ),
                    ft.Text(
                        text,
                        size=14,
                        weight=ft.FontWeight.W_500 if is_active else ft.FontWeight.W_400,
                        color=color,
                    ),
                ],
                spacing=12,
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border_radius=8,
            bgcolor=BLUE_50 if is_active else None,
            on_click=lambda e: self._nav_click(text),
        )
    
    def _build_header(self):
        """Build header matching Django web app"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Dashboard",
                                size=24,
                                weight=ft.FontWeight.W_700,
                                color=GRAY_900,
                            ),
                            ft.Container(expand=True),
                            ft.Row(
                                controls=[
                                    # Search
                                    ft.Container(
                                        content=ft.TextField(
                                            hint_text="Search...",
                                            border_radius=8,
                                            height=40,
                                            text_size=14,
                                            prefix_icon="search_outline",
                                            border_color=GRAY_200,
                                            focused_border_color=BLUE_500,
                                        ),
                                        width=300,
                                    ),
                                    # Notifications
                                    ft.IconButton(
                                        "notifications_outline",
                                        icon_color=GRAY_600,
                                        tooltip="Notifications",
                                    ),
                                    # Settings
                                    ft.IconButton(
                                        "settings_outline",
                                        icon_color=GRAY_600,
                                        tooltip="Settings",
                                    ),
                                ],
                                spacing=8,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(
                        f"Welcome back! Today is {datetime.now().strftime('%A, %B %d, %Y')}",
                        size=14,
                        color=GRAY_600,
                    ),
                ],
                spacing=8,
            ),
            padding=ft.padding.all(24),
            bgcolor=WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, GRAY_200)),
        )
    
    def _build_dashboard_content(self):
        """Build main dashboard content"""
        if self.loading:
            return self._build_loading_state()
        
        if self.error:
            return self._build_error_state()
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Stats Cards
                    ft.Row(
                        controls=[
                            self._build_stat_card(
                                "Total Clients",
                                str(self.stats_data.get('total_clients', 0)),
                                BLUE_600,
                                "people",
                            ),
                            self._build_stat_card(
                                "Today's Appointments",
                                str(self.stats_data.get('today_appointments', 0)),
                                GREEN_500,
                                "calendar_today",
                            ),
                            self._build_stat_card(
                                "Pending Cases",
                                str(self.stats_data.get('pending_cases', 0)),
                                YELLOW_500,
                                "pending_actions",
                            ),
                            self._build_stat_card(
                                "Monthly Revenue",
                                f"${self.stats_data.get('monthly_revenue', 0):,.0f}",
                                GREEN_500,
                                "trending_up",
                            ),
                        ],
                        spacing=16,
                    ),
                    
                    # Recent Activity & Appointments
                    ft.Row(
                        controls=[
                            # Recent Appointments
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            "Recent Appointments",
                                            size=18,
                                            weight=ft.FontWeight.W_700,
                                            color=GRAY_900,
                                        ),
                                        ft.Container(
                                            content=self._build_appointments_list(),
                                            margin=ft.margin.only(top=16),
                                        ),
                                    ],
                                    spacing=0,
                                ),
                                width=400,
                                padding=ft.padding.all(20),
                                bgcolor=WHITE,
                                border_radius=12,
                                border=ft.border.all(1, GRAY_200),
                            ),
                            
                            # Quick Actions
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            "Quick Actions",
                                            size=18,
                                            weight=ft.FontWeight.W_700,
                                            color=GRAY_900,
                                        ),
                                        ft.Column(
                                            controls=[
                                                self._action_button(
                                                    "Add New Client",
                                                    "person_add",
                                                    BLUE_600,
                                                ),
                                                self._action_button(
                                                    "Schedule Appointment",
                                                    "add_calendar",
                                                    GREEN_500,
                                                ),
                                                self._action_button(
                                                    "Create Case",
                                                    "add_box",
                                                    PURPLE_500,
                                                ),
                                                self._action_button(
                                                    "Generate Report",
                                                    "assignment",
                                                    INDIGO_500,
                                                ),
                                            ],
                                            spacing=8,
                                            margin=ft.margin.only(top=16),
                                        ),
                                    ],
                                    spacing=0,
                                ),
                                expand=True,
                                padding=ft.padding.all(20),
                                bgcolor=WHITE,
                                border_radius=12,
                                border=ft.border.all(1, GRAY_200),
                                margin=ft.margin.only(left=16),
                            ),
                        ],
                        spacing=16,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                ],
                spacing=24,
            ),
            padding=ft.padding.all(24),
            bgcolor=GRAY_50,
            expand=True,
        )
    
    def _build_loading_state(self):
        """Build loading state"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                width=48,
                                height=48,
                                bgcolor=GRAY_200,
                                border_radius=8,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Container(
                                        width=120,
                                        height=24,
                                        bgcolor=GRAY_200,
                                        border_radius=4,
                                    ),
                                    ft.Container(
                                        width=80,
                                        height=16,
                                        bgcolor=GRAY_200,
                                        border_radius=4,
                                        margin=ft.margin.only(top=4),
                                    ),
                                ],
                            ),
                        ],
                        spacing=16,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(24),
            bgcolor=GRAY_50,
            expand=True,
        )
    
    def _build_error_state(self):
        """Build error state"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        "error_outline",
                        color=RED_500,
                        size=48,
                    ),
                    ft.Text(
                        "Error loading data",
                        size=20,
                        weight=ft.FontWeight.W_700,
                        color=GRAY_900,
                    ),
                    ft.Text(
                        str(self.error),
                        size=14,
                        color=GRAY_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.ElevatedButton(
                        "Retry",
                        bgcolor=BLUE_600,
                        color=WHITE,
                        on_click=self._retry_load,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            padding=ft.padding.all(24),
            bgcolor=GRAY_50,
            expand=True,
        )
    
    async def _nav_click(self, page_name: str):
        """Handle navigation click"""
        if hasattr(self.app, 'navigate_to'):
            await self.app.navigate_to(page_name.lower())
    
    async def _logout(self, e):
        """Handle logout"""
        if hasattr(self.app, 'logout'):
            await self.app.logout()
    
    async def _handle_action(self, action: str):
        """Handle quick action clicks"""
        if hasattr(self.app, 'page') and self.app.page:
            self.app.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Action: {action}"),
                bgcolor=BLUE_600,
            )
            self.app.page.snack_bar.open = True
            await self.app.page.update_async()
    
    def _action_button(self, text: str, icon_name: str, color: str):
        """Build action button for quick actions"""
        return ft.Container(
            content=ft.ElevatedButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            icon_name,
                            color=color,
                            size=20,
                        ),
                        ft.Text(
                            text,
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=color,
                        ),
                    ],
                    spacing=8,
                ),
                bgcolor=WHITE,
                color=color,
                height=48,
                on_click=lambda e: self._handle_action(text),
                style=ft.ButtonStyle(
                    side=ft.BorderSide(1, color),
                    shape=ft.RoundedRectangleBorder(radius=8),
                    elevation=0,
                    overlay_color=color,
                ),
            ),
            margin=ft.margin.only(bottom=8),
        )
        
        # Loading state
        if self.loading:
            loading_content = ft.Column(
                [
                    header,
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.ProgressRing(color="#2196F3"),
                                ft.Text("Loading dashboard data...", color=GREY_600),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        alignment=ft.alignment.center,
                        expand=True,
                    ),
                ],
                expand=True,
            )
            self.controls.append(loading_content)
            return loading_content
        
        # Error state
        if self.error:
            error_content = ft.Column(
                [
                    header,
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon("error", color="#E53935", size=48),
                                ft.Text("Failed to load dashboard data", color="#E53935", weight=ft.FontWeight.W_700),
                                ft.Text(self.error, color=GREY_600),
                                ft.TextButton("Retry", on_click=self._retry_load),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        alignment=ft.alignment.center,
                        expand=True,
                    ),
                ],
                expand=True,
            )
            self.controls.append(error_content)
            return error_content
        
        # Stats cards with dynamic data
        stats_row = ft.Row(
            [
                self._build_stat_card(
                    "Total Appointments", 
                    str(self.stats_data.get("total_appointments", "0")), 
                    "#2196F3", 
                    "calendar_month"
                ),
                self._build_stat_card(
                    "Active Clients", 
                    str(self.stats_data.get("active_clients", "0")), 
                    "#4CAF50", 
                    "people"
                ),
                self._build_stat_card(
                    "Upcoming Deadlines", 
                    str(self.stats_data.get("upcoming_deadlines", "0")), 
                    "#FF9800", 
                    "notifications"
                ),
                self._build_stat_card(
                    "Total Revenue", 
                    f"${self.stats_data.get('total_revenue', '0'):,.2f}", 
                    "#9C27B0", 
                    "attach_money"
                ),
            ],
            spacing=20,
            run_spacing=20,
            wrap=True,
        )
        
        # Upcoming appointments
        upcoming_header = ft.Container(
            content=ft.Row(
                [
                    ft.Text("Upcoming Appointments", style=ft.TextThemeStyle.TITLE_MEDIUM),
                    ft.TextButton("View All", on_click=lambda _: self.app.navigate(1)),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(top=20, bottom=10),
        )
        
        appointments_list = ft.ListView(expand=True, spacing=10)
        
        if self.appointments_data:
            for appt in self.appointments_data:
                appointments_list.controls.append(
                    self._build_appointment_card(appt)
                )
        else:
            appointments_list.controls.append(
                ft.Container(
                    content=ft.Text("No upcoming appointments", italic=True, color=GREY_600),
                    alignment=ft.alignment.center,
                    padding=20,
                )
            )
        
        # Main content column
        content = ft.Column(
            [
                header,
                stats_row,
                upcoming_header,
                appointments_list,
            ],
            expand=True,
        )

    def _build_stat_card(self, title: str, value: str, color: str, icon_name):
        """Build statistics card matching Django design"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(
                                    icon_name,
                                    color=WHITE,
                                    size=24,
                                ),
                                width=48,
                                height=48,
                                bgcolor=color,
                                border_radius=8,
                                alignment=ft.alignment.center,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            value,
                                            size=24,
                                            weight=ft.FontWeight.W_700,
                                            color=GRAY_900,
                                        ),
                                        ft.Text(
                                            title,
                                            size=14,
                                            color=GRAY_600,
                                        ),
                                    ],
                                    spacing=4,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
            ),
            padding=ft.padding.all(20),
            bgcolor=WHITE,
            border_radius=12,
            border=ft.border.all(1, GRAY_200),
            height=120,
        )

async def _retry_load(self, e):
    """Retry loading data"""
    self._retrying = True  # Set flag to allow retry
    self.error = None
    self.loading = True
    await self.load_data()
    # Rebuild the view
    self.controls.clear()
    new_view = self.build()
    if self.app and hasattr(self.app, 'content'):
        self.app.content.content = new_view
        self.app.page.update()
    self._retrying = False  # Clear flag

    async def _on_window_resize(self, e):
        """Handle window resize to update responsive layout"""
        if hasattr(self.app, 'page') and self.app.page:
            # Rebuild the dashboard with new dimensions
            self.controls.clear()
            self.build()
            await self.app.page.update_async()
    
    async def load_data(self):
        """Load dashboard data from API"""
        # Skip if already loading or has an error
        if self.loading or (self.error and not hasattr(self, '_retrying')):
            logger.info(f"Skipping load - loading: {self.loading}, error: {self.error is not None}")
            return
        
        try:
            logger.info("Loading dashboard data...")
            self.loading = True
            self.error = None
            
            # Add timeout for API calls
            import asyncio
            try:
                # Load appointments data with timeout
                appointments_response = await asyncio.wait_for(
                    api_client.get_appointments(), 
                    timeout=10.0  # 10 second timeout
                )
            except asyncio.TimeoutError:
                logger.error("API request timed out")
                raise Exception("API request timed out. Please check your connection.")
                
            # Handle both dict with 'results' and direct list responses
            if isinstance(appointments_response, dict) and 'results' in appointments_response:
                appointments = appointments_response['results']
            elif isinstance(appointments_response, list):
                appointments = appointments_response
            else:
                appointments = []
            
            appointments_count = len(appointments)
            
            # Filter upcoming appointments (next 7 days)
            now = datetime.now()
            upcoming = []
            for appt in appointments:
                try:
                    # Handle different time formats
                    appt_time_str = appt.get('start_time', appt.get('date_time', appt.get('time', '')))
                    if isinstance(appt_time_str, str):
                        appt_time = datetime.fromisoformat(appt_time_str.replace('Z', '+00:00'))
                    elif isinstance(appt_time_str, datetime):
                        appt_time = appt_time_str
                    else:
                        continue
                    
                    if now <= appt_time <= now + timedelta(days=7):
                        upcoming.append(appt)
                except Exception as e:
                    logger.warning(f"Error parsing appointment time: {e}")
                    continue
            
            self.appointments_data = upcoming
            logger.info(f"Loaded {len(upcoming)} upcoming appointments")
            
            # Load stats data
            try:
                stats = await api_client.get_appointment_stats()
                self.stats_data = {
                    "total_appointments": stats.get("total", appointments_count),
                    "active_clients": stats.get("active_clients", 0),
                    "upcoming_deadlines": stats.get("upcoming", len(upcoming)),
                    "total_revenue": stats.get("total_revenue", 0.0),
                }
            except:
                # Fallback to computed stats
                self.stats_data = {
                    "total_appointments": appointments_count,
                    "active_clients": len(set(appt.get('client_id', '') for appt in appointments)),
                    "upcoming_deadlines": len(upcoming),
                    "total_revenue": 0.0,
                }
            
            logger.info("Stats data loaded")
            
            self.loading = False
            self.data_loaded = True
            logger.info("Dashboard data loaded successfully")
            
            # Refresh the view after loading
            if self.app and hasattr(self.app, 'content'):
                self.controls.clear()
                new_view = self.build()
                self.app.content.content = new_view
                if hasattr(self.app, 'page') and self.app.page:
                    try:
                        await self.app.page.update_async()
                    except:
                        self.app.page.update()
            
        except Exception as e:
            logger.error(f"Error loading dashboard data: {str(e)}")
            self.error = str(e)
            self.loading = False
    
    async def did_mount_async(self):
        """Called when the view is mounted to the page"""
        # Prevent multiple loads
        if self.data_loaded:
            logger.info("Dashboard data already loaded, skipping...")
            return
        
        await self.load_data()
    
    async def _view_appointment(self, e):
        """Handle viewing an appointment"""
        try:
            appointment = e.control.data
            print(f"Viewing appointment: {appointment['id']}")
            # In a real app, this would navigate to the appointment detail view
            if hasattr(self, 'page') and self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Viewing appointment: {appointment['title']}")
                )
                self.page.snack_bar.open = True
                try:
                    await self.page.update_async()
                except:
                    self.page.update()
        except Exception as ex:
            print(f"Error viewing appointment: {str(ex)}")
