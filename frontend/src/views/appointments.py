import flet as ft
from datetime import datetime, timedelta

class AppointmentsView:
    def __init__(self, app):
        self.app = app
        self.page = app.page
    
    def build(self):
        # Header with title and add button
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "Appointments",
                        style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.ElevatedButton(
                        "New Appointment",
                        icon=ft.icons.ADD,
                        on_click=self._show_add_appointment_dialog,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(bottom=20),
        )
        
        # Filters
        filter_row = ft.Row(
            [
                ft.Dropdown(
                    label="Status",
                    options=[
                        ft.dropdown.Option("All"),
                        ft.dropdown.Option("Scheduled"),
                        ft.dropdown.Option("Completed"),
                        ft.dropdown.Option("Cancelled"),
                    ],
                    value="All",
                    width=150,
                ),
                ft.Dropdown(
                    label="Type",
                    options=[
                        ft.dropdown.Option("All"),
                        ft.dropdown.Option("Consultation"),
                        ft.dropdown.Option("Meeting"),
                        ft.dropdown.Option("Court"),
                        ft.dropdown.Option("Phone Call"),
                    ],
                    value="All",
                    width=180,
                ),
                ft.OutlinedButton(
                    "Apply Filters",
                    icon=ft.icons.FILTER_ALT,
                    on_click=self._apply_filters,
                ),
                ft.Container(expand=True),  # Spacer
                ft.SearchBar(
                    hint_text="Search appointments...",
                    on_submit=self._search_appointments,
                    width=300,
                ),
            ],
            wrap=True,
            spacing=10,
            run_spacing=10,
        )
        
        # Appointments list
        self.appointments_list = ft.ListView(expand=True)
        self._load_appointments()
        
        # Main content column
        return ft.Column(
            [
                header,
                filter_row,
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                self.appointments_list,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
    
    def _load_appointments(self):
        # Clear existing items
        self.appointments_list.controls.clear()
        
        # Add section header
        today = datetime.now().date()
        self.appointments_list.controls.append(
            ft.Text("Today", style=ft.TextThemeStyle.TITLE_MEDIUM)
        )
        
        # Add appointments (mock data)
        appointments = self._get_appointments()
        today_appointments = [a for a in appointments if a["date"].date() == today]
        
        if today_appointments:
            for appt in today_appointments:
                self.appointments_list.controls.append(
                    self._build_appointment_card(appt)
                )
        else:
            self.appointments_list.controls.append(
                ft.Text("No appointments for today", italic=True, color=ft.colors.GREY)
            )
        
        # Add upcoming section
        self.appointments_list.controls.extend([
            ft.Divider(height=30),
            ft.Text("Upcoming", style=ft.TextThemeStyle.TITLE_MEDIUM),
        ])
        
        upcoming_appointments = [a for a in appointments if a["date"].date() > today]
        
        if upcoming_appointments:
            for appt in upcoming_appointments:
                self.appointments_list.controls.append(
                    self._build_appointment_card(appt)
                )
        else:
            self.appointments_list.controls.append(
                ft.Text("No upcoming appointments", italic=True, color=ft.colors.GREY)
            )
        
        self.page.update()
    
    def _build_appointment_card(self, appt):
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
                            bgcolor=ft.colors.BLUE_50,
                        ),
                        ft.VerticalDivider(width=20, color=ft.colors.TRANSPARENT),
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
                                    f"Type: {appt['type']} • {appt['location']}",
                                    style=ft.TextThemeStyle.BODY_SMALL,
                                    color=ft.colors.GREY_600,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=4,
                        ),
                        ft.Container(expand=True),  # Spacer
                        ft.PopupMenuButton(
                            items=[
                                ft.PopupMenuItem(text="Edit", icon=ft.icons.EDIT),
                                ft.PopupMenuItem(text="Cancel", icon=ft.icons.CANCEL),
                                ft.PopupMenuItem(),  # Divider
                                ft.PopupMenuItem(text="View Details", icon=ft.icons.VISIBILITY),
                            ]
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=10,
            ),
            elevation=0,
            shadow_color=ft.colors.GREY_200,
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    
    def _get_appointments(self):
        # Mock data - replace with actual API calls
        now = datetime.now()
        return [
            {
                "id": 1,
                "title": "Initial Consultation",
                "client": "John Smith",
                "time": now.replace(hour=10, minute=0, second=0, microsecond=0),
                "date": now,
                "type": "Consultation",
                "location": "Office",
                "status": "Scheduled",
            },
            {
                "id": 2,
                "title": "Case Review",
                "client": "Acme Corp",
                "time": now + timedelta(days=1, hours=10),
                "date": now + timedelta(days=1),
                "type": "Meeting",
                "location": "Zoom",
                "status": "Scheduled",
            },
            {
                "id": 3,
                "title": "Court Hearing",
                "client": "Jane Doe",
                "time": now + timedelta(days=2, hours=14, minutes=30),
                "date": now + timedelta(days=2),
                "type": "Court",
                "location": "City Courthouse",
                "status": "Scheduled",
            },
            {
                "id": 4,
                "title": "Contract Review",
                "client": "Robert Johnson",
                "time": now - timedelta(hours=2),
                "date": now,
                "type": "Consultation",
                "location": "Phone",
                "status": "Completed",
            },
        ]
    
    def _show_add_appointment_dialog(self, e):
        # TODO: Implement add appointment dialog
        print("Add new appointment clicked")
    
    def _apply_filters(self, e):
        # TODO: Implement filter logic
        print("Applying filters...")
    
    def _search_appointments(self, e):
        # TODO: Implement search logic
        print(f"Searching for: {e.control.value}")
