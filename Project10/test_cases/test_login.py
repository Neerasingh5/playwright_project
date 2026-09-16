import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.login_page import LoginPage
from utility.config_reader import ConfigReader
from utility.csv_helper import CSVHelper
from utility.helper import Helper
from utility.screenshot_helper import ScreenshotHelper


class LoginTest:
    """Test Case 1: Valid Login"""

    def test_valid_login(self):
        driver = Helper.start_browser(ConfigReader.get_property("browser"))
        login_page = LoginPage(driver)

        try:
            # Open login page
            driver.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
            time.sleep(2)

            assert login_page.is_login_page_displayed(), "Login page not displayed."
            ScreenshotHelper.capture_screenshot(driver, "LoginPage")

            # Read credentials from CSV
            csv = CSVHelper("CSVFiles/AutomationExercise_Valid_Login_Users.csv")
            row = csv.get_next_row()
            csv.close_csv()

            username = row[1].strip() if row else ConfigReader.get_property("username")
            password = row[2].strip() if row else ConfigReader.get_property("password")

            # Login
            login_page.login(username, password)
            time.sleep(3)

            # Assert login success
            assert login_page.is_login_successful(), f"Login failed for: {username}"
            logged_user = login_page.get_logged_in_user()
            assert "Logged in as" in logged_user, f"Expected 'Logged in as', got: '{logged_user}'"
            assert login_page.is_at_home_or_products_page(), "Not routed to home/products page."

            ScreenshotHelper.capture_screenshot(driver, "ValidLogin_Success")
            print(f"Login Test PASSED: {logged_user}")

        finally:
            Helper.close_browser(driver)


if __name__ == "__main__":
    LoginTest().test_valid_login()
