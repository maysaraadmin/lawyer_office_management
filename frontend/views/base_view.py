import flet as ft
from typing import Optional, Dict, Any, List, Callable, TypeVar, Generic, Type
from abc import ABC, abstractmethod

# Import services and config
from services.api_client import api_client, auth_service
from config import Config

T = TypeVar('T')

class BaseView(ABC):
    """Base view class for all views"""
    
    def __init__(self, app):
        self.app = app
        self.page = app.page
        self._view = None
    
    @property
    def view(self) -> ft.Control:
        """Get the view control"""
        if self._view is None:
            self._view = self.build()
        return self._view
    
    @abstractmethod
    def build(self) -> ft.Control:
        """Build the view"""
        pass
    
    async def initialize(self):
        """Initialize the view (called when the view is loaded)"""
        pass
    
    async def refresh(self):
        """Refresh the view data"""
        pass
    
    # Helper methods
    async def show_loading(self, message: str = "Loading..."):
        """Show a loading dialog"""
        await self.app.show_loading(message)
    
    async def hide_loading(self):
        """Hide the loading dialog"""
        await self.app.hide_loading()
    
    async def show_snackbar(self, message: str, color: str = None):
        """Show a snackbar message"""
        await self.app.show_snackbar(message, color)
    
    async def show_error(self, message: str):
        """Show an error message"""
        await self.show_snackbar(message, Config.COLORS['error'])
    
    async def show_success(self, message: str):
        """Show a success message"""
        await self.show_snackbar(message, Config.COLORS['success'])
    
    async def show_alert(self, title: str, message: str, on_confirm=None):
        """Show an alert dialog"""
        await self.app.show_alert(title, message, on_confirm)
    
    async def show_confirm_dialog(
        self, 
        title: str, 
        message: str, 
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        on_confirm: Callable = None,
        on_cancel: Callable = None,
    ):
        """Show a confirmation dialog"""
        await self.app.show_confirm_dialog(
            title=title,
            message=message,
            confirm_text=confirm_text,
            cancel_text=cancel_text,
            on_confirm=on_confirm,
            on_cancel=on_cancel,
        )
    
    async def go_to(self, route: str):
        """Navigate to a route"""
        await self.app.go_to(route)
    
    # UI Components
    def create_card(self, title: str, content: ft.Control, actions: List[ft.Control] = None) -> ft.Card:
        """Create a card with title and content"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            title=ft.Text(title, weight=ft.FontWeight.BOLD, size=16),
                        ),
                        ft.Divider(),
                        ft.Container(
                            content=content,
                            padding=ft.padding.symmetric(horizontal=16, vertical=8),
                        ),
                    ] + ([
                        ft.Row(
                            actions,
                            alignment=ft.MainAxisAlignment.END,
                        )
                    ] if actions else []),
                ),
                padding=ft.padding.symmetric(vertical=8),
            ),
            elevation=2,
            margin=ft.margin.all(8),
        )
    
    def create_data_table(
        self,
        columns: List[Dict[str, Any]],
        data: List[Dict[str, Any]],
        on_select: Callable = None,
        sort_column: str = None,
        sort_ascending: bool = True,
        on_sort: Callable = None,
    ) -> ft.DataTable:
        """Create a data table"""
        # Sort data if sort_column is provided
        if sort_column and data:
            data = sorted(
                data,
                key=lambda x: x.get(sort_column, ''),
                reverse=not sort_ascending
            )
        
        # Create data rows
        rows = []
        for item in data:
            cells = []
            for col in columns:
                col_name = col['name']
                value = item.get(col_name, '')
                
                # Format the value based on column type
                if 'format' in col:
                    if callable(col['format']):
                        value = col['format'](value)
                    elif col['format'] == 'date':
                        value = value.strftime('%Y-%m-%d') if value else ''
                    elif col['format'] == 'datetime':
                        value = value.strftime('%Y-%m-%d %H:%M') if value else ''
                    elif col['format'] == 'currency':
                        value = f"${value:,.2f}" if value is not None else '$0.00'
                    elif col['format'] == 'boolean':
                        value = 'Yes' if value else 'No'
                
                cells.append(ft.DataCell(ft.Text(str(value) if value is not None else '')))
            
            rows.append(
                ft.DataRow(
                    cells=cells,
                    on_select_changed=lambda e, item=item: on_select(item) if on_select else None,
                )
            )
        
        # Create header row with sort indicators
        header_cells = []
        for col in columns:
            col_name = col['name']
            label = col.get('label', col_name.replace('_', ' ').title())
            
            # Add sort indicator if column is sortable
            if col.get('sortable', False):
                is_sorted = sort_column == col_name
                sort_icon = ft.Icon(
                    ft.icons.ARROW_UPWARD if is_sorted and sort_ascending else ft.icons.ARROW_DOWNWARD,
                    size=16,
                    color=ft.colors.PRIMARY if is_sorted else ft.colors.GREY,
                )
                
                header_cells.append(
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.Text(label, weight=ft.FontWeight.BOLD),
                                sort_icon if is_sorted else ft.Container(width=16),
                            ],
                            spacing=4,
                        ),
                        on_tap=lambda e, col=col_name: on_sort(col) if on_sort else None,
                    )
                )
            else:
                header_cells.append(
                    ft.DataCell(
                        ft.Text(label, weight=ft.FontWeight.BOLD),
                    )
                )
        
        return ft.DataTable(
            columns=[ft.DataColumn(cell) for cell in header_cells],
            rows=rows,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=8,
            heading_row_color=ft.colors.GREY_100,
            heading_row_height=48,
            data_row_min_height=48,
            data_row_max_height=72,
            horizontal_margin=16,
            column_spacing=16,
            divider_thickness=1,
            show_checkbox_column=False,
            sort_column_index=next((i for i, col in enumerate(columns) if col.get('name') == sort_column), None),
            sort_ascending=sort_ascending,
        )
    
    def create_form_field(
        self,
        field_type: str,
        label: str,
        value: Any = None,
        required: bool = False,
        options: List[Dict[str, Any]] = None,
        on_change: Callable = None,
        disabled: bool = False,
        multiline: bool = False,
        min_lines: int = 1,
        max_lines: int = 1,
        keyboard_type: str = None,
        prefix_icon: str = None,
        suffix_icon: str = None,
        hint_text: str = None,
        error_text: str = None,
        autofocus: bool = False,
        expand: bool = False,
        **kwargs
    ) -> ft.Control:
        """Create a form field"""
        field = None
        
        # Common properties
        common_props = {
            'label': label,
            'border_radius': 8,
            'border_color': ft.colors.GREY_400,
            'focused_border_color': Config.COLORS['primary'],
            'focused_border_width': 2,
            'content_padding': ft.padding.symmetric(horizontal=12, vertical=16),
            'text_size': 14,
            'disabled': disabled,
            'expand': expand,
            'autofocus': autofocus,
        }
        
        # Create the appropriate field type
        if field_type == 'text':
            field = ft.TextField(
                value=str(value) if value is not None else '',
                multiline=multiline,
                min_lines=min_lines if multiline else None,
                max_lines=max_lines if multiline else 1,
                keyboard_type=keyboard_type,
                prefix_icon=prefix_icon,
                suffix_icon=suffix_icon,
                hint_text=hint_text,
                error_text=error_text,
                on_change=on_change,
                **common_props,
                **kwargs,
            )
        elif field_type == 'password':
            field = ft.TextField(
                value=value or '',
                password=True,
                can_reveal_password=True,
                prefix_icon=ft.icons.LOCK,
                hint_text=hint_text or 'Enter your password',
                error_text=error_text,
                on_change=on_change,
                **common_props,
                **kwargs,
            )
        elif field_type == 'email':
            field = ft.TextField(
                value=value or '',
                keyboard_type=ft.KeyboardType.EMAIL,
                prefix_icon=ft.icons.EMAIL,
                hint_text=hint_text or 'example@email.com',
                error_text=error_text,
                on_change=on_change,
                **common_props,
                **kwargs,
            )
        elif field_type == 'select':
            dropdown_options = [
                ft.dropdown.Option(
                    text=str(opt.get('label', opt.get('value', ''))),
                    key=str(opt.get('value', '')),
                )
                for opt in (options or [])
            ]
            
            field = ft.Dropdown(
                value=str(value) if value is not None else None,
                options=dropdown_options,
                hint_text=hint_text,
                error_text=error_text,
                on_change=on_change,
                **common_props,
                **kwargs,
            )
        elif field_type == 'date':
            field = ft.TextField(
                value=value.strftime('%Y-%m-%d') if value else '',
                keyboard_type=ft.KeyboardType.DATETIME,
                prefix_icon=ft.icons.CALENDAR_TODAY,
                hint_text=hint_text or 'YYYY-MM-DD',
                error_text=error_text,
                on_change=on_change,
                **common_props,
                **kwargs,
            )
        elif field_type == 'time':
            field = ft.TextField(
                value=value.strftime('%H:%M') if value else '',
                keyboard_type=ft.KeyboardType.DATETIME,
                prefix_icon=ft.icons.ACCESS_TIME,
                hint_text=hint_text or 'HH:MM',
                error_text=error_text,
                on_change=on_change,
                **common_props,
                **kwargs,
            )
        elif field_type == 'checkbox':
            field = ft.Checkbox(
                value=bool(value) if value is not None else False,
                label=label,
                on_change=on_change,
                disabled=disabled,
                **kwargs,
            )
        elif field_type == 'radio':
            radio_options = []
            for opt in (options or []):
                radio_options.append(
                    ft.Radio(
                        value=str(opt.get('value', '')),
                        label=str(opt.get('label', '')),
                    )
                )
            
            field = ft.RadioGroup(
                value=str(value) if value is not None else None,
                content=ft.Column(radio_options, spacing=8),
                on_change=on_change,
                disabled=disabled,
                **kwargs,
            )
        
        # Add required indicator
        if required and field and field_type != 'checkbox' and field_type != 'radio':
            field.label = ft.Row(
                [
                    ft.Text(label),
                    ft.Text("*", color=ft.colors.RED),
                ],
                spacing=2,
            )
        
        return field
    
    def create_button(
        self,
        text: str,
        on_click: Callable,
        variant: str = 'elevated',
        color: str = None,
        bgcolor: str = None,
        icon: str = None,
        disabled: bool = False,
        loading: bool = False,
        expand: bool = False,
    ) -> ft.Control:
        """Create a button"""
        if variant == 'elevated':
            return ft.ElevatedButton(
                text=text,
                on_click=on_click,
                color=color or ft.colors.WHITE,
                bgcolor=bgcolor or Config.COLORS['primary'],
                icon=icon,
                disabled=disabled or loading,
                expand=expand,
                style=ft.ButtonStyle(
                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                    shape=ft.RoundedRectangleBorder(radius=8),
                    elevation=2,
                ),
                content=ft.Row(
                    [
                        ft.ProgressRing(width=16, height=16, stroke_width=2, visible=loading),
                        ft.Text(text, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                ) if loading else None,
            )
        elif variant == 'outlined':
            return ft.OutlinedButton(
                text=text,
                on_click=on_click,
                color=color or Config.COLORS['primary'],
                icon=icon,
                disabled=disabled or loading,
                expand=expand,
                style=ft.ButtonStyle(
                    padding=ft.padding.symmetric(horizontal=24, vertical=12),
                    shape=ft.RoundedRectangleBorder(radius=8),
                    side=ft.BorderSide(1, color=Config.COLORS['primary'] if not disabled else ft.colors.GREY_400),
                ),
                content=ft.Row(
                    [
                        ft.ProgressRing(width=16, height=16, stroke_width=2, visible=loading),
                        ft.Text(text, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                ) if loading else None,
            )
        else:  # text button
            return ft.TextButton(
                text=text,
                on_click=on_click,
                style=ft.ButtonStyle(
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                ),
                disabled=disabled or loading,
                icon=icon,
            )
    
    def create_icon_button(
        self,
        icon: str,
        on_click: Callable,
        tooltip: str = None,
        color: str = None,
        bgcolor: str = None,
        size: int = 20,
        padding: int = 8,
        variant: str = 'standard',  # 'standard', 'filled', 'outlined'
        disabled: bool = False,
    ) -> ft.IconButton:
        """Create an icon button"""
        if variant == 'filled':
            return ft.IconButton(
                icon=icon,
                on_click=on_click,
                tooltip=tooltip,
                icon_color=color or ft.colors.WHITE,
                bgcolor=bgcolor or Config.COLORS['primary'],
                icon_size=size,
                disabled=disabled,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=padding,
                ),
            )
        elif variant == 'outlined':
            return ft.IconButton(
                icon=icon,
                on_click=on_click,
                tooltip=tooltip,
                icon_color=color or Config.COLORS['primary'],
                icon_size=size,
                disabled=disabled,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    side=ft.BorderSide(1, color=Config.COLORS['primary'] if not disabled else ft.colors.GREY_400),
                    padding=padding,
                ),
            )
        else:  # standard
            return ft.IconButton(
                icon=icon,
                on_click=on_click,
                tooltip=tooltip,
                icon_color=color or Config.COLORS['primary'],
                icon_size=size,
                disabled=disabled,
            )


class ListView(BaseView, Generic[T]):
    """Base list view with pagination and search"""
    
    def __init__(self, app):
        super().__init__(app)
        self.page = 1
        self.page_size = 10
        self.search_query = ''
        self.sort_by = None
        self.sort_ascending = True
        self.items = []
        self.total_items = 0
        self.is_loading = False
        self.search_controller = ft.TextEditingController()
        self.refresh_controller = ft.RefreshControl()
        
        # UI Controls
        self.search_field = None
        self.items_list = None
        self.pagination_controls = None
        self.empty_state = None
        self.error_state = None
        self.loading_indicator = None
    
    async def initialize(self):
        """Initialize the view"""
        await self.load_data()
    
    async def refresh(self):
        """Refresh the data"""
        self.page = 1
        await self.load_data()
    
    @abstractmethod
    async def load_data(self):
        """Load data from the API"""
        pass
    
    @abstractmethod
    def build_item_widget(self, item: T) -> ft.Control:
        """Build the widget for an item"""
        pass
    
    def build_search_field(self) -> ft.Control:
        """Build the search field"""
        if not hasattr(self, 'search_controller'):
            self.search_controller = ft.TextEditingController()
        
        async def on_search_changed(e):
            self.search_query = e.control.value
            await self.refresh()
        
        async def on_search_submit(e):
            await self.refresh()
        
        return ft.TextField(
            controller=self.search_controller,
            hint_text="Search...",
            prefix_icon=ft.icons.SEARCH,
            on_changed=on_search_changed,
            on_submit=on_search_submit,
            border_radius=20,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            text_size=14,
            expand=True,
        )
    
    def build_pagination_controls(self) -> ft.Control:
        """Build the pagination controls"""
        total_pages = (self.total_items + self.page_size - 1) // self.page_size
        
        async def go_to_prev_page(e):
            if self.page > 1:
                self.page -= 1
                await self.load_data()
        
        async def go_to_next_page(e):
            if self.page < total_pages:
                self.page += 1
                await self.load_data()
        
        return ft.Row(
            [
                ft.Text(f"Page {self.page} of {max(1, total_pages)}", size=14),
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.icons.CHEVRON_LEFT,
                            on_click=go_to_prev_page,
                            disabled=self.page <= 1 or self.is_loading,
                            tooltip="Previous page",
                        ),
                        ft.IconButton(
                            icon=ft.icons.CHEVRON_RIGHT,
                            on_click=go_to_next_page,
                            disabled=self.page >= total_pages or self.is_loading,
                            tooltip="Next page",
                        ),
                    ],
                    spacing=4,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
    
    def build_loading_indicator(self) -> ft.Control:
        """Build the loading indicator"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.ProgressRing(),
                    ft.Text("Loading...", size=14, color=ft.colors.GREY_600),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            padding=40,
            alignment=ft.alignment.center,
        )
    
    def build_empty_state(self) -> ft.Control:
        """Build the empty state"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.icons.SEARCH_OFF, size=48, color=ft.colors.GREY_400),
                    ft.Text("No items found", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "Try adjusting your search or filter to find what you're looking for.",
                        size=14,
                        color=ft.colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=40,
            alignment=ft.alignment.center,
        )
    
    def build_error_state(self, error: str) -> ft.Control:
        """Build the error state"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.icons.ERROR_OUTLINE, size=48, color=ft.colors.RED_400),
                    ft.Text("Something went wrong", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        error or "An unexpected error occurred. Please try again.",
                        size=14,
                        color=ft.colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.ElevatedButton(
                        "Retry",
                        on_click=lambda _: self.refresh(),
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(horizontal=24, vertical=12),
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            padding=40,
            alignment=ft.alignment.center,
        )
    
    def build(self) -> ft.Control:
        """Build the view"""
        # Search and filter bar
        search_bar = ft.Container(
            content=ft.Row(
                [
                    self.build_search_field(),
                    ft.IconButton(
                        icon=ft.icons.FILTER_LIST,
                        tooltip="Filters",
                        on_click=self.show_filters_dialog,
                    ),
                    ft.IconButton(
                        icon=ft.icons.REFRESH,
                        tooltip="Refresh",
                        on_click=self.refresh,
                    ),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
        )
        
        # Content area
        content = ft.Container(
            content=ft.Column(
                [
                    # Loading state
                    ft.Visibility(
                        visible=self.is_loading,
                        child=self.build_loading_indicator(),
                    ),
                    
                    # Error state
                    ft.Visibility(
                        visible=hasattr(self, 'error') and self.error is not None,
                        child=self.build_error_state(getattr(self, 'error', None)),
                    ),
                    
                    # Empty state
                    ft.Visibility(
                        visible=not self.is_loading and not getattr(self, 'error', None) and not self.items,
                        child=self.build_empty_state(),
                    ),
                    
                    # Items list
                    ft.Visibility(
                        visible=not self.is_loading and not getattr(self, 'error', None) and bool(self.items),
                        child=ft.ListView(
                            controls=[self.build_item_widget(item) for item in self.items],
                            expand=True,
                            spacing=8,
                            padding=ft.padding.symmetric(horizontal=16, vertical=8),
                        ),
                    ),
                    
                    # Pagination
                    ft.Visibility(
                        visible=not self.is_loading and not getattr(self, 'error', None) and bool(self.items),
                        child=ft.Container(
                            content=self.build_pagination_controls(),
                            padding=ft.padding.symmetric(horizontal=16, vertical=8),
                            border=ft.border.only(top=ft.border.BorderSide(1, ft.colors.GREY_200)),
                        ),
                    ),
                ],
                expand=True,
                spacing=0,
            ),
            expand=True,
        )
        
        return ft.Column(
            [
                search_bar,
                ft.Divider(height=1),
                content,
            ],
            expand=True,
            spacing=0,
        )
    
    async def show_filters_dialog(self, e):
        """Show the filters dialog"""
        # Override this method to implement custom filters
        pass
