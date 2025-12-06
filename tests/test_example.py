import pytest
from playwright.sync_api import Page, expect


@pytest.mark.ui
def test_example_homepage(page: Page):
    """Example test that navigates to Playwright website"""
    page.goto("https://playwright.dev/")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(pytest.regexp(r"Playwright"))


@pytest.mark.ui
def test_get_started_link(page: Page):
    """Example test that clicks on 'Get Started' link"""
    page.goto("https://playwright.dev/")

    # Click the get started link.
    page.get_by_role("link", name="Get started").click()

    # Expects page to have a heading with the name of Installation.
    expect(page.get_by_role("heading", name="Installation")).to_be_visible()


@pytest.mark.ui
def test_search_functionality(page: Page):
    """Example test for search functionality"""
    page.goto("https://playwright.dev/")

    # Click on search button
    search_button = page.get_by_label("Search")
    if search_button.is_visible():
        search_button.click()

        # Type in search box
        search_input = page.get_by_placeholder("Search docs")
        expect(search_input).to_be_visible()
