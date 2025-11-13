import flet as ft
from typing import Dict, Any, Optional

class StatsCard(ft.Container):
    """A card component for displaying statistics with optional trend indicator"""
    
    def __init__(
        self,
        title: str,
        value: Any,
        icon: str = "INFO",  # Using string literal for icon
        color: str = "#2196F3",  # Blue color as hex
        trend: Optional[float] = None,
        formatter: str = None,
        **kwargs
    ):
        """Initialize the stats card
        
        Args:
            title: The title of the stat
            value: The value to display
            icon: The icon to show
            color: The primary color of the card
            trend: Optional trend value (positive or negative percentage)
            formatter: Optional formatter for the value ('currency', 'percent', etc.)
        """
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        self.trend = trend
        self.formatter = formatter
        
        # Format the value
        formatted_value = self._format_value(value)
        
        # Create the icon
        icon_widget = ft.Container(
            content=ft.Icon(
                self.icon,
                size=24,
                color=ft.colors.WHITE,
            ),
            padding=12,
            bgcolor=f"{self.color}44",  # Add transparency
            border_radius=12,
        )
        
        # Create the value text
        value_text = ft.Text(
            formatted_value,
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLACK87,
        )
        
        # Create the title text
        title_text = ft.Text(
            self.title.upper(),
            size=12,
            weight=ft.FontWeight.W_500,
            color=ft.colors.GREY_600,
            letter_spacing=0.5,
        )
        
        # Create trend indicator if provided
        trend_widget = ft.Container()  # Empty container by default
        if self.trend is not None:
            trend_icon = (
                ft.icons.TRENDING_UP
                if self.trend >= 0
                else ft.icons.TRENDING_DOWN
            )
            trend_color = (
                ft.colors.GREEN if self.trend >= 0 else ft.colors.RED
            )
            trend_text = f"{abs(self.trend)}%"
            
            trend_widget = ft.Row(
                [
                    ft.Icon(
                        trend_icon,
                        size=16,
                        color=trend_color,
                    ),
                    ft.Text(
                        trend_text,
                        size=12,
                        color=trend_color,
                        weight=ft.FontWeight.W_500,
                    ),
                ],
                spacing=4,
                tight=True,
            )
        
        # Create the main content
        content = ft.Column(
            [
                # Top row with icon and title
                ft.Row(
                    [
                        icon_widget,
                        ft.Container(expand=True),  # Spacer
                        trend_widget,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                # Spacer
                ft.Container(height=16),
                # Value and title
                value_text,
                title_text,
            ],
            spacing=0,
            expand=True,
        )
        
        # Initialize the container
        super().__init__(
            content=content,
            padding=20,
            border_radius=12,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(1, ft.colors.GREY_200),
            **kwargs
        )
        
        # Add hover effect
        self.on_hover = self._on_hover
        self.on_click = self._on_click
    
    def _format_value(self, value) -> str:
        """Format the value based on the formatter"""
        if self.formatter == 'currency':
            return f"${float(value):,.2f}"
        elif self.formatter == 'percent':
            return f"{float(value):.1f}%"
        elif isinstance(value, (int, float)) and value >= 1000:
            return f"{value:,.0f}"
        return str(value)
    
    def _on_hover(self, e):
        """Handle hover effect"""
        self.border = ft.border.all(
            1,
            ft.colors.BLUE_200 if e.data == "true" else ft.colors.GREY_200
        )
        self.update()
    
    def _on_click(self, e):
        """Handle click event"""
        if hasattr(self, 'on_click_callback'):
            self.on_click_callback(e)
