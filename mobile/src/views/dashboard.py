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

class MobileDashboardView:
    """Mobile dashboard view matching Django web app design"""

    def __init__(self, page: ft.Page, api_client):
        self.page = page
        self.api_client = api_client
        self.loading = False
        self.error = None
        self.stats_data = {}
        self.appointments_data = []
        self.upcoming_deadlines = []
        
    def build(self) -> ft.Column:
        """Build the mobile dashboard view"""
        return ft.Column(
            controls=[
                self._build_header(),
                self._build_stats_grid(),
                self._build_recent_appointments(),
                self._build_upcoming_deadlines(),
                self._build_quick_actions(),
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
                                "Dashboard",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=GRAY_900,
                            ),
                            ft.Text(
                                "Welcome back! Here's what's happening today.",
                                size=14,
                                color=GRAY_600,
                            ),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                        icon_color=GRAY_600,
                        icon_size=24,
                        on_click=self._handle_notifications,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.all(16),
            bgcolor=WHITE,
        )
    
    def _build_stats_grid(self) -> ft.Container:
        """Build stats cards grid matching Django design"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            self._build_stat_card(
                                "Total Clients",
                                str(self.stats_data.get('total_clients', 0)),
                                BLUE_600,
                                ft.Icons.PEOPLE_OUTLINED,
                                BLUE_50,
                            ),
                            self._build_stat_card(
                                "Active Cases",
                                str(self.stats_data.get('active_cases', 0)),
                                GREEN_600,
                                ft.Icons.WORK_OUTLINE,
                                GREEN_50,
                            ),
                        ],
                        spacing=12,
                    ),
                    ft.Row(
                        controls=[
                            self._build_stat_card(
                                "Today's Appointments",
                                str(self.stats_data.get('today_appointments', 0)),
                                YELLOW_600,
                                ft.Icons.CALENDAR_TODAY_OUTLINED,
                                YELLOW_50,
                            ),
                            self._build_stat_card(
                                "Pending Tasks",
                                str(self.stats_data.get('pending_tasks', 0)),
                                RED_600,
                                ft.Icons.PENDING_ACTIONS_OUTLINED,
                                RED_50,
                            ),
                        ],
                        spacing=12,
                    ),
                ],
                spacing=12,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            bgcolor=GRAY_50,
        )
    
    def _build_stat_card(self, title: str, value: str, icon_color: str, icon, bg_color: str) -> ft.Container:
        """Build individual stat card matching Django design"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(
                                    icon,
                                    color=icon_color,
                                    size=24,
                                ),
                                width=48,
                                height=48,
                                bgcolor=bg_color,
                                border_radius=12,
                                alignment=ft.alignment.center,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            value,
                                            size=24,
                                            weight=ft.FontWeight.BOLD,
                                            color=GRAY_900,
                                        ),
                                        ft.Text(
                                            title,
                                            size=12,
                                            weight=ft.FontWeight.W_500,
                                            color=GRAY_600,
                                        ),
                                    ],
                                    spacing=2,
                                ),
                                expand=True,
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
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color="#00000010",
                offset=ft.Offset(0, 1),
            ),
        )
    
    def _build_recent_appointments(self) -> ft.Container:
        """Build recent appointments section matching Django design"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(
                                    "Recent Appointments",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=GRAY_900,
                                ),
                                ft.TextButton(
                                    "View All",
                                    style=ft.ButtonStyle(
                                        color=BLUE_600,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    ),
                                    on_click=self._view_all_appointments,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.padding.only(bottom=12),
                    ),
                    ft.Column(
                        controls=[
                            self._build_appointment_item(appt)
                            for appt in self.appointments_data[:5]
                        ] if self.appointments_data else [
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.CALENDAR_MONTH_OUTLINED,
                                            color=GRAY_400,
                                            size=48,
                                        ),
                                        ft.Text(
                                            "No appointments scheduled",
                                            color=GRAY_500,
                                            size=14,
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=12,
                                ),
                                padding=ft.padding.all(32),
                            )
                        ],
                        spacing=8,
                    ),
                ],
                spacing=0,
            ),
            padding=ft.padding.all(16),
            bgcolor=WHITE,
            margin=ft.margin.symmetric(horizontal=16, vertical=8),
            border_radius=12,
            border=ft.border.all(1, GRAY_200),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color="#00000010",
                offset=ft.Offset(0, 1),
            ),
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
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                        color=GRAY_900,
                                    ),
                                    ft.Text(
                                        client_name,
                                        size=12,
                                        color=GRAY_600,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            appt_time_str,
                                            size=12,
                                            weight=ft.FontWeight.W_500,
                                            color=GRAY_900,
                                            text_align=ft.TextAlign.RIGHT,
                                        ),
                                        ft.Container(
                                            content=ft.Text(
                                                status.title(),
                                                size=10,
                                                weight=ft.FontWeight.W_500,
                                                color=status_colors.get(status, GRAY_600),
                                            ),
                                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                            bgcolor=status_bg_colors.get(status, GRAY_100),
                                            border_radius=12,
                                        ),
                                    ],
                                    spacing=4,
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(
                        content=ft.Text(
                            date_str,
                            size=11,
                            color=GRAY_500,
                        ),
                        padding=ft.padding.only(left=56),
                    ),
                ],
                spacing=8,
            ),
            padding=ft.padding.all(12),
            border=ft.border.all(1, GRAY_200),
            border_radius=8,
            bgcolor=WHITE,
        )
    
    def _build_upcoming_deadlines(self) -> ft.Container:
        """Build upcoming deadlines section matching Django design"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(
                                    "Upcoming Deadlines",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=GRAY_900,
                                ),
                                ft.TextButton(
                                    "View All",
                                    style=ft.ButtonStyle(
                                        color=BLUE_600,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    ),
                                    on_click=self._view_all_deadlines,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.padding.only(bottom=12),
                    ),
                    ft.Column(
                        controls=[
                            self._build_deadline_item(deadline)
                            for deadline in self.upcoming_deadlines[:3]
                        ] if self.upcoming_deadlines else [
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.ALARM_OUTLINED,
                                            color=GRAY_400,
                                            size=48,
                                        ),
                                        ft.Text(
                                            "No upcoming deadlines",
                                            color=GRAY_500,
                                            size=14,
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=12,
                                ),
                                padding=ft.padding.all(32),
                            )
                        ],
                        spacing=8,
                    ),
                ],
                spacing=0,
            ),
            padding=ft.padding.all(16),
            bgcolor=WHITE,
            margin=ft.margin.symmetric(horizontal=16, vertical=8),
            border_radius=12,
            border=ft.border.all(1, GRAY_200),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color="#00000010",
                offset=ft.Offset(0, 1),
            ),
        )
    
    def _build_deadline_item(self, deadline: Dict[str, Any]) -> ft.Container:
        """Build individual deadline item matching Django design"""
        title = deadline.get('title', 'Unknown Deadline')
        case_name = deadline.get('case_name', 'Unknown Case')
        due_date = deadline.get('due_date', '')
        priority = deadline.get('priority', 'medium')
        
        # Priority colors
        priority_colors = {
            'high': RED_600,
            'medium': YELLOW_600,
            'low': GREEN_600,
        }
        priority_bg_colors = {
            'high': RED_50,
            'medium': YELLOW_50,
            'low': GREEN_50,
        }
        
        # Format due date
        if isinstance(due_date, str):
            try:
                due_datetime = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                due_str = due_datetime.strftime('%b %d, %Y')
                days_left = (due_datetime - datetime.now()).days
                if days_left < 0:
                    days_str = f"{abs(days_left)} days overdue"
                elif days_left == 0:
                    days_str = "Today"
                elif days_left == 1:
                    days_str = "Tomorrow"
                else:
                    days_str = f"{days_left} days"
            except:
                due_str = due_date
                days_str = "Unknown"
        else:
            due_str = "Unknown date"
            days_str = "Unknown"

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.ALARM_OUTLINED,
                                    color=priority_colors.get(priority, GRAY_600),
                                    size=20,
                                ),
                                width=40,
                                height=40,
                                bgcolor=priority_bg_colors.get(priority, GRAY_100),
                                border_radius=20,
                                alignment=ft.alignment.center,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        title,
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                        color=GRAY_900,
                                    ),
                                    ft.Text(
                                        case_name,
                                        size=12,
                                        color=GRAY_600,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            days_str,
                                            size=12,
                                            weight=ft.FontWeight.W_500,
                                            color=priority_colors.get(priority, GRAY_600),
                                            text_align=ft.TextAlign.RIGHT,
                                        ),
                                        ft.Container(
                                            content=ft.Text(
                                                priority.title(),
                                                size=10,
                                                weight=ft.FontWeight.W_500,
                                                color=WHITE,
                                            ),
                                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                            bgcolor=priority_colors.get(priority, GRAY_600),
                                            border_radius=12,
                                        ),
                                    ],
                                    spacing=4,
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(
                        content=ft.Text(
                            due_str,
                            size=11,
                            color=GRAY_500,
                        ),
                        padding=ft.padding.only(left=56),
                    ),
                ],
                spacing=8,
            ),
            padding=ft.padding.all(12),
            border=ft.border.all(1, GRAY_200),
            border_radius=8,
            bgcolor=WHITE,
        )
    
    def _build_quick_actions(self) -> ft.Container:
        """Build quick actions section matching Django design"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Quick Actions",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=GRAY_900,
                    ),
                    ft.Row(
                        controls=[
                            self._build_action_button(
                                "New Appointment",
                                ft.Icons.CALENDAR_TODAY_OUTLINED,
                                BLUE_600,
                                self._new_appointment,
                            ),
                            self._build_action_button(
                                "Add Client",
                                ft.Icons.PERSON_ADD_OUTLINED,
                                GREEN_600,
                                self._add_client,
                            ),
                            self._build_action_button(
                                "Create Case",
                                ft.Icons.ADD_TASK_OUTLINED,
                                YELLOW_600,
                                self._create_case,
                            ),
                        ],
                        spacing=12,
                    ),
                ],
                spacing=16,
            ),
            padding=ft.padding.all(16),
            bgcolor=WHITE,
            margin=ft.margin.symmetric(horizontal=16, vertical=8),
            border_radius=12,
            border=ft.border.all(1, GRAY_200),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color="#00000010",
                offset=ft.Offset(0, 1),
            ),
        )
    
    def _build_action_button(self, label: str, icon, color: str, on_click) -> ft.Container:
        """Build individual action button"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Icon(
                            icon,
                            color=color,
                            size=24,
                        ),
                        width=56,
                        height=56,
                        bgcolor=f"{color}15",
                        border_radius=16,
                        alignment=ft.alignment.center,
                    ),
                    ft.Text(
                        label,
                        size=12,
                        weight=ft.FontWeight.W_500,
                        color=GRAY_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            on_click=on_click,
            expand=True,
        )
    
    async def load_data(self):
        """Load dashboard data"""
        self.loading = True
        
        try:
            # Load stats
            self.stats_data = await self.api_client.get_dashboard_stats()
            
            # Load recent appointments
            self.appointments_data = await self.api_client.get_appointments()
            
            # Load upcoming deadlines (mock data for now)
            self.upcoming_deadlines = self.stats_data.get('upcoming_deadlines', [])
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            # Use mock data as fallback
            self.stats_data = {
                'total_clients': 156,
                'active_cases': 42,
                'today_appointments': 8,
                'pending_tasks': 23,
            }
            self.appointments_data = [
                {
                    'id': 1,
                    'title': 'Client Consultation',
                    'client_name': 'Alice Johnson',
                    'date': '2024-01-15',
                    'time': '10:00 AM',
                    'status': 'scheduled'
                },
                {
                    'id': 2,
                    'title': 'Case Review',
                    'client_name': 'Bob Smith',
                    'date': '2024-01-15',
                    'time': '2:00 PM',
                    'status': 'confirmed'
                }
            ]
            self.upcoming_deadlines = [
                {
                    'id': 1,
                    'title': 'File Motion',
                    'case_name': 'Smith vs. Jones',
                    'due_date': '2024-01-20',
                    'priority': 'high'
                }
            ]
        finally:
            self.loading = False
            self.page.update()
    
    def _handle_notifications(self, e):
        """Handle notifications click"""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text("Notifications coming soon!"),
                bgcolor=BLUE_600,
            )
        )
    
    def _view_all_appointments(self, e):
        """Navigate to appointments"""
        self.page.go("/appointments")
    
    def _view_all_deadlines(self, e):
        """Navigate to deadlines"""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text("Deadlines view coming soon!"),
                bgcolor=BLUE_600,
            )
        )
    
    def _new_appointment(self, e):
        """Create new appointment"""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text("New appointment form coming soon!"),
                bgcolor=BLUE_600,
            )
        )
    
    def _add_client(self, e):
        """Add new client"""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text("Add client form coming soon!"),
                bgcolor=BLUE_600,
            )
        )
    
    def _create_case(self, e):
        """Create new case"""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text("Create case form coming soon!"),
                bgcolor=BLUE_600,
            )
        )
