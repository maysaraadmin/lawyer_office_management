import flet as ft
from .views.dashboard import DashboardView
from .views.appointments import AppointmentsView
from .views.clients import ClientsView

class LawyerOfficeApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Lawyer Office Management"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.window_width = 1280
        self.page.window_height = 800
        self.page.window_resizable = True
        
        # Initialize views
        self.dashboard_view = DashboardView(self)
        self.appointments_view = AppointmentsView(self)
        self.clients_view = ClientsView(self)
        
        # Set up navigation
        self.nav_items = [
            ft.NavigationRailDestination(
                icon="dashboard_outlined",
                selected_icon="dashboard",
                label="Dashboard"
            ),
            ft.NavigationRailDestination(
                icon="calendar_today_outlined",
                selected_icon="calendar_today",
                label="Appointments"
            ),
            ft.NavigationRailDestination(
                icon="people_outline",
                selected_icon="people",
                label="Clients"
            ),
        ]
        
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            on_change=self.navigate,
            destinations=self.nav_items
        )
        
        # Main content area
        self.content = ft.Container(
            content=self.dashboard_view.build(),
            expand=True,
            padding=20
        )
        
        # Main layout
        self.main = ft.Row(
            [
                self.nav_rail,
                ft.VerticalDivider(width=1),
                self.content,
            ],
            expand=True,
        )
        
        # Set the initial view
        self.page.add(self.main)
        self.page.update()
    
    def navigate(self, e):
        index = e.control.selected_index
        self.nav_rail.selected_index = index
        
        if index == 0:
            self.content.content = self.dashboard_view.build()
        elif index == 1:
            self.content.content = self.appointments_view.build()
        elif index == 2:
            self.content.content = self.clients_view.build()
            
        self.page.update()

def main(page: ft.Page):
    app = LawyerOfficeApp(page)

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)
