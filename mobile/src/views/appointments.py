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

class MobileAppointmentsView:
    """Mobile appointments view matching Django web app design"""

    def __init__(self, page: ft.Page, api_client):
        self.page = page
        self.api_client = api_client
        self.loading = False
        self.error = None
        self.appointments_data = []
        self.filtered_appointments = []
        self.search_query = ""
        self.status_filter = "All"
        self.date_from = None
        self.date_to = None
        self.selected_appointment = None
        self.show_add_dialog = False
        
    def build(self) -> ft.Column:
        """Build the mobile appointments view"""
        return ft.Column(
            controls=[
                self._build_header(),
                self._build_filters(),
                self._build_appointments_list(),
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
                                "Appointments",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=GRAY_900,
                            ),
                            ft.Text(
                                f"{len(self.filtered_appointments)} appointments",
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
                hint_text="Search appointments...",
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
                                            text="Scheduled",
                                            style=ft.ButtonStyle(
                                                bgcolor=BLUE_600 if self.status_filter == "scheduled" else WHITE,
                                                color=WHITE if self.status_filter == "scheduled" else GRAY_700,
                                                elevation=0,
                                                side=ft.border.all(1, BLUE_600 if self.status_filter == "scheduled" else GRAY_300),
                                                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                            ),
                                            on_click=lambda _: self._set_status_filter("scheduled"),
                                        ),
                                        ft.ElevatedButton(
                                            text="Confirmed",
                                            style=ft.ButtonStyle(
                                                bgcolor=BLUE_600 if self.status_filter == "confirmed" else WHITE,
                                                color=WHITE if self.status_filter == "confirmed" else GRAY_700,
                                                elevation=0,
                                                side=ft.border.all(1, BLUE_600 if self.status_filter == "confirmed" else GRAY_300),
                                                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                            ),
                                            on_click=lambda _: self._set_status_filter("confirmed"),
                                        ),
                                        ft.ElevatedButton(
                                            text="Completed",
                                            style=ft.ButtonStyle(
                                                bgcolor=BLUE_600 if self.status_filter == "completed" else WHITE,
                                                color=WHITE if self.status_filter == "completed" else GRAY_700,
                                                elevation=0,
                                                side=ft.border.all(1, BLUE_600 if self.status_filter == "completed" else GRAY_300),
                                                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                            ),
                                            on_click=lambda _: self._set_status_filter("completed"),
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
                    # Date filters
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            "From Date",
                                            size=12,
                                            weight=ft.FontWeight.W_500,
                                            color=GRAY_700,
                                        ),
                                        ft.TextField(
                                            hint_text="Start date",
                                            border_color=GRAY_300,
                                            focused_border_color=BLUE_600,
                                            text_size=14,
                                            on_change=self._on_date_from_change,
                                        ),
                                    ],
                                    spacing=4,
                                    expand=True,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            "To Date",
                                            size=12,
                                            weight=ft.FontWeight.W_500,
                                            color=GRAY_700,
                                        ),
                                        ft.TextField(
                                            hint_text="End date",
                                            border_color=GRAY_300,
                                            focused_border_color=BLUE_600,
                                            text_size=14,
                                            on_change=self._on_date_to_change,
                                        ),
                                    ],
                                    spacing=4,
                                    expand=True,
                                ),
                            ],
                            spacing=12,
                        ),
                        padding=ft.padding.only(left=16, right=16, bottom=16),
                    ),
                ],
                spacing=0,
            ),
            bgcolor=WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, GRAY_200)),
        )
    
    def _build_appointments_list(self) -> ft.Column:
        """Build appointments list matching Django design"""
        if self.loading:
            return ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.ProgressRing(color=BLUE_600),
                                ft.Text("Loading appointments...", color=GRAY_600),
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
        
        if not self.filtered_appointments:
            return ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(
                                    ft.Icons.CALENDAR_MONTH_OUTLINED,
                                    color=GRAY_400,
                                    size=64,
                                ),
                                ft.Text(
                                    "No appointments found",
                                    size=18,
                                    weight=ft.FontWeight.W_500,
                                    color=GRAY_700,
                                ),
                                ft.Text(
                                    "Try adjusting your filters or create a new appointment",
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
                            self._build_appointment_item(appointment)
                            for appointment in self.filtered_appointments
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.all(16),
                    expand=True,
                ),
            ],
            expand=True,
        )
    
    def _build_appointment_item(self, appointment: Dict[str, Any]) -> ft.Container:
        """Build individual appointment item matching Django design"""
        # Parse appointment time
        appt_time = appointment.get('date', appointment.get('start_time', ''))
        appt_time_str = appointment.get('time', '')
        
        if isinstance(appt_time, str):
            try:
                appt_datetime = datetime.fromisoformat(appt_time.replace('Z', '+00:00'))
                date_str = appt_datetime.strftime('%b %d, %Y')
                if not appt_time_str:
                    appt_time_str = appt_datetime.strftime('%I:%M %p')
            except:
                date_str = appt_time
                appt_time_str = appt_time_str or "Unknown time"
        else:
            date_str = "Unknown date"
            appt_time_str = appt_time_str or "Unknown time"

        client_name = appointment.get('client_name', 'Unknown Client')
        title = appointment.get('title', 'General Consultation')
        status = appointment.get('status', 'scheduled')
        notes = appointment.get('notes', '')
        
        # Status colors
        status_colors = {
            'scheduled': YELLOW_600,
            'confirmed': GREEN_600,
            'cancelled': RED_600,
            'completed': GRAY_600,
        }
        status_bg_colors = {
            'scheduled': YELLOW_50,
            'confirmed': GREEN_50,
            'cancelled': RED_50,
            'completed': GRAY_100,
        }

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.CALENDAR_TODAY_OUTLINED,
                                    color=BLUE_600,
                                    size=20,
                                ),
                                width=40,
                                height=40,
                                bgcolor=BLUE_50,
                                border_radius=20,
                                alignment=ft.alignment.center,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        title,
                                        size=16,
                                        weight=ft.FontWeight.W_500,
                                        color=GRAY_900,
                                    ),
                                    ft.Text(
                                        client_name,
                                        size=14,
                                        color=GRAY_600,
                                    ),
                                    ft.Text(
                                        notes,
                                        size=12,
                                        color=GRAY_500,
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ) if notes else ft.Container(),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            appt_time_str,
                                            size=14,
                                            weight=ft.FontWeight.W_500,
                                            color=GRAY_900,
                                            text_align=ft.TextAlign.RIGHT,
                                        ),
                                        ft.Container(
                                            content=ft.Text(
                                                status.title(),
                                                size=11,
                                                weight=ft.FontWeight.W_500,
                                                color=status_colors.get(status, GRAY_600),
                                            ),
                                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                            bgcolor=status_bg_colors.get(status, GRAY_100),
                                            border_radius=12,
                                        ),
                                        ft.Text(
                                            date_str,
                                            size=11,
                                            color=GRAY_500,
                                            text_align=ft.TextAlign.RIGHT,
                                        ),
                                    ],
                                    spacing=4,
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
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
            on_click=lambda _, appt=appointment: self._view_appointment_details(appt),
        )
    
    def _build_fab(self) -> ft.FloatingActionButton:
        """Build floating action button"""
        return ft.FloatingActionButton(
            icon=ft.Icons.ADD_OUTLINED,
            bgcolor=BLUE_600,
            on_click=self._add_appointment,
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
    
    def _on_date_from_change(self, e):
        """Handle date from change"""
        self.date_from = e.control.value
        self._apply_filters()
    
    def _on_date_to_change(self, e):
        """Handle date to change"""
        self.date_to = e.control.value
        self._apply_filters()
    
    def _apply_filters(self):
        """Apply all filters"""
        self.filtered_appointments = []
        
        for appointment in self.appointments_data:
            # Status filter
            if self.status_filter != "All" and appointment.get('status') != self.status_filter:
                continue
            
            # Search filter
            if self.search_query:
                search_lower = self.search_query.lower()
                client_name = appointment.get('client_name', '').lower()
                title = appointment.get('title', '').lower()
                notes = appointment.get('notes', '').lower()
                
                if (search_lower not in client_name and 
                    search_lower not in title and 
                    search_lower not in notes):
                    continue
            
            # Date filters (simplified for now)
            # In a real app, you'd parse and compare dates properly
            
            self.filtered_appointments.append(appointment)
        
        self.page.update()
    
    def _view_appointment_details(self, appointment: Dict[str, Any]):
        """View appointment details"""
        self.selected_appointment = appointment
        # This would open a details dialog or navigate to details page
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(f"Viewing: {appointment.get('title', 'Unknown')}"),
                bgcolor=BLUE_600,
            )
        )
    
    def _add_appointment(self, e):
        """Add new appointment"""
        self.show_add_dialog = True
        # This would open an add appointment dialog
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text("Add appointment form coming soon!"),
                bgcolor=BLUE_600,
            )
        )
    
    async def load_data(self):
        """Load appointments data"""
        self.loading = True
        self.page.update()
        
        try:
            # Load appointments
            self.appointments_data = await self.api_client.get_appointments()
            self.filtered_appointments = self.appointments_data.copy()
            
        except Exception as e:
            print(f"Error loading appointments data: {e}")
            # Use mock data as fallback
            self.appointments_data = [
                {
                    'id': 1,
                    'title': 'Client Consultation',
                    'client_name': 'Alice Johnson',
                    'date': '2024-01-15',
                    'time': '10:00 AM',
                    'status': 'scheduled',
                    'notes': 'Initial consultation for new client'
                },
                {
                    'id': 2,
                    'title': 'Case Review',
                    'client_name': 'Bob Smith',
                    'date': '2024-01-15',
                    'time': '2:00 PM',
                    'status': 'confirmed',
                    'notes': 'Review case progress and next steps'
                },
                {
                    'id': 3,
                    'title': 'Court Appearance',
                    'client_name': 'Carol Davis',
                    'date': '2024-01-16',
                    'time': '9:00 AM',
                    'status': 'scheduled',
                    'notes': 'Motion hearing'
                },
                {
                    'id': 4,
                    'title': 'Document Signing',
                    'client_name': 'David Wilson',
                    'date': '2024-01-14',
                    'time': '3:00 PM',
                    'status': 'completed',
                    'notes': 'Sign settlement agreement'
                }
            ]
            self.filtered_appointments = self.appointments_data.copy()
        finally:
            self.loading = False
            self.page.update()
