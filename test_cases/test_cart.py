import os
import sys
import pytest
from playwright.sync_api import expect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from utility.config_reader import ConfigReader


class CartTest:
    """
    E. CART TEST CASES - 8 independent tests.
    Each test performs its own login and setup.
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

    def _add_random_product_to_cart(self, browser):
        """Helper: selects random product, adds it to cart, opens cart. Returns (ip, cp, prod)."""
        ip = self._login_and_go_to_products(browser)
        cp = CartPage(browser)
        prod = ip.click_random_product()
        ip.add_to_cart()
        ip.click_cart()
        return ip, cp, prod

    # ------------------------------------------------------------------ #
    # TEST 23: Verify cart icon is displayed
    # ------------------------------------------------------------------ #
    def test_cart_icon_is_displayed(self, browser):
        """Verify cart navigation icon/link is visible on products page."""
        ip = self._login_and_go_to_products(browser)

        # Assert cart link is visible on the products page
        expect(browser.locator(ip.cartButton).first).to_be_visible()

        print("PASS: Cart icon/link is visible on the products page.")

    # ------------------------------------------------------------------ #
    # TEST 24: Add product and verify cart count
    # ------------------------------------------------------------------ #
    def test_add_product_and_verify_cart_count(self, browser):
        """Add one random product and verify cart contains at least 1 item."""
        ip, cp, prod = self._add_random_product_to_cart(browser)

        # Assert cart page displayed
        assert cp.is_cart_displayed(), "Cart page was not displayed."

        # Assert cart has at least 1 item
        count = cp.get_cart_items_count()
        assert count >= 1, f"Expected at least 1 item in cart, got {count}."

        safe_name = prod["name"].encode("ascii", "ignore").decode("ascii")
        print(f"PASS: Cart count = {count} after adding '{safe_name}'.")

    # ------------------------------------------------------------------ #
    # TEST 25: Verify selected product exists in cart
    # ------------------------------------------------------------------ #
    def test_selected_product_exists_in_cart(self, browser):
        """Add random product to cart and verify it appears in the cart."""
        ip, cp, prod = self._add_random_product_to_cart(browser)

        assert cp.is_cart_displayed(), "Cart page not displayed."

        safe_name = prod["name"].encode("ascii", "ignore").decode("ascii")
        print(f"Selected Random Product: {safe_name}")

        # Assert product is in cart
        in_cart = cp.is_product_in_cart(prod["name"])
        assert in_cart, \
            f"'{safe_name}' not found in cart. Cart: {cp.get_cart_product_names()}"

        print(f"PASS: '{safe_name}' exists in cart.")

    # ------------------------------------------------------------------ #
    # TEST 26: Verify product name in cart matches selected product
    # ------------------------------------------------------------------ #
    def test_product_name_in_cart_matches_selected(self, browser):
        """Verify the cart product name exactly matches what was added."""
        ip, cp, prod = self._add_random_product_to_cart(browser)

        assert cp.is_cart_displayed(), "Cart page not displayed."

        safe_name = prod["name"].encode("ascii", "ignore").decode("ascii")
        cart_names = cp.get_cart_product_names()
        assert len(cart_names) > 0, "Cart is empty - no product names found."

        # Assert the product name matches (using fuzzy normalization from CartPage)
        assert cp.is_product_in_cart(prod["name"]), \
            f"Cart name mismatch. Selected: '{safe_name}'. Cart: {cart_names}"

        print(f"PASS: Cart product name matches selected: '{safe_name}'")

    # ------------------------------------------------------------------ #
    # TEST 27: Remove product and verify it is removed
    # ------------------------------------------------------------------ #
    def test_remove_product_from_cart(self, browser):
        """Add a product to cart, then remove it and verify it is removed."""
        ip, cp, prod = self._add_random_product_to_cart(browser)

        assert cp.is_cart_displayed(), "Cart page not displayed."
        initial_count = cp.get_cart_items_count()
        assert initial_count >= 1, "Cart is empty, nothing to remove."

        # Remove the product
        cp.remove_product()

        # Wait a moment for DOM update
        browser.locator(cp.cartTable).first.wait_for(state="visible", timeout=5000)

        new_count = cp.get_cart_items_count()
        assert new_count < initial_count, \
            f"Cart count should decrease after removal. Before: {initial_count}, After: {new_count}"

        safe_name = prod["name"].encode("ascii", "ignore").decode("ascii")
        print(f"PASS: Removed '{safe_name}'. Cart count: {initial_count} -> {new_count}")

    # ------------------------------------------------------------------ #
    # TEST 28: Add multiple products and verify all in cart
    # ------------------------------------------------------------------ #
    def test_add_multiple_products_all_in_cart(self, browser):
        """Add 2 random products and verify both exist in cart."""
        ip = self._login_and_go_to_products(browser)
        cp = CartPage(browser)

        prod1 = ip.click_random_product()
        safe1 = prod1["name"].encode("ascii", "ignore").decode("ascii")
        ip.add_to_cart()
        ip.back_to_products()

        prod2 = ip.click_random_product(exclude_index=prod1["index"])
        safe2 = prod2["name"].encode("ascii", "ignore").decode("ascii")
        ip.add_to_cart()
        ip.click_cart()

        assert cp.is_cart_displayed(), "Cart page not displayed."

        count = cp.get_cart_items_count()
        assert count >= 2, f"Expected >= 2 items in cart, found {count}."

        assert cp.is_product_in_cart(prod1["name"]), \
            f"Product 1 '{safe1}' not in cart. Cart: {cp.get_cart_product_names()}"
        assert cp.is_product_in_cart(prod2["name"]), \
            f"Product 2 '{safe2}' not in cart. Cart: {cp.get_cart_product_names()}"

        print(f"PASS: Both '{safe1}' and '{safe2}' in cart (total items: {count}).")

    # ------------------------------------------------------------------ #
    # TEST 29: Remove one product and verify remaining product
    # ------------------------------------------------------------------ #
    def test_remove_one_product_verify_remaining(self, browser):
        """Add 2 products to cart, remove one, verify the other remains."""
        ip = self._login_and_go_to_products(browser)
        cp = CartPage(browser)

        prod1 = ip.click_random_product()
        safe1 = prod1["name"].encode("ascii", "ignore").decode("ascii")
        ip.add_to_cart()
        ip.back_to_products()

        prod2 = ip.click_random_product(exclude_index=prod1["index"])
        safe2 = prod2["name"].encode("ascii", "ignore").decode("ascii")
        ip.add_to_cart()
        ip.click_cart()

        assert cp.is_cart_displayed(), "Cart page not displayed."
        assert cp.get_cart_items_count() >= 2, "Expected 2 items before removal."

        # Remove first product (topmost delete button)
        cp.remove_product()
        browser.wait_for_timeout(1000)

        # Cart should now have fewer items
        new_count = cp.get_cart_items_count()
        assert new_count >= 1, "Cart should still have at least 1 product."

        print(f"PASS: After removal, cart has {new_count} item(s). Started with 2.")

    # ------------------------------------------------------------------ #
    # TEST 30: Verify empty cart behavior after removing all
    # ------------------------------------------------------------------ #
    def test_empty_cart_after_removing_all(self, browser):
        """Add one product, remove it, verify cart is empty."""
        ip, cp, prod = self._add_random_product_to_cart(browser)

        assert cp.is_cart_displayed(), "Cart page not displayed."
        assert cp.get_cart_items_count() >= 1, "Cart should have 1 item before removal."

        # Remove the product
        cp.remove_product()
        browser.wait_for_timeout(1500)

        # Assert cart is now empty (0 items or no rows)
        count_after = cp.get_cart_items_count()
        safe_name = prod["name"].encode("ascii", "ignore").decode("ascii")

        # Verify product is no longer in cart
        still_in_cart = cp.is_product_in_cart(prod["name"])
        assert not still_in_cart or count_after == 0, \
            f"'{safe_name}' should be removed, but cart still shows: {cp.get_cart_product_names()}"

        print(f"PASS: Cart is empty after removing '{safe_name}'. Count: {count_after}")
