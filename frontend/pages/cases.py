import flet as ft
from ..services.api_client import api_client
from .base_page import BasePage
from ..components.case_card import CaseCard

class CasesPage(BasePage):
    def __init__(self, page: ft.Page):
        super().__init__(page)
        self.page.title = "Cases - Lawyer Office Management"
        self.cases = []
        self.case_list = ft.ListView(expand=True, spacing=10, padding=20)
        self.search_field = ft.TextField(
            label="Search cases...",
            prefix_icon=ft.icons.SEARCH,
            on_submit=self.search_cases,
            expand=True
        )
        
    async def initialize(self):
        """Initialize the cases page"""
        if not await self.check_auth():
            return
            
        self.setup_app_bar()
        self.setup_drawer()
        self.show_loading("Loading cases...")
        
        try:
            await self.load_cases()
            await self.build_ui()
        except Exception as e:
            await self.handle_error(e, "Failed to load cases")
    
    async def load_cases(self, search_query: str = None):
        """Load cases from the API"""
        try:
            params = {}
            if search_query:
                params["search"] = search_query
                
            response = await api_client.get("cases/", params=params)
            self.cases = response.get("results", [])
            
        except Exception as e:
            await self.handle_error(e, "Failed to load cases")
            self.cases = []
    
    async def search_cases(self, e):
        """Search for cases"""
        query = self.search_field.value.strip()
        await self.load_cases(query)
        await self.build_ui()
    
    async def build_ui(self):
        """Build the UI components"""
        # Clear existing content
        self.page.clean()
        
        # Rebuild app bar and drawer
        self.setup_app_bar()
        self.setup_drawer()
        
        # Create header
        header = ft.Row(
            [
                ft.Text("Cases", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.IconButton(
                    icon=ft.icons.ADD,
                    tooltip="Add New Case",
                    on_click=self.add_new_case,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # Build case list
        self.case_list.controls = []
        if not self.cases:
            self.case_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.icons.CASE, size=48),
                            ft.Text("No cases found"),
                            ft.ElevatedButton(
                                "Add New Case",
                                on_click=self.add_new_case,
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
            for case in self.cases:
                self.case_list.controls.append(
                    CaseCard(case, on_click=self.view_case_details)
                )
        
        # Build the main content
        content = ft.Column(
            [
                header,
                ft.Row(
                    [
                        self.search_field,
                        ft.IconButton(
                            icon=ft.icons.FILTER_LIST,
                            tooltip="Filter cases",
                            on_click=self.show_filters,
                        ),
                    ],
                    spacing=10,
                ),
                ft.Divider(),
                self.case_list,
            ],
            expand=True,
            spacing=20,
        )
        
        # Add content to page
        self.page.add(content)
        self.page.update()
    
    async def view_case_details(self, case_id: str):
        """View details of a specific case"""
        # Navigate to case details page
        self.page.go(f"/cases/{case_id}")
    
    async def add_new_case(self, _=None):
        """Navigate to add new case page"""
        self.page.go("/cases/new")
    
    async def show_filters(self, _):
        """Show filter dialog"""
        # TODO: Implement filter dialog
        self.show_snackbar("Filter functionality coming soon!")

async def cases_page(page: ft.Page):
    """Create and initialize the cases page"""
    cases = CasesPage(page)
    await cases.initialize()
    return cases
