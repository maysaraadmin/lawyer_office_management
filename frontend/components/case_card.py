import flet as ft
from datetime import datetime
from typing import Dict, Any, Optional, Callable

class CaseCard(ft.Container):
    """A card component for displaying case information"""
    
    def __init__(
        self,
        case: Dict[str, Any],
        on_tap: Optional[Callable] = None,
        **kwargs
    ):
        """Initialize the case card
        
        Args:
            case: Dictionary containing case data
            on_tap: Callback function when the card is tapped
        """
        self.case = case
        self.on_tap_callback = on_tap
        
        # Parse the case data
        title = case.get('title', 'Untitled Case')
        case_number = case.get('case_number', 'N/A')
        status = case.get('status', 'open').lower()
        
        # Format dates
        opened_date = self._parse_date(case.get('opened_date'))
        last_updated = self._parse_date(case.get('updated_at'))
        
        # Get status color
        status_color = self._get_status_color(status)
        
        # Create the main content
        content = ft.Row(
            [
                # Left side - case number and status
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                f"#{case_number}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.BLUE_700,
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
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    width=100,
                    padding=8,
                    alignment=ft.alignment.center,
                ),
                
                # Divider
                ft.Container(
                    width=1,
                    height=80,
                    bgcolor=ft.colors.GREY_200,
                    margin=ft.margin.symmetric(horizontal=8),
                ),
                
                # Middle - case details
                ft.Column(
                    [
                        # Title
                        ft.Text(
                            title,
                            size=16,
                            weight=ft.FontWeight.W_500,
                            color=ft.colors.BLACK87,
                        ),
                        
                        # Client and type
                        ft.Text(
                            "Client: " + 
                            f"{case.get('client', {}).get('name', 'N/A')} • {case.get('case_type', 'N/A')}",
                            size=12,
                            color=ft.colors.GREY_700,
                        ),
                        
                        # Description
                        ft.Text(
                            (case['description'][:100] + '...') if len(case.get('description', '')) > 100 
                            else case.get('description', ''),
                            size=12,
                            color=ft.colors.GREY_600,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ) if case.get('description') else ft.Container(),
                        
                        # Dates
                        ft.Row(
                            [
                                ft.Text(
                                    f"Opened: {opened_date}",
                                    size=10,
                                    color=ft.colors.GREY_500,
                                ),
                                ft.Text(
                                    "•",
                                    size=10,
                                    color=ft.colors.GREY_400,
                                ),
                                ft.Text(
                                    f"Updated: {last_updated}",
                                    size=10,
                                    color=ft.colors.GREY_500,
                                ),
                            ],
                            spacing=4,
                        ),
                    ],
                    spacing=4,
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                
                # Right side - actions
                ft.Row(
                    [
                        # Next court date if available
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Next Court",
                                        size=10,
                                        color=ft.colors.GREY_600,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Text(
                                        self._parse_date(case.get('next_court_date'), 'N/A'),
                                        size=12,
                                        color=ft.colors.BLUE_700,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=2,
                            ),
                            padding=8,
                            border_radius=8,
                            bgcolor=ft.colors.BLUE_50,
                            visible=bool(case.get('next_court_date')),
                        ),
                        
                        # Chevron icon
                        ft.IconButton(
                            icon=ft.icons.CHEVRON_RIGHT,
                            icon_size=20,
                            icon_color=ft.colors.GREY_400,
                            on_click=self._on_tap,
                        ),
                    ],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.END,
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
    
    def _parse_date(self, date_str: Optional[str], default: str = 'N/A') -> str:
        """Parse a date string into a readable format"""
        if not date_str:
            return default
        
        try:
            # Try parsing with timezone
            if 'T' in date_str and 'Z' in date_str:
                dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                # Try parsing without timezone
                dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            
            # Format as 'MMM d, YYYY' (e.g., 'Jan 1, 2023')
            return dt.strftime('%b %-d, %Y')
        except (ValueError, TypeError):
            return default
    
    def _get_status_color(self, status: str) -> str:
        """Get the color for a status"""
        status_colors = {
            'open': ft.colors.BLUE,
            'active': ft.colors.GREEN,
            'pending': ft.colors.ORANGE,
            'closed': ft.colors.GREY,
            'dismissed': ft.colors.PURPLE,
            'settled': ft.colors.TEAL,
            'trial': ft.colors.INDIGO,
            'appeal': ft.colors.DEEP_ORANGE,
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
