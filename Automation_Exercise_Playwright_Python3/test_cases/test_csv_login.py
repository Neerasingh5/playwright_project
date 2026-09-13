import os
import sys
import time

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.login_page import LoginPage
from utility.csv_helper import CSVHelper
from utility.config_reader import ConfigReader
from utility.helper import Helper
from utility.screenshot_helper import ScreenshotHelper

class CSVLoginTest:

    csv_path = "CSVFiles/AutomationExercise_Valid_Login_Users.csv"

    def test_ddt_login(self):
        csv = CSVHelper(self.csv_path)

        # Launch Browser
        driver = Helper.start_browser(ConfigReader.get_property("browser"))
        login_page = LoginPage(driver)

        total = 0
        passed = 0
        failed = 0

        print("\n==============================================")
        print("      AUTOMATION EXERCISE LOGIN TEST RESULTS")
        print("==============================================")

        while True:
            csv_cell = csv.get_next_row()
            if csv_cell is None:
                break

            total += 1

            test_case_id = csv_cell[0]
            username = csv_cell[1]
            password = csv_cell[2]

            # Automation Exercise has a separate login page.
            driver.goto(ConfigReader.get_property("loginUrl"))

            time.sleep(1.5)

            login_page.login(username, password)

            time.sleep(2.0)

            if login_page.is_login_successful():
                print(f"{test_case_id} | {username} --> PASS")
                passed += 1
            else:
                print(f"{test_case_id} | {username} --> FAIL")
                failed += 1

            ScreenshotHelper.capture_screenshot(driver, test_case_id)

            # Return to Login Page for the next CSV row
            driver.goto(ConfigReader.get_property("loginUrl"))

        print("--------------------------------------------")
        print(f"Total Test Cases : {total}")
        print(f"Passed           : {passed}")
        print(f"Failed           : {failed}")

        Helper.close_browser(driver)
        csv.close_csv()

        assert failed == 0, "One or more CSV login test cases failed."

    # Alias for exact TestNG method name
    DDTLoginTest = test_ddt_login


if __name__ == "__main__":
    test = CSVLoginTest()
    test.test_ddt_login()
