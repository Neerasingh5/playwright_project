import os
import sys
import pytest
from playwright.sync_api import expect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from utility.config_reader import ConfigReader


class RandomProductTest:
    """
    D. RANDOM PRODUCT TEST CASES - 4 independent tests using dynamic product selection.
    """

    def _login_and_go_to_products(self, browser):
        """Helper: login and navigate to products page, return InventoryPage."""
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
    # TEST 19: Select one random product
    # ------------------------------------------------------------------ #
    def test_select_one_random_product(self, browser):
        """Dynamically select a random product and verify its details page opens."""
        ip = self._login_and_go_to_products(browser)

        # Get all available products first
        browser.locator(ip.productDetailsLinks).first.wait_for(state="visible", timeout=15000)
        total = browser.locator(ip.productDetailsLinks).count()
        assert total > 0, "No products available to select."

        # Click random product
        prod = ip.click_random_product()

        # Assert product details page is displayed
        assert ip.is_product_details_displayed(), "Product details page not displayed."

        # Assert product name is captured and non-empty
        assert len(prod["name"]) > 0, "Selected product name should not be empty."

        # Assert URL shows product details
        assert "/product_details/" in browser.url, \
            f"Expected product details URL, got: {browser.url}"

        # Assert product title element is visible
        expect(browser.locator(ip.productTitle).first).to_be_visible()

        safe_name = prod["name"].encode("ascii", "ignore").decode("ascii")
        print(f"PASS: Selected Random Product [{prod['index']+1}/{total}]: {safe_name}")

    # ------------------------------------------------------------------ #
    # TEST 20: Verify randomly selected product details
    # ------------------------------------------------------------------ #
    def test_verify_random_product_details(self, browser):
        """Select random product and verify all detail elements are present."""
        ip = self._login_and_go_to_products(browser)

        prod = ip.click_random_product()

        # Assert product name is non-empty
        assert len(prod["name"]) > 0, "Product name empty."

        # Assert product price is captured
        assert len(prod["price"]) > 0, "Product price empty."

        # Assert product name element is visible
        expect(browser.locator(ip.productTitle).first).to_be_visible()

        # Assert product price element is visible
        expect(browser.locator(ip.productPrice).first).to_be_visible()

        # Assert Add to Cart button is visible
        expect(browser.locator(ip.addToCart_btn).first).to_be_visible()

        # Assert quantity input is visible
        expect(browser.locator(ip.quantityInput).first).to_be_visible()

        safe_name = prod["name"].encode("ascii", "ignore").decode("ascii")
        print(f"PASS: Random product details verified: '{safe_name}' @ {prod['price']}")

    # ------------------------------------------------------------------ #
    # TEST 21: Add randomly selected product to cart
    # ------------------------------------------------------------------ #
    def test_add_random_product_to_cart(self, browser):
        """Select random product, add to cart, verify it appears in cart."""
        ip = self._login_and_go_to_products(browser)
        cart_page = CartPage(browser)

        prod = ip.click_random_product()
        safe_name = prod["name"].encode("ascii", "ignore").decode("ascii")
        print(f"Selected Random Product: {safe_name}")

        # Assert product details page is shown
        assert ip.is_product_details_displayed(), f"Product details page not shown for '{safe_name}'."

        # Add to cart
        added = ip.add_to_cart()
        assert added, f"Cart modal not shown after adding '{safe_name}'."

        # Navigate to cart
        ip.click_cart()

        # Assert cart page displayed
        assert cart_page.is_cart_displayed(), "Cart page not displayed."

        # Assert selected product is in cart
        assert cart_page.is_product_in_cart(prod["name"]), \
            f"'{safe_name}' not found in cart. Cart contents: {cart_page.get_cart_product_names()}"

        cart_names = cart_page.get_cart_product_names()
        print(f"PASS: '{safe_name}' found in cart. Cart: {cart_names}")

    # ------------------------------------------------------------------ #
    # TEST 22: Select multiple random products and add them to cart
    # ------------------------------------------------------------------ #
    def test_add_multiple_random_products_to_cart(self, browser):
        """Select 2 different random products and verify both appear in cart."""
        ip = self._login_and_go_to_products(browser)
        cart_page = CartPage(browser)

        # Select first random product
        prod1 = ip.click_random_product()
        safe1 = prod1["name"].encode("ascii", "ignore").decode("ascii")
        print(f"Selected Random Product 1: {safe1}")

        assert ip.is_product_details_displayed(), f"Details not shown for Product 1: {safe1}"
        added1 = ip.add_to_cart()
        assert added1, f"Failed to add Product 1 '{safe1}' to cart."

        # Go back to products
        ip.back_to_products()
        assert ip.is_products_page_displayed(), "Failed to return to products page."

        # Select second random product (different from first)
        prod2 = ip.click_random_product(exclude_index=prod1["index"])
        safe2 = prod2["name"].encode("ascii", "ignore").decode("ascii")
        print(f"Selected Random Product 2: {safe2}")

        assert prod2["index"] != prod1["index"], "Product 2 should be different from Product 1."
        assert ip.is_product_details_displayed(), f"Details not shown for Product 2: {safe2}"

        added2 = ip.add_to_cart()
        assert added2, f"Failed to add Product 2 '{safe2}' to cart."

        # Navigate to cart
        ip.click_cart()
        assert cart_page.is_cart_displayed(), "Cart page not displayed."

        # Assert both products are in cart
        cart_names = cart_page.get_cart_product_names()
        assert cart_page.is_product_in_cart(prod1["name"]), \
            f"Product 1 '{safe1}' not in cart. Cart: {cart_names}"
        assert cart_page.is_product_in_cart(prod2["name"]), \
            f"Product 2 '{safe2}' not in cart. Cart: {cart_names}"

        count = cart_page.get_cart_items_count()
        assert count >= 2, f"Expected at least 2 items in cart, found {count}."

        print(f"PASS: Both products in cart: '{safe1}' & '{safe2}'")
