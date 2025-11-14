import flet as ft
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

from services import api_client

# Color constants
GREY_600 = "#757575"
WHITE = "#FFFFFF"
BLUE_600 = "#1E88E5"
GREEN_600 = "#43A047"
ORANGE_600 = "#FB8C00"
RED_600 = "#E53935"

logger = logging.getLogger(__name__)

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
        """Build the dashboard view"""
        # Clear any existing controls
        self.controls = []
        
        # Header with welcome message
        header = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Dashboard",
                        style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        f"Welcome back! Today is {datetime.now().strftime('%A, %B %d, %Y')}",
                        style=ft.TextThemeStyle.BODY_MEDIUM,
                        color=GREY_600,
                    ),
                ],
                spacing=4,
            ),
            padding=ft.padding.only(bottom=20),
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
                                ft.Text("Failed to load dashboard data", color="#E53935", weight=ft.FontWeight.BOLD),
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
        
        # Store the content in controls
        self.controls.append(content)
        return content
    
    def _build_stat_card(self, title: str, value: str, color: str, icon_name: str) -> ft.Card:
        # Convert icon name to lowercase and replace any underscores
        icon_name = str(icon_name).lower().replace('_', '')
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(name=icon_name, color=color, size=24),
                                ft.Text(
                                    value,
                                    style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            spacing=10,
                        ),
                        ft.Text(
                            title,
                            style=ft.TextThemeStyle.BODY_SMALL,
                            color=GREY_600,
                        ),
                    ],
                    spacing=4,
                ),
                padding=20,
                width=250,
                height=120,
            ),
            elevation=1,
shadow_color="#E0E0E0",
        )
    
    def _build_appointment_card(self, appt: dict) -> ft.Card:
        # Handle time - could be datetime object or string
        if isinstance(appt.get("time"), str):
            # Parse string time
            try:
                appt_time = datetime.fromisoformat(appt["time"].replace('Z', '+00:00'))
            except:
                appt_time = datetime.now()
        elif isinstance(appt.get("time"), datetime):
            appt_time = appt["time"]
        else:
            appt_time = datetime.now()
            
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        appt_time.strftime("%I:%M %p"),
                                        style=ft.TextThemeStyle.BODY_LARGE,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        appt_time.strftime("%b %d"),
                                        style=ft.TextThemeStyle.BODY_SMALL,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=2,
                            ),
                            padding=10,
                            border_radius=8,
                            bgcolor=WHITE,
                        ),
                        ft.VerticalDivider(width=20, color="#FFFFFF"),
                        ft.Column(
                            [
                                ft.Text(
                                    appt["title"],
                                    style=ft.TextThemeStyle.BODY_LARGE,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    f"With: {appt['client']}",
                                    style=ft.TextThemeStyle.BODY_MEDIUM,
                                ),
                                ft.Text(
                                    f"Type: {appt['type']}",
                                    style=ft.TextThemeStyle.BODY_SMALL,
                                    color=GREY_600,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=4,
                        ),
                        ft.Container(expand=True),  # Spacer
                        ft.IconButton(
                            icon="chevron_right",
                            bgcolor=BLUE_600,
                            on_click=self._view_appointment,
                            data=appt,  # Store appointment data in the button
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=10,
            ),
            elevation=0,
shadow_color="#EEEEEE",
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    
    async def did_mount_async(self):
        """Called when the dashboard is mounted"""
        await self.load_dashboard_data()
    
    async def load_dashboard_data(self):
        """Load dashboard data from API"""
        try:
            logger.info("Loading dashboard data...")
            self.loading = True
            self.error = None
            
            # Load appointments data
            appointments_count = 0
            try:
                appointments = await api_client.get_appointments()
                appointments_count = len(appointments)
                # Filter upcoming appointments (next 7 days)
                now = datetime.now()
                upcoming = []
                for appt in appointments:
                    appt_time = datetime.fromisoformat(appt.get('date_time', '').replace('Z', '+00:00'))
                    if appt_time > now and appt_time <= now + timedelta(days=7):
                        upcoming.append(appt)
                self.appointments_data = upcoming[:5]  # Show max 5 appointments
                logger.info(f"Loaded {len(self.appointments_data)} upcoming appointments")
            except Exception as e:
                logger.error(f"Failed to load appointments: {str(e)}")
                self.appointments_data = []
                appointments_count = 0
            
            # Load stats data
            try:
                # For now, use mock data for stats since we don't have specific endpoints
                # In a real app, these would come from the API
                self.stats_data = {
                    "total_appointments": appointments_count,
                    "active_clients": 18,  # This would come from a clients endpoint
                    "upcoming_deadlines": 5,  # This would come from a cases/deadlines endpoint
                    "total_revenue": 12450.00,  # This would come from a billing endpoint
                }
                logger.info("Stats data loaded")
            except Exception as e:
                logger.error(f"Failed to load stats: {str(e)}")
                self.stats_data = {
                    "total_appointments": 0,
                    "active_clients": 0,
                    "upcoming_deadlines": 0,
                    "total_revenue": 0.00,
                }
            
            self.loading = False
            self.data_loaded = True
            logger.info("Dashboard data loaded successfully")
            
            # Update the UI
            if hasattr(self, 'controls') and self.controls:
                self.controls.clear()
                new_content = self.build()
                if hasattr(self.page, 'update'):
                    self.page.update()
            
        except Exception as e:
            logger.error(f"Error loading dashboard data: {str(e)}")
            self.loading = False
            self.error = str(e)
            
            # Update UI to show error
            if hasattr(self, 'controls') and self.controls:
                self.controls.clear()
                new_content = self.build()
                if hasattr(self.page, 'update'):
                    self.page.update()
    
    async def _retry_load(self, e):
        """Retry loading dashboard data"""
        await self.load_dashboard_data()
    
    def _get_upcoming_appointments(self):
        """Fallback method - now returns loaded data"""
        return self.appointments_data if self.appointments_data else []
    
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
