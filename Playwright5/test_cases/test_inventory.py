import os
import sys
import pytest
from playwright.sync_api import expect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from utility.config_reader import ConfigReader


class InventoryTest:
    """
    C. INVENTORY / PRODUCT TEST CASES - 6 independent tests.
    """

    def _login_and_go_to_products(self, browser):
        """Helper: login and navigate to products page."""
        browser.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
        lp = LoginPage(browser)
        lp.login(
            ConfigReader.get_property("username"),
            ConfigReader.get_property("password")
        )
        assert lp.is_login_successful(), "Login failed in setup."
        ip = InventoryPage(browser)
        ip.click_products()
        return ip

    # ------------------------------------------------------------------ #
    # TEST 13: Inventory/products page opens after login
    # ------------------------------------------------------------------ #
    def test_inventory_page_opens_after_login(self, browser):
        """Verify products page is accessible after a successful login."""
        ip = self._login_and_go_to_products(browser)

        # Assert URL contains /products
        assert "/products" in browser.url, f"Expected '/products' in URL, got: {browser.url}"

        # Assert page is displayed
        assert ip.is_products_page_displayed(), "Products page not displayed after login."

        print(f"PASS: Products page URL: {browser.url}")

    # ------------------------------------------------------------------ #
    # TEST 14: Products are displayed
    # ------------------------------------------------------------------ #
    def test_products_are_displayed(self, browser):
        """Verify that product listings are visible on the products page."""
        ip = self._login_and_go_to_products(browser)

        # Assert at least one product detail link is visible
        expect(browser.locator(ip.productDetailsLinks).first).to_be_visible()

        # Assert multiple products exist
        count = browser.locator(ip.productDetailsLinks).count()
        assert count > 0, f"Expected at least 1 product link, found {count}."

        print(f"PASS: {count} products are displayed on the products page.")

    # ------------------------------------------------------------------ #
    # TEST 15: Product names are displayed
    # ------------------------------------------------------------------ #
    def test_product_names_are_displayed(self, browser):
        """Verify that clicking a product shows a non-empty product name."""
        ip = self._login_and_go_to_products(browser)

        # Click first product to verify name
        browser.locator(ip.productDetailsLinks).first.click()
        browser.locator(ip.productTitle).first.wait_for(state="visible", timeout=10000)

        product_name = browser.locator(ip.productTitle).first.inner_text().strip()
        assert len(product_name) > 0, "Product name should not be empty."

        # Assert product title element is visible
        expect(browser.locator(ip.productTitle).first).to_be_visible()

        print(f"PASS: Product name displayed: '{product_name}'")

    # ------------------------------------------------------------------ #
    # TEST 16: Product prices are displayed
    # ------------------------------------------------------------------ #
    def test_product_prices_are_displayed(self, browser):
        """Verify that clicking a product shows a non-empty product price."""
        ip = self._login_and_go_to_products(browser)

        # Click first product
        browser.locator(ip.productDetailsLinks).first.click()
        browser.locator(ip.productPrice).first.wait_for(state="visible", timeout=10000)

        # Assert price element is visible
        expect(browser.locator(ip.productPrice).first).to_be_visible()

        product_price = browser.locator(ip.productPrice).first.inner_text().strip()
        assert len(product_price) > 0, "Product price should not be empty."

        print(f"PASS: Product price displayed: '{product_price}'")

    # ------------------------------------------------------------------ #
    # TEST 17: Product details page is displayed correctly
    # ------------------------------------------------------------------ #
    def test_product_details_page_displayed(self, browser):
        """Verify that product details page loads with all key elements."""
        ip = self._login_and_go_to_products(browser)

        browser.locator(ip.productDetailsLinks).first.click()
        ip.is_product_details_displayed()

        # Assert URL contains /product_details/
        assert "/product_details/" in browser.url, \
            f"Expected '/product_details/' in URL, got: {browser.url}"

        # Assert product name visible
        expect(browser.locator(ip.productTitle).first).to_be_visible()

        # Assert product price visible
        expect(browser.locator(ip.productPrice).first).to_be_visible()

        # Assert Add to Cart button visible
        expect(browser.locator(ip.addToCart_btn).first).to_be_visible()

        # Assert quantity input visible
        expect(browser.locator(ip.quantityInput).first).to_be_visible()

        print(f"PASS: Product details page at {browser.url}")

    # ------------------------------------------------------------------ #
    # TEST 18: Product list contains expected available products
    # ------------------------------------------------------------------ #
    def test_product_list_contains_available_products(self, browser):
        """Verify the products list has an expected number of items."""
        ip = self._login_and_go_to_products(browser)

        # All product links
        links = browser.locator(ip.productDetailsLinks).all()
        count = len(links)

        # Automation Exercise has 34+ products — assert at least 10
        assert count >= 10, f"Expected at least 10 products, found {count}."

        # Every link should have a valid href
        for link in links[:5]:  # spot-check first 5
            href = link.get_attribute("href") or ""
            assert "/product_details/" in href, f"Unexpected product link: {href}"

        print(f"PASS: Products page contains {count} products.")
