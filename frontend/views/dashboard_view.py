import flet as ft
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio

# Import base view and components
from .base_view import BaseView
from components.stats_card import StatsCard
from components.appointment_card import AppointmentCard
from components.case_card import CaseCard

# Import services and config
from services.api_client import api_client, auth_service
from config import Config

class DashboardView(BaseView):
    """Dashboard view showing overview and important information"""
    
    def __init__(self, app):
        super().__init__(app)
        self.stats = {}
        self.upcoming_appointments = []
        self.recent_cases = []
        self.tasks = []
        self.is_loading = True
        self.error = None
    
    async def initialize(self):
        """Initialize the dashboard data"""
        await self.load_data()
    
    async def load_data(self):
        """Load dashboard data from the API"""
        self.is_loading = True
        self.error = None
        
        try:
            # Load data in parallel
            await asyncio.gather(
                self.load_stats(),
                self.load_upcoming_appointments(),
                self.load_recent_cases(),
                self.load_tasks(),
            )
        except Exception as e:
            logger.error(f"Error loading dashboard data: {str(e)}")
            self.error = str(e)
        finally:
            self.is_loading = False
            await self.page.update_async()
    
    async def load_stats(self):
        """Load dashboard statistics"""
        try:
            # Get stats from the API
            response = await api_client.get('dashboard/stats/')
            self.stats = response.get('stats', {})
        except Exception as e:
            logger.error(f"Error loading stats: {str(e)}")
            self.stats = {}
    
    async def load_upcoming_appointments(self):
        """Load upcoming appointments"""
        try:
            # Get upcoming appointments from the API
            today = datetime.now().date()
            next_week = today + timedelta(days=7)
            
            params = {
                'start_date': today.isoformat(),
                'end_date': next_week.isoformat(),
                'status': 'scheduled,confirmed',
                'ordering': 'start_time',
                'page_size': 5,
            }
            
            response = await api_client.get('appointments/', params=params)
            self.upcoming_appointments = response.get('results', [])
        except Exception as e:
            logger.error(f"Error loading upcoming appointments: {str(e)}")
            self.upcoming_appointments = []
    
    async def load_recent_cases(self):
        """Load recent cases"""
        try:
            # Get recent cases from the API
            params = {
                'ordering': '-created_at',
                'page_size': 5,
            }
            
            response = await api_client.get('cases/', params=params)
            self.recent_cases = response.get('results', [])
        except Exception as e:
            logger.error(f"Error loading recent cases: {str(e)}")
            self.recent_cases = []
    
    async def load_tasks(self):
        """Load user tasks"""
        try:
            # Get user tasks from the API
            params = {
                'assigned_to': 'me',
                'status': 'pending,in_progress',
                'ordering': 'due_date',
                'page_size': 5,
            }
            
            response = await api_client.get('tasks/', params=params)
            self.tasks = response.get('results', [])
        except Exception as e:
            logger.error(f"Error loading tasks: {str(e)}")
            self.tasks = []
    
    def build_stats_cards(self) -> ft.Row:
        """Build the stats cards row"""
        stats = [
            {
                'title': 'Active Cases',
                'value': self.stats.get('active_cases', 0),
                'icon': ft.icons.CASE,
                'color': Config.COLORS['primary'],
                'trend': self.stats.get('cases_trend', 0),
            },
            {
                'title': 'Upcoming Appointments',
                'value': self.stats.get('upcoming_appointments', 0),
                'icon': ft.icons.CALENDAR_TODAY,
                'color': Config.COLORS['success'],
                'trend': self.stats.get('appointments_trend', 0),
            },
            {
                'title': 'Pending Tasks',
                'value': self.stats.get('pending_tasks', 0),
                'icon': ft.icons.CHECK_CIRCLE_OUTLINE,
                'color': Config.COLORS['warning'],
                'trend': self.stats.get('tasks_trend', 0),
            },
            {
                'title': 'Unpaid Invoices',
                'value': self.stats.get('unpaid_invoices', 0),
                'icon': ft.icons.ATTACH_MONEY,
                'color': Config.COLORS['error'],
                'trend': self.stats.get('invoices_trend', 0),
                'formatter': 'currency',
            },
        ]
        
        return ft.ResponsiveRow(
            [
                ft.Container(
                    content=StatsCard(**stat),
                    col={"sm": 12, "md": 6, "lg": 3},
                    padding=8,
                )
                for stat in stats
            ],
            spacing=8,
        )
    
    def build_upcoming_appointments(self) -> ft.Container:
        """Build the upcoming appointments section"""
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "Upcoming Appointments",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(expand=True),
                    ft.TextButton(
                        "View All",
                        on_click=lambda _: self.go_to('/appointments'),
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.GREY_200),
            border_radius=ft.border_radius.only(top_left=8, top_right=8),
        )
        
        if not self.upcoming_appointments:
            content = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            ft.icons.CALENDAR_TODAY,
                            size=48,
                            color=ft.colors.GREY_400,
                        ),
                        ft.Text(
                            "No upcoming appointments",
                            size=16,
                            color=ft.colors.GREY_600,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(
                            "You don't have any appointments scheduled for the next 7 days.",
                            size=14,
                            color=ft.colors.GREY_500,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                padding=40,
                bgcolor=ft.colors.WHITE,
                border=ft.border.all(1, ft.colors.GREY_200),
                border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
                border_top=ft.border.BorderSide(0, ft.colors.TRANSPARENT),
            )
        else:
            content = ft.Column(
                [
                    ft.Container(
                        content=AppointmentCard(appt),
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        border_bottom=ft.border.all(1, ft.colors.GREY_200),
                    )
                    for appt in self.upcoming_appointments
                ],
                spacing=0,
            )
            
            content = ft.Container(
                content=content,
                bgcolor=ft.colors.WHITE,
                border=ft.border.all(1, ft.colors.GREY_200),
                border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
                border_top=ft.border.BorderSide(0, ft.colors.TRANSPARENT),
            )
        
        return ft.Column(
            [header, content],
            spacing=0,
        )
    
    def build_recent_cases(self) -> ft.Container:
        """Build the recent cases section"""
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "Recent Cases",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(expand=True),
                    ft.TextButton(
                        "View All",
                        on_click=lambda _: self.go_to('/cases'),
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.GREY_200),
            border_radius=ft.border_radius.only(top_left=8, top_right=8),
        )
        
        if not self.recent_cases:
            content = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            ft.icons.CASE,
                            size=48,
                            color=ft.colors.GREY_400,
                        ),
                        ft.Text(
                            "No recent cases",
                            size=16,
                            color=ft.colors.GREY_600,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(
                            "You don't have any recent cases.",
                            size=14,
                            color=ft.colors.GREY_500,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                padding=40,
                bgcolor=ft.colors.WHITE,
                border=ft.border.all(1, ft.colors.GREY_200),
                border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
                border_top=ft.border.BorderSide(0, ft.colors.TRANSPARENT),
            )
        else:
            content = ft.Column(
                [
                    ft.Container(
                        content=CaseCard(case),
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        border_bottom=ft.border.all(1, ft.colors.GREY_200),
                    )
                    for case in self.recent_cases
                ],
                spacing=0,
            )
            
            content = ft.Container(
                content=content,
                bgcolor=ft.colors.WHITE,
                border=ft.border.all(1, ft.colors.GREY_200),
                border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
                border_top=ft.border.BorderSide(0, ft.colors.TRANSPARENT),
            )
        
        return ft.Column(
            [header, content],
            spacing=0,
        )
    
    def build_tasks_section(self) -> ft.Container:
        """Build the tasks section"""
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "My Tasks",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(expand=True),
                    ft.TextButton(
                        "View All",
                        on_click=lambda _: self.go_to('/tasks'),
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.GREY_200),
            border_radius=ft.border_radius.only(top_left=8, top_right=8),
        )
        
        if not self.tasks:
            content = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            ft.icons.CHECK_CIRCLE_OUTLINE,
                            size=48,
                            color=ft.colors.GREY_400,
                        ),
                        ft.Text(
                            "No tasks",
                            size=16,
                            color=ft.colors.GREY_600,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(
                            "You don't have any pending tasks.",
                            size=14,
                            color=ft.colors.GREY_500,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                padding=40,
                bgcolor=ft.colors.WHITE,
                border=ft.border.all(1, ft.colors.GREY_200),
                border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
                border_top=ft.border.BorderSide(0, ft.colors.TRANSPARENT),
            )
        else:
            task_items = []
            for task in self.tasks:
                task_items.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Checkbox(
                                    value=task.get('status') == 'completed',
                                    on_change=lambda e, t=task: self.toggle_task_status(e, t),
                                    tooltip="Mark as completed" if task.get('status') != 'completed' else "Mark as pending",
                                ),
                                ft.Text(
                                    task.get('title', 'Untitled Task'),
                                    expand=True,
                                    style=ft.TextStyle(
                                        decoration=ft.TextDecoration.LINE_THROUGH if task.get('status') == 'completed' else None,
                                        color=ft.colors.GREY_700 if task.get('status') == 'completed' else ft.colors.BLACK,
                                    ),
                                ),
                                ft.PopupMenuButton(
                                    icon=ft.icons.MORE_VERT,
                                    tooltip="Task actions",
                                    items=[
                                        ft.PopupMenuItem(
                                            text="Edit",
                                            icon=ft.icons.EDIT,
                                            on_click=lambda e, t=task: self.go_to(f"/tasks/{t['id']}/edit"),
                                        ),
                                        ft.PopupMenuItem(
                                            text="Delete",
                                            icon=ft.icons.DELETE,
                                            on_click=lambda e, t=task: self.confirm_delete_task(t),
                                        ),
                                    ],
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        border_bottom=ft.border.all(1, ft.colors.GREY_200),
                    )
                )
            
            content = ft.Column(
                task_items,
                spacing=0,
            )
            
            content = ft.Container(
                content=content,
                bgcolor=ft.colors.WHITE,
                border=ft.border.all(1, ft.colors.GREY_200),
                border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
                border_top=ft.border.BorderSide(0, ft.colors.TRANSPARENT),
            )
        
        return ft.Column(
            [header, content],
            spacing=0,
        )
    
    async def toggle_task_status(self, e, task):
        """Toggle task status between completed and pending"""
        try:
            new_status = 'completed' if task.get('status') != 'completed' else 'pending'
            
            # Update task status via API
            await api_client.patch(
                f"tasks/{task['id']}/",
                data={
                    'status': new_status,
                },
            )
            
            # Update local task status
            task['status'] = new_status
            
            # Show success message
            await self.show_snackbar(
                f"Task marked as {new_status}",
                color=Config.COLORS['success'],
            )
            
            # Refresh the tasks list
            await self.load_tasks()
            await self.page.update_async()
            
        except Exception as e:
            logger.error(f"Error toggling task status: {str(e)}")
            await self.show_snackbar(
                f"Error updating task: {str(e)}",
                color=Config.COLORS['error'],
            )
    
    def show_task_menu(self, e, task):
        """Show task context menu"""
        e.control.show_menu = True
        self.page.update()
    
    async def confirm_delete_task(self, task):
        """Show confirmation dialog before deleting a task"""
        def on_confirm():
            self.page.close_dialog()
            self._delete_task(task)
        
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Delete Task"),
            content=ft.Text(f"Are you sure you want to delete the task '{task.get('title')}'?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.page.close_dialog()),
                ft.TextButton("Delete", on_click=lambda _: on_confirm()),
            ],
        )
        self.page.dialog.open = True
        await self.page.update_async()
    
    async def _delete_task(self, task):
        """Delete a task"""
        try:
            # Delete task via API
            await api_client.delete(f"tasks/{task['id']}/")
            
            # Remove task from local list
            self.tasks = [t for t in self.tasks if t['id'] != task['id']]
            
            # Show success message
            await self.show_snackbar(
                "Task deleted successfully",
                color=Config.COLORS['success'],
            )
            
            # Update the UI
            await self.page.update_async()
            
        except Exception as e:
            logger.error(f"Error deleting task: {str(e)}")
            await self.show_snackbar(
                f"Error deleting task: {str(e)}",
                color=Config.COLORS['error'],
            )
    
    def build_quick_actions(self) -> ft.Container:
        """Build the quick actions section"""
        actions = [
            {
                'icon': ft.icons.ADD,
                'label': 'New Case',
                'color': Config.COLORS['primary'],
                'on_click': lambda _: self.go_to('/cases/new'),
            },
            {
                'icon': ft.icons.ADD_ALARM,
                'label': 'New Appointment',
                'color': Config.COLORS['success'],
                'on_click': lambda _: self.go_to('/appointments/new'),
            },
            {
                'icon': ft.icons.ASSIGNMENT_ADD,
                'label': 'New Task',
                'color': Config.COLORS['warning'],
                'on_click': lambda _: self.go_to('/tasks/new'),
            },
            {
                'icon': ft.icons.RECEIPT,
                'label': 'New Invoice',
                'color': Config.COLORS['error'],
                'on_click': lambda _: self.go_to('/invoices/new'),
            },
        ]
        
        action_buttons = []
        for action in actions:
            action_buttons.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                content=ft.Icon(
                                    action['icon'],
                                    size=24,
                                    color=ft.colors.WHITE,
                                ),
                                padding=12,
                                bgcolor=action['color'],
                                border_radius=12,
                            ),
                            ft.Text(
                                action['label'],
                                size=12,
                                text_align=ft.TextAlign.CENTER,
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    on_click=action['on_click'],
                    padding=8,
                    border_radius=8,
                    tooltip=action['label'],
                    ink=True,
                )
            )
        
        return ft.Container(
            content=ft.ResponsiveRow(
                action_buttons,
                spacing=16,
                run_spacing=16,
            ),
            padding=16,
            bgcolor=ft.colors.WHITE,
            border_radius=8,
            border=ft.border.all(1, ft.colors.GREY_200),
            margin=ft.margin.only(bottom=16),
        )
    
    def build(self) -> ft.Container:
        """Build the dashboard view"""
        if self.is_loading:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.ProgressRing(),
                        ft.Text("Loading dashboard..."),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                ),
                alignment=ft.alignment.center,
            )
        
        if self.error:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            ft.icons.ERROR_OUTLINE,
                            size=48,
                            color=Config.COLORS['error'],
                        ),
                        ft.Text(
                            "Error loading dashboard",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=Config.COLORS['error'],
                        ),
                        ft.Text(
                            self.error,
                            size=14,
                            color=ft.colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.ElevatedButton(
                            "Retry",
                            on_click=lambda _: self.initialize(),
                            icon=ft.icons.REFRESH,
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
        
        return ft.Container(
            content=ft.Column(
                [
                    # Quick actions
                    self.build_quick_actions(),
                    
                    # Stats cards
                    self.build_stats_cards(),
                    
                    # Main content
                    ft.ResponsiveRow(
                        [
                            # Left column
                            ft.Container(
                                content=ft.Column(
                                    [
                                        # Upcoming appointments
                                        self.build_upcoming_appointments(),
                                        
                                        # Recent cases
                                        ft.Container(height=16),  # Spacer
                                        self.build_recent_cases(),
                                    ],
                                    spacing=16,
                                    expand=True,
                                ),
                                col={"sm": 12, "lg": 8},
                                padding=ft.padding.only(right=8),
                            ),
                            
                            # Right column
                            ft.Container(
                                content=ft.Column(
                                    [
                                        # Tasks
                                        self.build_tasks_section(),
                                    ],
                                    spacing=16,
                                ),
                                col={"sm": 12, "lg": 4},
                                padding=ft.padding.only(left=8),
                            ),
                        ],
                        spacing=0,
                    ),
                ],
                spacing=16,
                expand=True,
            ),
            padding=16,
        )


# For testing the view directly
if __name__ == "__main__":
    import logging
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Mock the API client for testing
    class MockApiClient:
        async def get(self, endpoint, params=None):
            if 'stats' in endpoint:
                return {
                    'stats': {
                        'active_cases': 12,
                        'upcoming_appointments': 5,
                        'pending_tasks': 8,
                        'unpaid_invoices': 3,
                        'cases_trend': 2,
                        'appointments_trend': -1,
                        'tasks_trend': 0,
                        'invoices_trend': 1,
                    }
                }
            elif 'appointments' in endpoint:
                return {
                    'results': [],
                }
            elif 'cases' in endpoint:
                return {
                    'results': [],
                }
            elif 'tasks' in endpoint:
                return {
                    'results': [],
                }
            return {}
    
    # Mock the auth service
    class MockAuthService:
        async def login(self, username, password):
            return {'access': 'mock_token', 'refresh': 'mock_refresh_token'}
    
    # Set up the test app
    async def main(page: ft.Page):
        # Configure page
        page.title = "Lawyer Office - Dashboard"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        
        # Set up API client and auth service
        api_client = MockApiClient()
        auth_service = MockAuthService()
        
        # Create and initialize the view
        view = DashboardView(page)
        await view.initialize()
        
        # Add the view to the page
        page.add(view.build())
        
        # Update the page
        await page.update_async()
    
    # Run the app
    ft.app(target=main)
