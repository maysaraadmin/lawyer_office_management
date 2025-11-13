import flet as ft
from flet import Page, ThemeMode, MainAxisAlignment, CrossAxisAlignment
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main(page: Page):
    """Main entry point for the application"""
    try:
        # Configure page
        page.title = "Lawyer Office Management"
        page.theme_mode = ThemeMode.LIGHT
        page.window_width = 1200
        page.window_height = 800
        page.window_resizable = True
        
        # Add a simple UI to verify it's working
        page.add(
            ft.AppBar(
                title=ft.Text("Lawyer Office Management"),
                bgcolor=ft.colors.BLUE_700,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Welcome to Lawyer Office Management", 
                              size=24, 
                              weight="bold"),
                        ft.Text("The application is running successfully!", 
                              size=16),
                        ft.ElevatedButton(
                            "Click me!", 
                            on_click=lambda e: print("Button clicked!")
                        )
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                    expand=True
                ),
                margin=20,
                padding=20,
                border_radius=10,
                bgcolor=ft.colors.GREY_100,
                width=float("inf"),
                height=float("inf")
            )
        )
        
        logger.info("Application started successfully")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        page.add(ft.Text(f"An error occurred: {str(e)}", color="red"))

if __name__ == "__main__":
    # Run the app on 127.0.0.1:8501
    ft.app(
        target=main,
        view=ft.WEB_BROWSER,
        port=8501,
        host="127.0.0.1"
    )
