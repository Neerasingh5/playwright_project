import os
import sys
import csv
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.login_page import LoginPage
from utility.config_reader import ConfigReader

# ------------------------------------------------------------------ #
# Helpers to load CSV data
# ------------------------------------------------------------------ #
def _load_csv(filename):
    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "CSVFiles", filename
    )
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def _get_row_by_tc(filename, tc_id):
    for row in _load_csv(filename):
        if row["TestCaseID"].strip() == tc_id:
            return row
    return None


CSV_FILE = "AutomationExercise_Login_TestData.csv"


class CSVLoginTest:
    """
    B. CSV / DATA-DRIVEN LOGIN TESTS - 4 separate, independent tests.
    Each uses its own CSV row and asserts the expected result.
    """

    # ------------------------------------------------------------------ #
    # TEST 9: Valid login from CSV (TC001)
    # ------------------------------------------------------------------ #
    def test_csv_valid_login(self, browser):
        """TC001 from CSV: valid credentials => login successful."""
        row = _get_row_by_tc(CSV_FILE, "TC001")
        assert row is not None, "TC001 row not found in CSV."

        browser.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
        lp = LoginPage(browser)

        assert lp.is_login_page_displayed(), "Login page not displayed."
        lp.login(row["Username"].strip(), row["Password"].strip())

        expected = row["ExpectedResult"].strip()
        assert "success" in expected.lower(), f"CSV expected result should be 'Login successful', got: '{expected}'"

        # Assert actual login succeeded
        assert lp.is_login_successful(), f"TC001: Expected successful login for '{row['Username']}'"
        logged = lp.get_logged_in_user()
        assert "Logged in as" in logged, f"TC001: 'Logged in as' not found. Got: '{logged}'"

        print(f"PASS CSV TC001: {logged}")

    # ------------------------------------------------------------------ #
    # TEST 10: Invalid username from CSV (TC002)
    # ------------------------------------------------------------------ #
    def test_csv_invalid_username(self, browser):
        """TC002 from CSV: invalid username => login failed."""
        row = _get_row_by_tc(CSV_FILE, "TC002")
        assert row is not None, "TC002 row not found in CSV."

        browser.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
        lp = LoginPage(browser)

        assert lp.is_login_page_displayed(), "Login page not displayed."
        lp.login(row["Username"].strip(), row["Password"].strip())

        expected = row["ExpectedResult"].strip()
        assert "fail" in expected.lower(), f"CSV expected result should be 'Login failed', got: '{expected}'"

        # Assert login was rejected
        assert lp.is_login_failed(), f"TC002: Expected login failure for invalid user '{row['Username']}'"
        err = lp.get_error_message()
        assert len(err) > 0, "TC002: Error message text should not be empty."
        assert "incorrect" in err.lower(), f"TC002: Expected 'incorrect' in error, got: '{err}'"

        print(f"PASS CSV TC002: Rejected with '{err}'")

    # ------------------------------------------------------------------ #
    # TEST 11: Invalid password from CSV (TC003)
    # ------------------------------------------------------------------ #
    def test_csv_invalid_password(self, browser):
        """TC003 from CSV: valid username + wrong password => login failed."""
        row = _get_row_by_tc(CSV_FILE, "TC003")
        assert row is not None, "TC003 row not found in CSV."

        browser.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
        lp = LoginPage(browser)

        assert lp.is_login_page_displayed(), "Login page not displayed."
        lp.login(row["Username"].strip(), row["Password"].strip())

        expected = row["ExpectedResult"].strip()
        assert "fail" in expected.lower(), f"CSV expected result should be 'Login failed', got: '{expected}'"

        assert lp.is_login_failed(), f"TC003: Expected login failure for wrong password."
        err = lp.get_error_message()
        assert len(err) > 0, "TC003: Error message should not be empty."
        assert "incorrect" in err.lower(), f"TC003: Expected 'incorrect' in error, got: '{err}'"

        print(f"PASS CSV TC003: Wrong password rejected with '{err}'")

    # ------------------------------------------------------------------ #
    # TEST 12: Both invalid from CSV (TC004)
    # ------------------------------------------------------------------ #
    def test_csv_invalid_username_and_password(self, browser):
        """TC004 from CSV: invalid username + wrong password => login failed."""
        row = _get_row_by_tc(CSV_FILE, "TC004")
        assert row is not None, "TC004 row not found in CSV."

        browser.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
        lp = LoginPage(browser)

        assert lp.is_login_page_displayed(), "Login page not displayed."
        lp.login(row["Username"].strip(), row["Password"].strip())

        expected = row["ExpectedResult"].strip()
        assert "fail" in expected.lower(), f"CSV expected result should be 'Login failed', got: '{expected}'"

        assert lp.is_login_failed(), f"TC004: Expected login failure for both invalid credentials."
        err = lp.get_error_message()
        assert len(err) > 0, "TC004: Error message should not be empty."
        assert "incorrect" in err.lower(), f"TC004: Expected 'incorrect' in error, got: '{err}'"

        print(f"PASS CSV TC004: Both invalid rejected with '{err}'")
