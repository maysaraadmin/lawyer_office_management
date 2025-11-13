import flet as ft
from datetime import datetime, timedelta

# Define color constants as strings
GREY_600 = "#757575"
WHITE = "#FFFFFF"
BLUE_600 = "#1E88E5"
GREEN_600 = "#43A047"
ORANGE_600 = "#FB8C00"
RED_600 = "#E53935"

class DashboardView:
    def __init__(self, app):
        self.app = app
        self.page = app.page
    
    def build(self):
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
        
        # Stats cards
        stats_row = ft.Row(
            [
                self._build_stat_card("Total Appointments", "24", "#2196F3", "calendar_today"),
                self._build_stat_card("Active Clients", "18", "#4CAF50", "people"),
                self._build_stat_card("Upcoming Deadlines", "5", "#FF9800", "notification_important"),
                self._build_stat_card("Total Revenue", "$12,450", "#9C27B0", "attach_money"),
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
        
        appointments = self._get_upcoming_appointments()
        appointments_list = ft.ListView(expand=True, spacing=10)
        
        for appt in appointments:
            appointments_list.controls.append(
                self._build_appointment_card(appt)
            )
        
        # Main content column
        return ft.Column(
            [
                header,
                stats_row,
                upcoming_header,
                appointments_list if appointments else ft.Text("No upcoming appointments", italic=True),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
    
    def _build_stat_card(self, title: str, value: str, color: str, icon) -> ft.Card:
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(icon, color=color, size=24),
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
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        appt["time"].strftime("%I:%M %p"),
                                        style=ft.TextThemeStyle.BODY_LARGE,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        appt["time"].strftime("%b %d"),
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
                            on_click=lambda e, a=appt: self._view_appointment(a),
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
    
    def _get_upcoming_appointments(self):
        # Mock data - replace with actual API calls
        now = datetime.now()
        return [
            {
                "id": 1,
                "title": "Initial Consultation",
                "client": "John Smith",
                "time": now + timedelta(hours=2),
                "type": "Consultation",
                "location": "Office",
            },
            {
                "id": 2,
                "title": "Case Review",
                "client": "Acme Corp",
                "time": now + timedelta(days=1, hours=10),
                "type": "Meeting",
                "location": "Zoom",
            },
            {
                "id": 3,
                "title": "Court Hearing",
                "client": "Jane Doe",
                "time": now + timedelta(days=2, hours=14, minutes=30),
                "type": "Court",
                "location": "City Courthouse",
            },
        ]
    
    def _view_appointment(self, appointment):
        # TODO: Implement appointment detail view
        print(f"Viewing appointment: {appointment['id']}")
