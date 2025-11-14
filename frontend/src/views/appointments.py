from datetime import datetime, timedelta
import asyncio
import logging
import flet as ft

logger = logging.getLogger(__name__)

class AppointmentsView:
    def __init__(self, app):
        self.app = app
        self.page = app.page
    
    def build(self):
        # Header with title and add button
        header = ft.Row(
            [
                ft.Text(
                    "Appointments",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.ElevatedButton(
                    "New Appointment",
                    icon="add",
                    on_click=self._show_add_appointment_dialog,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        padding=ft.padding.only(bottom=20),

        # Search and filter row
        search_filter_row = ft.Row(
            [
                ft.TextField(
                    label="Search appointments...",
                    expand=True,
                    prefix_icon=ft.Icon("search"),
                    on_change=self._search_appointments,
                ),
                ft.Dropdown(
                    label="Filter by Status",
                    options=[
                        ft.dropdown.Option("All"),
                        ft.dropdown.Option("Scheduled"),
                        ft.dropdown.Option("Completed"),
                        ft.dropdown.Option("Cancelled"),
                        ft.dropdown.Option("Rescheduled"),
                    ],
                    value="All",
                    width=200,
                    on_change=self._apply_filters,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Appointments list (mock data for now)
        appointments_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=ft.padding.all(10),
        )

        # Add mock appointments
        now = datetime.now()
        mock_appointments = [
            {
                "id": 1,
                "title": "Client Consultation",
                "description": "Initial consultation with new client",
                "time": now + timedelta(hours=2),
                "date": now,
                "type": "Consultation",
                "location": "Office",
                "status": "Scheduled",
            },
            {
                "id": 2,
                "title": "Case Review",
                "description": "Review case documents and prepare strategy",
                "time": now - timedelta(hours=2),
                "date": now,
                "type": "Internal",
                "location": "Office",
                "status": "Completed",
            },
            {
                "id": 3,
                "title": "Court Appearance",
                "description": "Attend hearing at downtown courthouse",
                "time": now + timedelta(days=1),
                "date": now + timedelta(days=1),
                "type": "Court",
                "location": "Downtown Courthouse",
                "status": "Scheduled",
            },
            {
                "id": 4,
                "title": "Client Meeting",
                "description": "Follow-up meeting with existing client",
                "time": now - timedelta(hours=2),
                "date": now,
                "type": "Consultation",
                "location": "Phone",
                "status": "Completed",
            },
        ]

        for appointment in mock_appointments:
            status_color = {
                "Scheduled": ft.Colors.BLUE,
                "Completed": ft.Colors.GREEN,
                "Cancelled": ft.Colors.RED,
                "Rescheduled": ft.Colors.ORANGE,
            }.get(appointment["status"], ft.Colors.GREY)

            appointment_card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        appointment["title"],
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        expand=True,
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            appointment["status"],
                                            size=12,
                                            color=ft.Colors.WHITE,
                                        ),
                                        bgcolor=status_color,
                                        padding=ft.padding.symmetric(5, 10),
                                        border_radius=5,
                                    ),
                                ]
                            ),
                            ft.Text(appointment["description"]),
                            ft.Row(
                                [
                                    ft.Icon("schedule", size=16),
                                    ft.Text(
                                        appointment["time"].strftime("%I:%M %p")
                                        if isinstance(appointment["time"], datetime)
                                        else appointment["time"]
                                    ),
                                    ft.Icon("calendar_today", size=16),
                                    ft.Text(
                                        appointment["date"].strftime("%b %d, %Y")
                                        if isinstance(appointment["date"], datetime)
                                        else appointment["date"]
                                    ),
                                    ft.Icon("location_on", size=16),
                                    ft.Text(appointment["location"]),
                                ],
                            ),
                        ],
                        spacing=5,
                    ),
                    padding=ft.padding.all(15),
                ),
                elevation=2,
            )
            appointments_list.controls.append(appointment_card)

        # Main container
        container = ft.Container(
            content=ft.Column(
                [
                    header,
                    search_filter_row,
                    ft.Divider(),
                    appointments_list,
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            padding=ft.padding.all(20),
        )

        return container

    def _show_add_appointment_dialog(self, e):
        """Show dialog to add a new appointment"""
        logger.info("Add appointment dialog requested")
        try:
            # Create form fields
            title_field = ft.TextField(
                label="Title",
                autofocus=True,
                width=300
            )
            
            description_field = ft.TextField(
                label="Description",
                multiline=True,
                width=300,
                height=100
            )
            
            start_time_field = ft.TextField(
                label="Start Time (YYYY-MM-DD HH:MM)",
                value=datetime.now().strftime("%Y-%m-%d %H:%M"),
                width=300
            )
            
            end_time_field = ft.TextField(
                label="End Time (YYYY-MM-DD HH:MM)",
                value=(datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),
                width=300
            )
            
            status_field = ft.Dropdown(
                label="Status",
                options=[
                    ft.dropdown.Option("scheduled"),
                    ft.dropdown.Option("completed"),
                    ft.dropdown.Option("cancelled"),
                    ft.dropdown.Option("rescheduled")
                ],
                value="scheduled",
                width=300
            )
            
            def close_dialog(e):
                self.page.dialog.open = False
                self.page.update()
            
            def save_appointment(e):
                """Save the new appointment"""
                import asyncio
                
                async def _save():
                    try:
                        # Validate required fields
                        if not title_field.value or not start_time_field.value or not end_time_field.value:
                            self.page.snack_bar = ft.SnackBar(
                                content=ft.Text("Please fill in all required fields"),
                                bgcolor=ft.Colors.RED
                            )
                            self.page.snack_bar.open = True
                            await self.page.update_async()
                            return
                        
                        # Validate datetime format
                        try:
                            start_dt = datetime.strptime(start_time_field.value, "%Y-%m-%d %H:%M")
                            end_dt = datetime.strptime(end_time_field.value, "%Y-%m-%d %H:%M")
                            
                            if start_dt >= end_dt:
                                self.page.snack_bar = ft.SnackBar(
                                    content=ft.Text("End time must be after start time"),
                                    bgcolor=ft.Colors.RED
                                )
                                self.page.snack_bar.open = True
                                await self.page.update_async()
                                return
                        except ValueError:
                            self.page.snack_bar = ft.SnackBar(
                                content=ft.Text("Invalid datetime format. Use YYYY-MM-DD HH:MM"),
                                bgcolor=ft.Colors.RED
                            )
                            self.page.snack_bar.open = True
                            await self.page.update_async()
                            return
                        
                        # Prepare appointment data
                        appointment_data = {
                            "title": title_field.value,
                            "description": description_field.value or "",
                            "start_time": start_dt.isoformat(),
                            "end_time": end_dt.isoformat(),
                            "status": status_field.value
                        }
                        
                        # Create appointment via API
                        from src.services.api_client import api_client
                        logger.info(f"Creating appointment with data: {appointment_data}")
                        logger.info(f"API client access token: {api_client.access_token is not None}")
                        result = await api_client.create_appointment(appointment_data)
                        logger.info(f"Appointment created successfully: {result}")
                        
                        # Show success message
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text("Appointment created successfully!"),
                            bgcolor=ft.Colors.GREEN
                        )
                        self.page.snack_bar.open = True
                        
                        # Close dialog and refresh data
                        close_dialog(e)
                        await self.load_data()
                        await self.page.update_async()
                        
                    except Exception as ex:
                        logger.error(f"Error creating appointment: {str(ex)}")
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Error creating appointment: {str(ex)}"),
                            bgcolor=ft.Colors.RED
                        )
                        self.page.snack_bar.open = True
                        await self.page.update_async()
                
                # Run the async function
                asyncio.create_task(_save())
            
            # Create dialog
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Add New Appointment"),
                content=ft.Column(
                    [
                        title_field,
                        description_field,
                        start_time_field,
                        end_time_field,
                        status_field
                    ],
                    tight=True,
                    height=400,
                    scroll=ft.ScrollMode.AUTO
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=close_dialog),
                    ft.TextButton("Save", on_click=save_appointment),
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
            
            self.page.dialog = dialog
            dialog.open = True
            logger.info(f"Dialog created and opened. Dialog object: {dialog}")
            logger.info(f"Dialog.open state: {dialog.open}")
            logger.info(f"Page.dialog set: {self.page.dialog}")
            self.page.update()
            logger.info("Page updated with dialog")
            
        except Exception as ex:
            logger.error(f"Error opening appointment dialog: {str(ex)}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error opening dialog: {str(ex)}"),
                bgcolor=ft.Colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _apply_filters(self, e):
        # TODO: Implement filter logic
        print("Applying filters...")
    
    def _search_appointments(self, e):
        # TODO: Implement search logic
        print(f"Searching for: {e.control.value}")

    async def load_data(self):
        """Load appointments data from API"""
        try:
            from src.services.api_client import api_client
            appointments = await api_client.get_appointments()
            logger.info(f"Loaded {len(appointments)} appointments")
        except Exception as e:
            logger.error(f"Error loading appointments: {str(e)}")
            # Keep mock data if API fails
