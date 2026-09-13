import os
import sys
import pytest
from playwright.sync_api import expect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.login_page import LoginPage
from utility.config_reader import ConfigReader


class LoginTest:
    """
    A. LOGIN TEST CASES - 8 independent tests covering all scenarios.
    """

    # ------------------------------------------------------------------ #
    # TEST 1: Login page is displayed
    # ------------------------------------------------------------------ #
    def test_login_page_is_displayed(self, browser):
        """Verify that navigating to /login shows the login form."""
        browser.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
        lp = LoginPage(browser)

        # Assert URL contains /login
        assert "/login" in browser.url, "Expected URL to contain '/login'"

        # Assert login form heading is visible
        expect(browser.locator(lp.loginFormHeading).first).to_be_visible()

        # Assert username field is visible
        expect(browser.locator(lp.txtUsername).first).to_be_visible()

        # Assert password field is visible
        expect(browser.locator(lp.txtPassword).first).to_be_visible()

        # Assert login button is visible
        expect(browser.locator(lp.btnLogin).first).to_be_visible()

        print("PASS: Login page displayed with all form elements.")

    # ------------------------------------------------------------------ #
    # TEST 2: Valid login
    # ------------------------------------------------------------------ #
    def test_valid_login(self, browser):
        """Login with valid username and password => reaches home, shows 'Logged in as'."""
        browser.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
        lp = LoginPage(browser)

        assert lp.is_login_page_displayed(), "Login page not displayed."

        lp.login(
            ConfigReader.get_property("username"),
            ConfigReader.get_property("password")
        )

        # Assert successful login indicator visible
        expect(browser.locator(lp.loginSuccess).first).to_be_visible()

        # Assert the text contains 'Logged in as'
        logged_user = lp.get_logged_in_user()
        assert "Logged in as" in logged_user, f"Expected 'Logged in as', got: '{logged_user}'"

        # Assert we are NOT on the login page anymore
        assert "/login" not in browser.url, "Should have left the login page after successful login."

        print(f"PASS: Valid login. {logged_user}")

    # ------------------------------------------------------------------ #
    # TEST 3: Invalid username
    # ------------------------------------------------------------------ #
    def test_login_with_invalid_username(self, browser):
        """Login with invalid username but valid password => shows error."""
        browser.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
        lp = LoginPage(browser)

        assert lp.is_login_page_displayed(), "Login page not displayed."
        lp.login("nonexistent_user_xyz123@invalid.com", ConfigReader.get_property("password"))

        # Assert error message is displayed
        assert lp.is_login_failed(), "Expected login failure but no error message was shown."

        err = lp.get_error_message()
        assert len(err) > 0, "Error message text should not be empty."
        assert "incorrect" in err.lower(), f"Expected 'incorrect' in error, got: '{err}'"

        # Assert still on login page
        assert "/login" in browser.url, "Should remain on login page after invalid login."

        print(f"PASS: Invalid username rejected. Error: '{err}'")

    # ------------------------------------------------------------------ #
    # TEST 4: Invalid password
    # ------------------------------------------------------------------ #
    def test_login_with_invalid_password(self, browser):
        """Login with valid username but wrong password => shows error."""
        browser.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
        lp = LoginPage(browser)

        assert lp.is_login_page_displayed(), "Login page not displayed."
        lp.login(ConfigReader.get_property("username"), "WrongPassword_9999!")

        # Assert error message is displayed
        assert lp.is_login_failed(), "Expected login failure but no error was shown."

        err = lp.get_error_message()
        assert len(err) > 0, "Error message text should not be empty."
        assert "incorrect" in err.lower(), f"Expected 'incorrect' in error, got: '{err}'"

        print(f"PASS: Invalid password rejected. Error: '{err}'")

    # ------------------------------------------------------------------ #
    # TEST 5: Invalid username AND invalid password
    # ------------------------------------------------------------------ #
    def test_login_with_invalid_username_and_password(self, browser):
        """Login with both invalid username and invalid password => shows error."""
        browser.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
        lp = LoginPage(browser)

        assert lp.is_login_page_displayed(), "Login page not displayed."
        lp.login("fake_user_99999@invalid.com", "FakePassword_99!")

        assert lp.is_login_failed(), "Expected login failure but no error message was shown."
        err = lp.get_error_message()
        assert len(err) > 0, "Error message text should not be empty."
        assert "incorrect" in err.lower(), f"Expected 'incorrect' in error, got: '{err}'"

        print(f"PASS: Both invalid credentials rejected. Error: '{err}'")

    # ------------------------------------------------------------------ #
    # TEST 6: Empty username
    # ------------------------------------------------------------------ #
    def test_login_with_empty_username(self, browser):
        """Login with empty username field => form should not submit / show error."""
        browser.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
        lp = LoginPage(browser)

        assert lp.is_login_page_displayed(), "Login page not displayed."

        # Fill only password, leave username empty
        browser.locator(lp.txtPassword).first.fill(ConfigReader.get_property("password"))
        browser.locator(lp.btnLogin).first.click()

        # Browser HTML5 validation or an error — we should NOT be logged in
        is_logged_in = lp.is_login_successful()
        assert not is_logged_in, "Should NOT be logged in with empty username."

        # Confirm we're still on or redirected back to login
        assert "/login" in browser.url or lp.is_login_page_displayed(), \
            "Expected to remain on login page with empty username."

        print("PASS: Empty username did not allow login.")

    # ------------------------------------------------------------------ #
    # TEST 7: Empty password
    # ------------------------------------------------------------------ #
    def test_login_with_empty_password(self, browser):
        """Login with empty password field => form should not submit / show error."""
        browser.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
        lp = LoginPage(browser)

        assert lp.is_login_page_displayed(), "Login page not displayed."

        # Fill only username, leave password empty
        browser.locator(lp.txtUsername).first.fill(ConfigReader.get_property("username"))
        browser.locator(lp.btnLogin).first.click()

        # Should NOT be logged in
        is_logged_in = lp.is_login_successful()
        assert not is_logged_in, "Should NOT be logged in with empty password."

        assert "/login" in browser.url or lp.is_login_page_displayed(), \
            "Expected to remain on login page with empty password."

        print("PASS: Empty password did not allow login.")

    # ------------------------------------------------------------------ #
    # TEST 8: Both username and password empty
    # ------------------------------------------------------------------ #
    def test_login_with_both_fields_empty(self, browser):
        """Login with both username and password empty => form validation prevents login."""
        browser.goto(ConfigReader.get_property("loginUrl"), wait_until="domcontentloaded")
        lp = LoginPage(browser)

        assert lp.is_login_page_displayed(), "Login page not displayed."
        assert lp.is_login_page_displayed(), "Login page not displayed."

        # Click login without filling anything
        browser.locator(lp.btnLogin).first.click()

        # Should NOT be logged in
        is_logged_in = lp.is_login_successful()
        assert not is_logged_in, "Should NOT be logged in with empty credentials."

        assert "/login" in browser.url or lp.is_login_page_displayed(), \
            "Expected to remain on login page with empty credentials."

        print("PASS: Both fields empty - login not allowed.")
