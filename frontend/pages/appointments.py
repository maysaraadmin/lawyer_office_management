import flet as ft
from datetime import datetime, timedelta
from ..services.api_client import api_client
from .base_page import BasePage
from ..components.appointment_card import AppointmentCard

class AppointmentsPage(BasePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.page.title = "Appointments - Lawyer Office Management"
        self.appointments = []
        self.filtered_appointments = []
        self.current_view = "list"  # 'list' or 'calendar'
        self.selected_date = datetime.now().date()
        
        # UI Components
        self.appointment_list = ft.ListView(expand=True, spacing=10, padding=10)
        self.calendar_view = ft.Container(expand=True)
        
        # Search and filter controls
        self.search_field = ft.TextField(
            label="Search appointments...",
            prefix_icon=ft.icons.SEARCH,
            on_submit=self.search_appointments,
            expand=True,
        )
        
        # Date picker
        self.date_picker = ft.DatePicker(
            first_date=datetime.now() - timedelta(days=365),
            last_date=datetime.now() + timedelta(days=365),
            on_change=self.on_date_selected,
        )
        self.page.overlay.append(self.date_picker)
    
    async def initialize(self):
        """Initialize the appointments page"""
        if not await self.check_auth():
            return
            
        self.setup_app_bar()
        self.setup_drawer()
        self.show_loading("Loading appointments...")
        
        try:
            await self.load_appointments()
            await self.build_ui()
        except Exception as e:
            await self.handle_error(e, "Failed to load appointments")
    
    async def load_appointments(self, start_date=None, end_date=None):
        """Load appointments from the API"""
        try:
            params = {}
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()
                
            response = await api_client.get("appointments/", params=params)
            self.appointments = response.get("results", [])
            self.filtered_appointments = self.appointments.copy()
            
        except Exception as e:
            await self.handle_error(e, "Failed to load appointments")
            self.appointments = []
            self.filtered_appointments = []
    
    async def search_appointments(self, e):
        """Search appointments by keyword"""
        query = self.search_field.value.strip().lower()
        if not query:
            self.filtered_appointments = self.appointments.copy()
        else:
            self.filtered_appointments = [
                apt for apt in self.appointments
                if (query in apt.get('title', '').lower() or
                    query in apt.get('client_name', '').lower() or
                    query in apt.get('case_name', '').lower() or
                    query in apt.get('location', '').lower() or
                    query in apt.get('notes', '').lower())
            ]
        await self.update_appointment_list()
    
    async def on_date_selected(self, e):
        """Handle date selection from date picker"""
        if e.control.value:
            self.selected_date = e.control.value
            await self.load_appointments(
                start_date=datetime.combine(self.selected_date, datetime.min.time()),
                end_date=datetime.combine(self.selected_date, datetime.max.time())
            )
            await self.update_appointment_list()
    
    async def build_ui(self):
        """Build the UI components"""
        # Clear existing content
        self.page.clean()
        
        # Rebuild app bar and drawer
        self.setup_app_bar()
        self.setup_drawer()
        
        # Create header with actions
        header = ft.Row(
            [
                ft.Text("Appointments", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "New Appointment",
                            icon=ft.icons.ADD,
                            on_click=self.create_appointment,
                        ),
                        ft.IconButton(
                            icon=ft.icons.CALENDAR_TODAY,
                            tooltip="Today",
                            on_click=self.go_to_today,
                        ),
                        ft.IconButton(
                            icon=ft.icons.VIEW_LIST if self.current_view == "calendar" else ft.icons.CALENDAR_VIEW_MONTH,
                            tooltip=f"Switch to {'Calendar' if self.current_view == 'list' else 'List'} View",
                            on_click=self.toggle_view,
                        ),
                    ],
                    spacing=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # Build the filter row
        filter_row = ft.Row(
            [
                self.search_field,
                ft.ElevatedButton(
                    text=self.selected_date.strftime("%b %d, %Y"),
                    icon=ft.icons.CALENDAR_TODAY,
                    on_click=lambda _: self.date_picker.pick_date(),
                ),
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
                    on_change=self.filter_by_status,
                ),
                ft.Dropdown(
                    label="Type",
                    options=[
                        ft.dropdown.Option("All"),
                        ft.dropdown.Option("Consultation"),
                        ft.dropdown.Option("Court Date"),
                        ft.dropdown.Option("Meeting"),
                        ft.dropdown.Option("Other"),
                    ],
                    value="All",
                    width=150,
                    on_change=self.filter_by_type,
                ),
            ],
            spacing=10,
        )
        
        # Build the main content
        content = ft.Column(
            [
                header,
                ft.Divider(),
                filter_row,
                ft.Container(
                    content=self.appointment_list if self.current_view == "list" else self.calendar_view,
                    expand=True,
                ),
            ],
            expand=True,
            spacing=20,
        )
        
        # Update the appointment list
        await self.update_appointment_list()
        
        # Add content to page
        self.page.add(content)
        self.page.update()
    
    async def update_appointment_list(self):
        """Update the appointment list view"""
        if self.current_view == "list":
            self.appointment_list.controls = []
            
            if not self.filtered_appointments:
                self.appointment_list.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.icons.EVENT_AVAILABLE, size=48, color=ft.colors.GREY_400),
                                ft.Text("No appointments found"),
                                ft.ElevatedButton(
                                    "Schedule an Appointment",
                                    on_click=self.create_appointment,
                                )
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=16,
                        ),
                        padding=40,
                        alignment=ft.alignment.center,
                    )
                )
            else:
                for appointment in self.filtered_appointments:
                    self.appointment_list.controls.append(
                        AppointmentCard(
                            appointment=appointment,
                            on_click=lambda _, id=appointment.get('id'): self.view_appointment(id),
                            on_edit=lambda _, id=appointment.get('id'): self.edit_appointment(id),
                            on_delete=lambda _, id=appointment.get('id'): self.delete_appointment(id),
                        )
                    )
            
            self.page.update()
        else:
            # Update calendar view (to be implemented)
            pass
    
    async def toggle_view(self, _):
        """Toggle between list and calendar view"""
        self.current_view = "calendar" if self.current_view == "list" else "list"
        await self.build_ui()
    
    async def go_to_today(self, _):
        """Navigate to today's date"""
        today = datetime.now().date()
        if self.selected_date != today:
            self.selected_date = today
            await self.load_appointments(
                start_date=datetime.combine(today, datetime.min.time()),
                end_date=datetime.combine(today, datetime.max.time())
            )
            await self.build_ui()
    
    async def filter_by_status(self, e):
        """Filter appointments by status"""
        status = e.control.value
        if status == "All":
            self.filtered_appointments = self.appointments.copy()
        else:
            self.filtered_appointments = [
                apt for apt in self.appointments
                if apt.get('status', '').lower() == status.lower()
            ]
        await self.update_appointment_list()
    
    async def filter_by_type(self, e):
        """Filter appointments by type"""
        apt_type = e.control.value
        if apt_type == "All":
            self.filtered_appointments = self.appointments.copy()
        else:
            self.filtered_appointments = [
                apt for apt in self.appointments
                if apt.get('appointment_type', '').lower() == apt_type.lower()
            ]
        await self.update_appointment_list()
    
    async def create_appointment(self, _=None):
        """Navigate to create appointment page"""
        self.page.go("/appointments/new")
    
    async def view_appointment(self, appointment_id: str):
        """View appointment details"""
        self.page.go(f"/appointments/{appointment_id}")
    
    async def edit_appointment(self, appointment_id: str):
        """Edit an appointment"""
        self.page.go(f"/appointments/{appointment_id}/edit")
    
    async def delete_appointment(self, appointment_id: str):
        """Delete an appointment"""
        # Confirm deletion
        def close_dialog(_):
            dlg_modal.open = False
            self.page.update()
        
        def delete_and_close(_):
            close_dialog(None)
            self._delete_appointment_confirm(appointment_id)
        
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete"),
            content=ft.Text("Are you sure you want to delete this appointment?"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Delete", on_click=delete_and_close, style=ft.ButtonStyle(color=ft.colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dlg_modal
        dlg_modal.open = True
        self.page.update()
    
    async def _delete_appointment_confirm(self, appointment_id: str):
        """Confirm and delete the appointment"""
        try:
            await api_client.delete(f"appointments/{appointment_id}/")
            # Remove from local list
            self.appointments = [apt for apt in self.appointments if apt.get('id') != appointment_id]
            self.filtered_appointments = [apt for apt in self.filtered_appointments if apt.get('id') != appointment_id]
            
            # Update UI
            await self.update_appointment_list()
            self.show_snackbar("Appointment deleted successfully", ft.colors.GREEN)
            
        except Exception as e:
            await self.handle_error(e, "Failed to delete appointment")

async def appointments_page(page: ft.Page):
    """Create and initialize the appointments page"""
    appointments = AppointmentsPage(page)
    await appointments.initialize()
    return appointments
