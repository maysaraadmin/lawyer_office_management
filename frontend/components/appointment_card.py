import flet as ft
from datetime import datetime
from typing import Dict, Any, Optional, Callable

class AppointmentCard(ft.Container):
    """A card component for displaying appointment information"""
    
    def __init__(
        self,
        appointment: Dict[str, Any],
        on_tap: Optional[Callable] = None,
        **kwargs
    ):
        """Initialize the appointment card
        
        Args:
            appointment: Dictionary containing appointment data
            on_tap: Callback function when the card is tapped
        """
        self.appointment = appointment
        self.on_tap_callback = on_tap
        
        # Parse the appointment data
        title = appointment.get('title', 'Untitled Appointment')
        client_name = appointment.get('client', {}).get('name', 'No Client')
        
        # Format the date and time
        start_time = self._parse_datetime(appointment.get('start_time'))
        end_time = self._parse_datetime(appointment.get('end_time'))
        
        # Create the time text
        time_text = self._format_time_range(start_time, end_time)
        
        # Create the status indicator
        status = appointment.get('status', 'scheduled').lower()
        status_color = self._get_status_color(status)
        
        # Create the main content
        content = ft.Row(
            [
                # Left side - time and status
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                start_time.strftime('%I:%M') if start_time else '--:--',
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.BLUE_700,
                            ),
                            ft.Text(
                                start_time.strftime('%p').lower() if start_time else '--',
                                size=12,
                                color=ft.colors.GREY_600,
                            ),
                            ft.Container(
                                content=ft.Container(
                                    width=8,
                                    height=8,
                                    border_radius=4,
                                    bgcolor=status_color,
                                ),
                                margin=ft.margin.only(top=4),
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    width=80,
                    padding=8,
                    alignment=ft.alignment.center,
                ),
                
                # Divider
                ft.Container(
                    width=1,
                    height=60,
                    bgcolor=ft.colors.GREY_200,
                    margin=ft.margin.symmetric(horizontal=8),
                ),
                
                # Right side - details
                ft.Column(
                    [
                        # Title and status
                        ft.Row(
                            [
                                ft.Text(
                                    title,
                                    size=16,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.colors.BLACK87,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        status.upper(),
                                        size=10,
                                        color=status_color,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                    bgcolor=f"{status_color}22",
                                    border_radius=12,
                                ),
                            ],
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        
                        # Client and time
                        ft.Text(
                            f"With {client_name}",
                            size=14,
                            color=ft.colors.GREY_700,
                        ),
                        
                        # Location or notes
                        ft.Text(
                            appointment.get('location',
                                (appointment.get('notes', '')[:60] + '...') if len(appointment.get('notes', '')) > 60 
                                else appointment.get('notes', '')
                            ),
                            size=12,
                            color=ft.colors.GREY_600,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                    spacing=4,
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                
                # Chevron icon
                ft.Icon(
                    ft.icons.CHEVRON_RIGHT,
                    size=20,
                    color=ft.colors.GREY_400,
                ),
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        # Initialize the container
        super().__init__(
            content=content,
            padding=12,
            margin=ft.margin.symmetric(vertical=4),
            border_radius=8,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.GREY_200),
            on_click=self._on_tap,
            on_hover=self._on_hover,
            **kwargs
        )
        
        # Store the hover state
        self.is_hovered = False
    
    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse a datetime string into a datetime object"""
        if not dt_str:
            return None
        
        try:
            # Try parsing with timezone
            if 'T' in dt_str and 'Z' in dt_str:
                return datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            # Try parsing without timezone
            return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            return None
    
    def _format_time_range(self, start: Optional[datetime], end: Optional[datetime]) -> str:
        """Format a time range as a string"""
        if not start or not end:
            return "Time not specified"
        
        # Same day
        if start.date() == end.date():
            return (
                f"{start.strftime('%a, %b %d, %Y')} • "
                f"{start.strftime('%-I:%M %p')} - {end.strftime('%-I:%M %p')}"
            )
        
        # Different days
        return (
            f"{start.strftime('%a, %b %d, %I:%M %p')} - "
            f"{end.strftime('%a, %b %d, %I:%M %p')}"
        )
    
    def _get_status_color(self, status: str) -> str:
        """Get the color for a status"""
        status_colors = {
            'scheduled': ft.colors.BLUE,
            'confirmed': ft.colors.GREEN,
            'completed': ft.colors.GREY,
            'cancelled': ft.colors.RED,
            'no_show': ft.colors.ORANGE,
            'rescheduled': ft.colors.PURPLE,
        }
        return status_colors.get(status.lower(), ft.colors.GREY)
    
    def _on_hover(self, e):
        """Handle hover effect"""
        self.is_hovered = e.data == "true"
        self.bgcolor = ft.colors.BLUE_50 if self.is_hovered else ft.colors.WHITE
        self.update()
    
    def _on_tap(self, e):
        """Handle tap/click event"""
        if self.on_tap_callback:
            self.on_tap_callback(e)
