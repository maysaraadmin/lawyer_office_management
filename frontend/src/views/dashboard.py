import flet as ft
from datetime import datetime, timedelta
from flet import *
import logging
from src.services.api_client import api_client

logger = logging.getLogger(__name__)

# Color constants
WHITE = "#FFFFFF"
GREY_50 = "#FAFAFA"
GREY_100 = "#F5F5F5"
GREY_200 = "#EEEEEE"
GREY_300 = "#E0E0E0"
GREY_400 = "#BDBDBD"
GREY_500 = "#9E9E9E"
GREY_600 = "#757575"
GREY_700 = "#616161"
GREY_800 = "#424242"
GREY_900 = "#212121"
BLUE = "#2196F3"
GREEN = "#4CAF50"
ORANGE = "#FF9800"
RED = "#F44336"

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
                            icon_color=WHITE,
                            on_click=self._view_appointment,
                            data=appt,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=10,
            ),
            elevation=0,
            shadow_color="#EEEEEE",
            shape=ft.RoundedRectangleBorder(radius=8),
        )

async def _retry_load(self, e):
    """Retry loading data"""
    self.error = None
    self.loading = True
    await self.load_data()
    # Rebuild the view
    self.controls.clear()
    new_view = self.build()
    if self.app and hasattr(self.app, 'content'):
        self.app.content.content = new_view
        self.app.page.update()

async def load_data(self):
    """Load dashboard data from API"""
    try:
        logger.info("Loading dashboard data...")
        self.loading = True
        self.error = None
        
        # Load appointments data
        appointments = await api_client.get_appointments()
        appointments_count = len(appointments)
        # Filter upcoming appointments (next 7 days)
        now = datetime.now()
        upcoming = []
        for appt in appointments:
            try:
                # Handle different time formats
                appt_time_str = appt.get('date_time', appt.get('time', ''))
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
        
    except Exception as e:
        logger.error(f"Error loading dashboard data: {str(e)}")
        self.error = str(e)
        self.loading = False
    
    async def did_mount_async(self):
        """Called when the view is mounted to the page"""
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
