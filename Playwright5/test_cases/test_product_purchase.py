import os
import sys

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utility.config_reader import ConfigReader
from utility.helper import Helper
from utility.random_helper import RandomHelper
from utility.screenshot_helper import ScreenshotHelper

class ProductPurchaseTest:

    def test_purchase_product(self):

        # Launch Browser
        driver = Helper.start_browser(ConfigReader.get_property("browser"))

        # Step 1: Verify Home Page
        assert "automationexercise.com" in driver.url, "Failed to load Automation Exercise homepage."
        ScreenshotHelper.capture_screenshot(driver, "HomePage")

        # Create Page Objects
        login_page = LoginPage(driver)
        inventory_page = InventoryPage(driver)
        cart_page = CartPage(driver)
        checkout_page = CheckoutPage(driver)

        # Step 2: Navigate to Login Page and Verify
        driver.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
        assert login_page.is_login_page_displayed(), "Login page was not displayed."

        # Step 3: Login and Validate Authentication
        username = ConfigReader.get_property("username")
        password = ConfigReader.get_property("password")
        login_page.login(username, password)

        assert login_page.is_login_successful(), "Automation Exercise login failed."
        logged_in_user = login_page.get_logged_in_user()
        assert "Logged in as" in logged_in_user, f"Expected 'Logged in as' indicator, got: '{logged_in_user}'"
        assert login_page.is_at_home_or_products_page(), "User was not routed to the expected logged-in page."
        print(f"Login Verified: {logged_in_user}")
        ScreenshotHelper.capture_screenshot(driver, "LoginSuccess")

        # Step 4: Navigate to Products Catalog and Verify
        inventory_page.click_products()
        assert inventory_page.is_products_page_displayed(), "Products catalog page was not displayed."

        # Step 5: Dynamic Selection: Random Product 1
        prod1 = inventory_page.click_random_product()
        assert inventory_page.is_product_details_displayed(), f"Product 1 details page not displayed for '{prod1['name']}'."
        assert len(prod1["name"]) > 0, "Selected product 1 name is empty."

        # Set Dynamic Quantity for Product 1
        qty1 = inventory_page.set_random_quantity(min_qty=1, max_qty=3)
        ScreenshotHelper.capture_screenshot(driver, "Product1_Details")

        # Step 6: Add Product 1 to Cart and Assert Confirmation
        added1 = inventory_page.add_to_cart()
        assert added1, f"Failed to add Product 1 ('{prod1['name']}') to cart (confirmation modal not displayed)."
        ScreenshotHelper.capture_screenshot(driver, "Product1_Added")

        # Step 7: Return to Products Catalog and Verify
        inventory_page.back_to_products()
        assert inventory_page.is_products_page_displayed(), "Failed to navigate back to products catalog."
        ScreenshotHelper.capture_screenshot(driver, "InventoryPage")

        # Step 8: Dynamic Selection: Random Product 2 (guaranteed different from Product 1)
        prod2 = inventory_page.click_random_product(exclude_index=prod1["index"])
        assert prod2["index"] != prod1["index"], "Product 2 should be different from Product 1."
        assert inventory_page.is_product_details_displayed(), f"Product 2 details page not displayed for '{prod2['name']}'."
        assert len(prod2["name"]) > 0, "Selected product 2 name is empty."

        # Set Dynamic Quantity for Product 2
        qty2 = inventory_page.set_random_quantity(min_qty=1, max_qty=2)
        ScreenshotHelper.capture_screenshot(driver, "Product2_Details")

        # Step 9: Add Product 2 to Cart and Assert Confirmation
        added2 = inventory_page.add_to_cart()
        assert added2, f"Failed to add Product 2 ('{prod2['name']}') to cart (confirmation modal not displayed)."
        ScreenshotHelper.capture_screenshot(driver, "Product2_Added")

        # Step 10: Open Cart and Validate Contents & Quantities
        inventory_page.click_cart()
        ScreenshotHelper.capture_screenshot(driver, "CartPage")

        assert cart_page.is_cart_displayed(), "Cart page was not displayed."
        cart_count = cart_page.get_cart_items_count()
        assert cart_count >= 2, f"Expected at least 2 distinct products in cart, but found {cart_count}."

        # Explicit assertion: Cart contains randomly selected products
        assert cart_page.is_product_in_cart(prod1["name"]), f"Product 1 '{prod1['name']}' not found in cart."
        assert cart_page.is_product_in_cart(prod2["name"]), f"Product 2 '{prod2['name']}' not found in cart."

        # Explicit assertion: Selected quantities match cart quantities
        cart_qty1 = cart_page.get_product_quantity(prod1["name"])
        assert cart_qty1 == qty1, f"Product 1 quantity mismatch: expected {qty1}, but cart shows {cart_qty1}."
        cart_qty2 = cart_page.get_product_quantity(prod2["name"])
        assert cart_qty2 == qty2, f"Product 2 quantity mismatch: expected {qty2}, but cart shows {cart_qty2}."
        p1_safe = prod1['name'].encode('ascii', 'ignore').decode('ascii')
        p2_safe = prod2['name'].encode('ascii', 'ignore').decode('ascii')
        print(f"Cart Contents Verified: '{p1_safe}' (qty={cart_qty1}) & '{p2_safe}' (qty={cart_qty2})")

        # Step 11: Checkout Flow and Validation
        cart_page.checkout()
        assert checkout_page.is_checkout_page_displayed(), "Checkout page was not displayed successfully."
        ScreenshotHelper.capture_screenshot(driver, "CheckoutPage")

        # Step 12: Customer Details & Notes Validation
        cust = checkout_page.enter_customer_details()
        assert checkout_page.is_customer_info_accepted(cust["comment"]), "Customer order comments were not accepted."
        ScreenshotHelper.capture_screenshot(driver, "OrderComment")

        # Step 13: Proceed to Payment and Validate Payment Page
        checkout_page.click_continue()
        assert checkout_page.is_payment_page_displayed(), "Payment/Overview page was not displayed."
        ScreenshotHelper.capture_screenshot(driver, "PaymentPage")

        # Step 14: Dynamic Payment Details & Finish Order
        customer_full_name = f"{cust['first_name']} {cust['last_name']}"
        card_details = RandomHelper.get_random_card_details(customer_name=customer_full_name)
        checkout_page.click_finish(card_details=card_details)
        ScreenshotHelper.capture_screenshot(driver, "OrderCompleted")

        # Step 15: Assert Order Completion and Confirmation Message
        assert checkout_page.is_order_successful(), "Order was not completed successfully."
        confirmation_msg = checkout_page.get_order_confirmation_message()
        assert "order has been confirmed" in confirmation_msg.lower() or "order placed" in confirmation_msg.lower(), \
            f"Expected confirmation message, got: '{confirmation_msg}'"
        safe_conf_msg = confirmation_msg.encode('ascii', 'ignore').decode('ascii')
        print(f"Order Successfully Completed: {safe_conf_msg}")

        # Close Browser
        Helper.close_browser(driver)

    # Aliases for exact Java compatibility
    purchaseProduct = test_purchase_product


if __name__ == "__main__":
    test = ProductPurchaseTest()
    test.test_purchase_product()
