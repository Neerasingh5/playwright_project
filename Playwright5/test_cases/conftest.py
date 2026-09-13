import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utility.helper import Helper
from utility.config_reader import ConfigReader
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage


@pytest.fixture(scope="function")
def browser():
    """Fixture: launches browser, navigates to home page, yields page, closes after test."""
    driver = Helper.start_browser(ConfigReader.get_property("browser"))
    yield driver
    Helper.close_browser(driver)


@pytest.fixture(scope="function")
def login_page(browser):
    """Fixture: navigates to login page and returns LoginPage object."""
    browser.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
    return LoginPage(browser)


@pytest.fixture(scope="function")
def logged_in_browser(browser):
    """Fixture: performs a valid login and yields the page (already authenticated)."""
    browser.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
    lp = LoginPage(browser)
    lp.login(
        ConfigReader.get_property("username"),
        ConfigReader.get_property("password")
    )
    lp.is_login_successful()
    yield browser


@pytest.fixture(scope="function")
def products_page(logged_in_browser):
    """Fixture: logs in then navigates to /products, yields page."""
    ip = InventoryPage(logged_in_browser)
    ip.click_products()
    yield logged_in_browser


@pytest.fixture(scope="function")
def page_objects(browser):
    """Fixture: returns a dict of all page objects bound to the same browser instance."""
    return {
        "page": browser,
        "login_page": LoginPage(browser),
        "inventory_page": InventoryPage(browser),
        "cart_page": CartPage(browser),
        "checkout_page": CheckoutPage(browser),
    }
