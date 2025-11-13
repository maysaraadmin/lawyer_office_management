import flet as ft
from flet import Page, View, AppBar, Text, colors

def main(page: Page):
    """
    Main entry point for the Lawyer Office Mobile App
    """
    # Configure the page
    page.title = "Lawyer Office"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # Set up the app's theme
    page.theme = ft.Theme(
        color_scheme_seed=colors.BLUE,
        visual_density=ft.ThemeVisualDensity.COMFORTABLE,
    )
    
    # Navigation state
    current_view = ft.Ref[View]()
    
    def route_change(route):
        """Handle route changes"""
        page.views.clear()
        
        # Home/Dashboard view
        if page.route == "/" or page.route == "/dashboard":
            view = View(
                "/",
                [
                    AppBar(title=Text("Dashboard"), bgcolor=colors.SURFACE_VARIANT),
                    ft.ElevatedButton(
                        "Go to Cases",
                        on_click=lambda _: page.go("/cases"),
                    ),
                    ft.ElevatedButton(
                        "Go to Appointments",
                        on_click=lambda _: page.go("/appointments"),
                    ),
                ],
            )
            
        # Cases view
        elif page.route == "/cases":
            view = View(
                "/cases",
                [
                    AppBar(
                        title=Text("My Cases"),
                        bgcolor=colors.SURFACE_VARIANT,
                        leading=ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            on_click=lambda _: page.go("/"),
                        ),
                    ),
                    ft.Text("Your cases will appear here"),
                ],
            )
            
        # Appointments view
        elif page.route == "/appointments":
            view = View(
                "/appointments",
                [
                    AppBar(
                        title=Text("Appointments"),
                        bgcolor=colors.SURFACE_VARIANT,
                        leading=ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            on_click=lambda _: page.go("/"),
                        ),
                    ),
                    ft.Text("Your appointments will appear here"),
                ],
            )
            
        # 404 - Page not found
        else:
            view = View(
                "/404",
                [
                    AppBar(title=Text("404"), bgcolor=colors.SURFACE_VARIANT),
                    ft.Text("Page not found"),
                    ft.ElevatedButton(
                        "Go to Dashboard",
                        on_click=lambda _: page.go("/"),
                    ),
                ],
            )
        
        page.views.append(view)
        current_view.value = view
        page.update()
    
    # Set up navigation
    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    
    # Configure page events
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Initialize the app
    page.go(page.route or "/")

# Run the app
if __name__ == "__main__":
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,  # Use ft.AppView.FLET_APP for mobile
        port=8502,  # Different port from the web app
    )
