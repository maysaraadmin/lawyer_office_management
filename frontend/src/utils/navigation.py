from flet import Page

async def navigate_to(page: Page, route: str):
    """Helper function to navigate to a route"""
    page.views.clear()
    page.go(route)
