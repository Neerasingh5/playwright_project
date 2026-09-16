import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from utility.config_reader import ConfigReader
from utility.helper import Helper
from utility.random_helper import RandomHelper
from utility.screenshot_helper import ScreenshotHelper


class ProductPurchaseTest:
    """
    Test Case 4: End-to-End Product Purchase
    Login → Products → Random Brand → Random Product from selected brand → Add To Cart → Open Cart → Checkout → Customer Details → Continue → Finish → Verify Order Successful
    """

    def test_purchase_product(self):
        driver = Helper.start_browser(ConfigReader.get_property("browser"))

        try:
            login_page    = LoginPage(driver)
            products_page = ProductsPage(driver)
            cart_page     = CartPage(driver)
            checkout_page = CheckoutPage(driver)

            # ---- Step 1: Login ----
            driver.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
            time.sleep(2)

            assert login_page.is_login_page_displayed(), "Login page not displayed."

            login_page.login(
                ConfigReader.get_property("username"),
                ConfigReader.get_property("password")
            )
            time.sleep(3)

            assert login_page.is_login_successful(), "Login failed."
            logged_user = login_page.get_logged_in_user()
            assert "Logged in as" in logged_user, f"Expected 'Logged in as', got: '{logged_user}'"
            print(f"Logged in: {logged_user}")
            ScreenshotHelper.capture_screenshot(driver, "TC4_Login")

            # ---- Step 2: Open Products ----
            products_page.click_products()
            time.sleep(2)
            assert products_page.is_products_page_displayed(), "Products page not displayed."

            # ---- Step 3: Random Brand ----
            brand = products_page.select_random_brand()
            time.sleep(2)

            assert brand != "", "Brand name should not be empty."
            assert products_page.is_brand_displayed(brand), f"Brand page not displayed for '{brand}'."
            ScreenshotHelper.capture_screenshot(driver, "TC4_BrandSelected")

            # ---- Step 4: Random Product from selected brand ----
            product = products_page.select_random_product()
            time.sleep(2)

            # ---- Step 5: Add To Cart ----
            products_page.add_to_cart()
            time.sleep(2)
            ScreenshotHelper.capture_screenshot(driver, "TC4_ProductAdded")

            # ---- Step 6: Open Cart ----
            cart_page.open_cart()
            time.sleep(2)

            assert cart_page.is_cart_displayed(), "Cart not displayed."
            assert cart_page.is_product_present(product), f"'{product}' not in cart."
            print(f"Cart verified: '{product}' present.")
            ScreenshotHelper.capture_screenshot(driver, "TC4_Cart")

            # ---- Step 7: Checkout ----
            cart_page.checkout()
            time.sleep(2)

            assert checkout_page.is_checkout_page_displayed(), "Checkout page not displayed."
            ScreenshotHelper.capture_screenshot(driver, "TC4_Checkout")

            # ---- Step 8: Enter Customer Details ----
            cust = checkout_page.enter_customer_details()
            assert checkout_page.is_customer_info_accepted(cust["comment"]), "Order comments not saved."

            # ---- Step 9: Continue (Place Order) ----
            checkout_page.click_continue()
            time.sleep(2)
            assert checkout_page.is_payment_page_displayed(), "Payment page not displayed."
            ScreenshotHelper.capture_screenshot(driver, "TC4_Payment")

            # ---- Step 10: Finish (Payment) ----
            checkout_page.click_finish()
            time.sleep(2)
            ScreenshotHelper.capture_screenshot(driver, "TC4_OrderDone")

            # ---- Step 11: Verify Order Successful ----
            assert checkout_page.is_order_successful(), "Order was not successful."
            msg = checkout_page.get_order_confirmation_message()
            assert "order has been confirmed" in msg.lower() or "order placed" in msg.lower(), \
                f"Unexpected confirmation message: '{msg}'"
            print(f"TC4 PASSED — Order confirmed: {msg}")

        finally:
            Helper.close_browser(driver)

    # Alias
    purchaseProduct = test_purchase_product


if __name__ == "__main__":
    ProductPurchaseTest().test_purchase_product()
