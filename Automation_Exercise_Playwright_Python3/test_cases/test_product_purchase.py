import os
import sys
import time

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utility.config_reader import ConfigReader
from utility.helper import Helper
from utility.screenshot_helper import ScreenshotHelper

class ProductPurchaseTest:

    def test_purchase_product(self):

        # Launch Browser
        driver = Helper.start_browser(ConfigReader.get_property("browser"))

        # Home Page
        ScreenshotHelper.capture_screenshot(driver, "HomePage")

        # Create Page Objects
        login_page = LoginPage(driver)
        inventory_page = InventoryPage(driver)
        cart_page = CartPage(driver)
        checkout_page = CheckoutPage(driver)

        # Login
        driver.goto(ConfigReader.get_property("loginUrl"))
        login_page.login(
            ConfigReader.get_property("username"),
            ConfigReader.get_property("password")
        )
        time.sleep(2.0)

        assert login_page.is_login_successful(), "Automation Exercise login failed."
        ScreenshotHelper.capture_screenshot(driver, "LoginSuccess")

        # Navigate to Products Page
        inventory_page.click_products()
        time.sleep(1.5)

        # Dynamic Selection: Random Product 1
        prod1 = inventory_page.click_random_product()
        time.sleep(1.0)
        # Dynamic quantity for product 1
        inventory_page.set_random_quantity(min_qty=1, max_qty=3)
        ScreenshotHelper.capture_screenshot(driver, f"Product1_Details")

        inventory_page.add_to_cart()
        time.sleep(1.0)
        ScreenshotHelper.capture_screenshot(driver, f"Product1_Added")

        # Go back to Products Page
        inventory_page.back_to_products()
        time.sleep(1.0)
        ScreenshotHelper.capture_screenshot(driver, "InventoryPage")

        # Dynamic Selection: Random Product 2 (guaranteed different from Product 1)
        prod2 = inventory_page.click_random_product(exclude_index=prod1["index"])
        time.sleep(1.0)
        # Dynamic quantity for product 2
        inventory_page.set_random_quantity(min_qty=1, max_qty=2)
        ScreenshotHelper.capture_screenshot(driver, f"Product2_Details")

        inventory_page.add_to_cart()
        time.sleep(1.0)
        ScreenshotHelper.capture_screenshot(driver, f"Product2_Added")

        # Cart
        inventory_page.click_cart()
        time.sleep(1.0)
        ScreenshotHelper.capture_screenshot(driver, "CartPage")

        assert cart_page.is_cart_displayed(), "Cart page was not displayed."

        # Checkout
        cart_page.checkout()
        time.sleep(1.0)
        ScreenshotHelper.capture_screenshot(driver, "CheckoutPage")

        # Dynamic customer details and randomized delivery notes
        checkout_page.enter_customer_details()
        time.sleep(0.5)
        ScreenshotHelper.capture_screenshot(driver, "OrderComment")

        checkout_page.click_continue()
        time.sleep(1.0)
        ScreenshotHelper.capture_screenshot(driver, "PaymentPage")

        # Dynamic payment details & complete order
        checkout_page.click_finish()
        time.sleep(1.5)
        ScreenshotHelper.capture_screenshot(driver, "OrderCompleted")

        assert checkout_page.is_order_successful(), "Order was not completed successfully."

        # Close Browser
        Helper.close_browser(driver)

    # Aliases for exact Java compatibility
    purchaseProduct = test_purchase_product


if __name__ == "__main__":
    test = ProductPurchaseTest()
    test.test_purchase_product()
