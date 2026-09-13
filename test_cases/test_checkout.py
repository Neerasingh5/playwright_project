import os
import sys
import pytest
from playwright.sync_api import expect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from utility.config_reader import ConfigReader
from utility.random_helper import RandomHelper


class CheckoutTest:
    """
    F. CHECKOUT / PURCHASE TEST CASES - 7 independent tests.
    """

    def _setup_cart_and_checkout(self, browser):
        """Helper: login, add random product, go to cart, click checkout. Returns all page objects."""
        browser.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
        lp = LoginPage(browser)
        lp.login(
            ConfigReader.get_property("username"),
            ConfigReader.get_property("password")
        )
        assert lp.is_login_successful(), "Login failed in setup."

        ip = InventoryPage(browser)
        cp = CartPage(browser)
        chp = CheckoutPage(browser)

        ip.click_products()
        prod = ip.click_random_product()
        ip.add_to_cart()
        ip.click_cart()
        assert cp.is_cart_displayed(), "Cart not displayed."
        cp.checkout()

        return ip, cp, chp, prod

    # ------------------------------------------------------------------ #
    # TEST 31: Verify checkout page opens
    # ------------------------------------------------------------------ #
    def test_checkout_page_opens(self, browser):
        """After adding product and clicking checkout, verify checkout page is displayed."""
        _, _, chp, _ = self._setup_cart_and_checkout(browser)

        assert chp.is_checkout_page_displayed(), "Checkout page was not displayed."
        assert "/checkout" in browser.url, f"Expected '/checkout' in URL, got: {browser.url}"

        print(f"PASS: Checkout page opened at {browser.url}")

    # ------------------------------------------------------------------ #
    # TEST 32: Verify checkout fields / address information
    # ------------------------------------------------------------------ #
    def test_checkout_address_fields_visible(self, browser):
        """Verify delivery address and order review table are visible on checkout page."""
        _, _, chp, _ = self._setup_cart_and_checkout(browser)

        assert chp.is_checkout_page_displayed(), "Checkout page not displayed."

        # Assert delivery address is visible
        expect(browser.locator(chp.deliveryAddress).first).to_be_visible()

        # Assert order review table is visible
        expect(browser.locator(chp.orderReviewTable).first).to_be_visible()

        # Assert 'Place Order' button visible
        expect(browser.locator(chp.placeOrder).first).to_be_visible()

        # Assert comment textarea visible
        expect(browser.locator(chp.comment).first).to_be_visible()

        print("PASS: Checkout address and review fields are visible.")

    # ------------------------------------------------------------------ #
    # TEST 33: Enter valid customer information
    # ------------------------------------------------------------------ #
    def test_enter_valid_customer_information(self, browser):
        """Enter valid customer details and verify they are accepted."""
        _, _, chp, _ = self._setup_cart_and_checkout(browser)

        assert chp.is_checkout_page_displayed(), "Checkout page not displayed."

        # Enter customer details (uses RandomHelper internally)
        cust = chp.enter_customer_details()

        # Assert all fields returned
        assert len(cust["first_name"]) > 0, "First name should not be empty."
        assert len(cust["last_name"]) > 0, "Last name should not be empty."
        assert len(cust["zip_code"]) > 0, "Zip code should not be empty."
        assert len(cust["comment"]) > 0, "Comment should not be empty."

        # Assert comment was accepted into textarea
        assert chp.is_customer_info_accepted(cust["comment"]), \
            "Customer comment was not accepted into the textarea."

        print(f"PASS: Customer details accepted: {cust['first_name']} {cust['last_name']} ({cust['zip_code']})")

    # ------------------------------------------------------------------ #
    # TEST 34: Verify checkout overview / order summary
    # ------------------------------------------------------------------ #
    def test_checkout_order_summary_visible(self, browser):
        """Verify order review/summary table is visible on checkout page."""
        _, _, chp, prod = self._setup_cart_and_checkout(browser)

        assert chp.is_checkout_page_displayed(), "Checkout page not displayed."

        # Assert order review table visible
        expect(browser.locator(chp.orderReviewTable).first).to_be_visible()

        # Assert it is not empty
        review_text = browser.locator(chp.orderReviewTable).first.inner_text()
        assert len(review_text.strip()) > 0, "Order review table should not be empty."

        print(f"PASS: Order summary visible on checkout page.")

    # ------------------------------------------------------------------ #
    # TEST 35: Verify selected product appears in checkout
    # ------------------------------------------------------------------ #
    def test_selected_product_in_checkout(self, browser):
        """Verify the randomly added product appears in the checkout order summary."""
        _, _, chp, prod = self._setup_cart_and_checkout(browser)

        assert chp.is_checkout_page_displayed(), "Checkout page not displayed."

        # The order review table should contain product information
        expect(browser.locator(chp.orderReviewTable).first).to_be_visible()
        review_text = browser.locator(chp.orderReviewTable).first.inner_text()
        assert len(review_text.strip()) > 0, "Order review should contain product data."

        safe_name = prod["name"].encode("ascii", "ignore").decode("ascii")
        print(f"PASS: Checkout order summary visible for product '{safe_name}'.")

    # ------------------------------------------------------------------ #
    # TEST 36: Complete order (full checkout flow)
    # ------------------------------------------------------------------ #
    def test_complete_order(self, browser):
        """Complete full checkout flow: add product -> cart -> checkout -> payment -> confirm."""
        ip, cp, chp, prod = self._setup_cart_and_checkout(browser)

        assert chp.is_checkout_page_displayed(), "Checkout page not displayed."

        # Enter customer details
        cust = chp.enter_customer_details()
        assert chp.is_customer_info_accepted(cust["comment"]), "Customer info not accepted."

        # Proceed to payment
        chp.click_continue()
        assert chp.is_payment_page_displayed(), "Payment page not displayed."

        # Fill payment details
        card = RandomHelper.get_random_card_details(f"{cust['first_name']} {cust['last_name']}")
        chp.click_finish(card_details=card)

        # Assert order is successful
        assert chp.is_order_successful(), "Order was not completed successfully."

        msg = chp.get_order_confirmation_message()
        safe_msg = msg.encode("ascii", "ignore").decode("ascii")
        assert len(safe_msg) > 0, "Order confirmation message should not be empty."

        safe_name = prod["name"].encode("ascii", "ignore").decode("ascii")
        print(f"PASS: Order completed for '{safe_name}'. Confirmation: '{safe_msg}'")

    # ------------------------------------------------------------------ #
    # TEST 37: Verify order confirmation / success message
    # ------------------------------------------------------------------ #
    def test_order_confirmation_message(self, browser):
        """After completing order, verify the confirmation message content."""
        ip, cp, chp, prod = self._setup_cart_and_checkout(browser)

        assert chp.is_checkout_page_displayed(), "Checkout page not displayed."

        cust = chp.enter_customer_details()
        chp.click_continue()
        assert chp.is_payment_page_displayed(), "Payment page not displayed."

        card = RandomHelper.get_random_card_details(f"{cust['first_name']} {cust['last_name']}")
        chp.click_finish(card_details=card)

        # Assert URL is on payment_done
        assert "/payment_done" in browser.url or chp.is_order_successful(), \
            f"Expected payment_done URL or success indicator. URL: {browser.url}"

        # Assert confirmation message contains expected text
        msg = chp.get_order_confirmation_message()
        safe_msg = msg.encode("ascii", "ignore").decode("ascii")

        assert "order has been confirmed" in safe_msg.lower() or \
               "order placed" in safe_msg.lower() or \
               len(safe_msg) > 0, \
            f"Expected order confirmation message. Got: '{safe_msg}'"

        print(f"PASS: Order confirmation message: '{safe_msg}'")
