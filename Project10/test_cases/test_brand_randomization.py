import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.cart_page import CartPage
from pages.products_page import ProductsPage
from utility.config_reader import ConfigReader
from utility.helper import Helper
from utility.screenshot_helper import ScreenshotHelper


class BrandRandomizationTest:
    """
    Test Case 2: Random Brand Selection + Validation
    Test Case 3: Random Brand + Add To Cart
    """

    # ---------------------------------------------------------------
    # Test Case 2: Random Brand Selection + Validation
    # ---------------------------------------------------------------
    def test_random_brand_selection(self):
        driver = Helper.start_browser(ConfigReader.get_property("browser"))
        products_page = ProductsPage(driver)

        try:
            # Login
            driver.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
            time.sleep(2)

            from pages.login_page import LoginPage
            login_page = LoginPage(driver)
            login_page.login(
                ConfigReader.get_property("username"),
                ConfigReader.get_property("password")
            )
            time.sleep(3)

            # Open Products
            products_page.click_products()
            time.sleep(2)
            assert products_page.is_products_page_displayed(), "Products page not displayed."
            ScreenshotHelper.capture_screenshot(driver, "TC2_ProductsPage")

            # Get available brands and randomly select one brand
            brand = products_page.select_random_brand()
            time.sleep(2)

            # Assertions
            assert brand != "", "Selected brand name should not be empty."
            assert products_page.is_brand_displayed(brand), f"Brand page not displayed for '{brand}'."

            ScreenshotHelper.capture_screenshot(driver, f"TC2_Brand_{brand.replace(' ', '_')}")
            print(f"TC2 PASSED — Brand selected and verified: '{brand}'")

        finally:
            Helper.close_browser(driver)

    # ---------------------------------------------------------------
    # Test Case 3: Random Brand + Add To Cart
    # ---------------------------------------------------------------
    def test_random_brand_add_to_cart(self):
        driver = Helper.start_browser(ConfigReader.get_property("browser"))
        products_page = ProductsPage(driver)
        cart_page = CartPage(driver)

        try:
            # Login
            driver.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
            time.sleep(2)

            from pages.login_page import LoginPage
            login_page = LoginPage(driver)
            login_page.login(
                ConfigReader.get_property("username"),
                ConfigReader.get_property("password")
            )
            time.sleep(3)

            # Products
            products_page.click_products()
            time.sleep(2)

            # Randomly select a brand
            brand = products_page.select_random_brand()
            time.sleep(2)

            # Select a random product from that selected brand
            product = products_page.select_random_product()
            time.sleep(2)

            # Add product to cart
            products_page.add_to_cart()
            time.sleep(2)

            # Open Cart
            cart_page.open_cart()
            time.sleep(2)

            # Verify the selected product is in the cart
            assert cart_page.is_product_present(product), f"Product '{product}' not found in cart."
            ScreenshotHelper.capture_screenshot(driver, "TC3_CartVerified")
            print(f"TC3 PASSED — Product '{product}' from brand '{brand}' is verified in cart.")

        finally:
            Helper.close_browser(driver)


if __name__ == "__main__":
    t = BrandRandomizationTest()
    t.test_random_brand_selection()
    t.test_random_brand_add_to_cart()
