import flet as ft
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio

# Import base view
from .base_view import BaseView

class AppointmentsView(BaseView):
    """View for managing appointments"""
    
    def __init__(self, app):
        super().__init__(app)
        self.appointments = []
        self.is_loading = True
        self.error = None
        self.selected_date = datetime.now().date()
    
    async def initialize(self):
        """Initialize the appointments data"""
        await self.load_appointments()
    
    async def load_appointments(self):
        """Load appointments from the API"""
        self.is_loading = True
        self.error = None
        
        try:
            # Get appointments from the API for the selected date
            start_date = self.selected_date
            end_date = self.selected_date + timedelta(days=1)
            
            params = {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'ordering': 'start_time',
            }
            
            response = await self.app.api_client.get('appointments/', params=params)
            self.appointments = response.get('results', [])
        except Exception as e:
            logger.error(f"Error loading appointments: {str(e)}")
            self.error = str(e)
        finally:
            self.is_loading = False
            await self.page.update_async()
    
    async def change_date(self, delta_days):
        """Change the selected date by the given number of days"""
        self.selected_date += timedelta(days=delta_days)
        await self.load_appointments()
    
    def build(self) -> ft.Container:
        """Build the appointments view"""
        if self.is_loading:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.ProgressRing(),
                        ft.Text("Loading appointments..."),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
        
        if self.error:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            "ERROR_OUTLINE",
                            size=48,
                            color="#F44336",  # Red
                        ),
                        ft.Text(
                            "Error loading appointments",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="#F44336",  # Red
                        ),
                        ft.Text(
                            self.error,
                            size=14,
                            color="#757575",  # Grey 600
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.ElevatedButton(
                            "Retry",
                            on_click=lambda _: self.initialize(),
                            icon="REFRESH",
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
        
        # Build calendar header
        date_header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon="CHEVRON_LEFT",
                        on_click=lambda _: self.change_date(-1),
                        tooltip="Previous day",
                    ),
                    ft.Text(
                        self.selected_date.strftime("%A, %B %d, %Y"),
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.IconButton(
                        icon="CHEVRON_RIGHT",
                        on_click=lambda _: self.change_date(1),
                        tooltip="Next day",
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Today",
                        on_click=lambda _: self.change_date(0),
                        icon="TODAY",
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(bottom=16),
        )
        
        # Build time slots
        time_slots = ft.Column(spacing=0, expand=True)
        
        # Generate time slots from 8 AM to 8 PM
        start_hour = 8
        end_hour = 20
        
        for hour in range(start_hour, end_hour + 1):
            for minute in [0, 30]:  # Half-hour slots
                if hour == end_hour and minute == 30:
                    break  # Skip 8:30 PM
                    
                time_str = f"{hour:02d}:{minute:02d}"
                time_dt = datetime.strptime(time_str, "%H:%M")
                
                # Find appointments for this time slot
                slot_appointments = [
                    appt for appt in self.appointments
                    if self._is_appointment_in_slot(appt, time_dt)
                ]
                
                # Create time slot row
                time_slot = ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Text(
                                    time_dt.strftime("%I:%M %p"),
                                    size=12,
                                    color="#757575",  # Grey 600
                                ),
                                width=80,
                                padding=ft.padding.only(right=8),
                            ),
                            self._build_appointments_row(slot_appointments, time_dt),
                        ],
                        spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, "#E0E0E0")),  # Grey 300
                    padding=ft.padding.symmetric(vertical=8),
                )
                
                time_slots.controls.append(time_slot)
        
        return ft.Container(
            content=ft.Column(
                [
                    # Header
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(
                                    "Appointments",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Container(expand=True),
                                ft.ElevatedButton(
                                    "New Appointment",
                                    on_click=lambda _: self.add_appointment(),
                                    icon="ADD",
                                    style=ft.ButtonStyle(
                                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.only(bottom=24),
                    ),
                    
                    # Date navigation
                    date_header,
                    
                    # Calendar view
                    ft.Container(
                        content=time_slots,
                        border=ft.border.all(1, "#E0E0E0"),  # Grey 300
                        border_radius=8,
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            padding=16,
            expand=True,
        )
    
    def _is_appointment_in_slot(self, appointment, time_dt):
        """Check if an appointment falls within the given time slot"""
        try:
            start_time = datetime.strptime(appointment.get('start_time', ''), "%H:%M:%S").time()
            end_time = datetime.strptime(appointment.get('end_time', '23:59:59'), "%H:%M:%S").time()
            
            slot_start = time_dt.time()
            slot_end = (time_dt + timedelta(minutes=30)).time()
            
            return (
                (start_time <= slot_start and end_time > slot_start) or
                (start_time < slot_end and end_time >= slot_end) or
                (start_time >= slot_start and end_time <= slot_end)
            )
        except (ValueError, AttributeError):
            return False
    
    def _build_appointments_row(self, appointments, time_dt):
        """Build a row of appointment cards for the given time slot"""
        if not appointments:
            return ft.Container(expand=True)
        
        appointment_cards = ft.Row(
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        for appt in appointments:
            # Determine status color
            status = appt.get('status', '').lower()
            if status == 'completed':
                color = "#4CAF50"  # Green
            elif status == 'cancelled':
                color = "#F44336"  # Red
            else:
                color = "#2196F3"  # Blue
            
            # Create appointment card
            card = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            appt.get('title', 'Untitled Appointment'),
                            weight=ft.FontWeight.W_500,
                            color=ft.colors.WHITE,
                        ),
                        ft.Text(
                            f"{appt.get('client', {}).get('name', 'No client')} • {appt.get('duration', 30)} min",
                            size=12,
                            color=ft.colors.WHITE70,
                        ),
                    ],
                    spacing=2,
                ),
                padding=ft.padding.all(8),
                bgcolor=color,
                border_radius=4,
                on_click=lambda e, a=appt: self.view_appointment(a),
                tooltip="Click to view details",
                width=200,
            )
            
            appointment_cards.controls.append(card)
        
        return appointment_cards
    
    async def add_appointment(self):
        """Navigate to add appointment form"""
        await self.go_to("/appointments/new")
    
    async def view_appointment(self, appointment):
        """Navigate to appointment details"""
        await self.go_to(f"/appointments/{appointment.get('id')}")
    
    async def edit_appointment(self, appointment):
        """Navigate to edit appointment form"""
        await self.go_to(f"/appointments/{appointment.get('id')}/edit")
