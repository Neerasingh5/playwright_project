from playwright.sync_api import Page

class LoginPage:

    def __init__(self, driver: Page):
        self.driver = driver
        self.page = driver

        # Locators - Automation Exercise login page
        self.txtUsername = "input[data-qa='login-email']"
        self.txtPassword = "input[data-qa='login-password']"
        self.btnLogin = "button[data-qa='login-button']"
        self.loginFormHeading = ".login-form h2"
        self.errorMessage = ".login-form p"
        self.logoutBtn = "a[href='/logout']"

        # Used to verify successful login
        self.loginSuccess = "//a[contains(normalize-space(.),'Logged in as')]"

    def is_login_page_displayed(self) -> bool:
        """Verifies that the login page and its form are displayed."""
        try:
            self.page.locator(self.loginFormHeading).first.wait_for(state="visible", timeout=10000)
            return "/login" in self.page.url
        except Exception:
            return "/login" in self.page.url

    # Login Method - with explicit wait for fields to be interactive
    def login(self, username: str, password: str):
        user_loc = self.page.locator(self.txtUsername).first
        user_loc.wait_for(state="visible", timeout=10000)
        user_loc.fill(username)

        pass_loc = self.page.locator(self.txtPassword).first
        pass_loc.wait_for(state="visible", timeout=5000)
        pass_loc.fill(password)

        btn_loc = self.page.locator(self.btnLogin).first
        btn_loc.wait_for(state="visible", timeout=5000)
        btn_loc.click()

    # Verify Login Success
    def is_login_successful(self) -> bool:
        try:
            self.page.locator(self.loginSuccess).first.wait_for(state="visible", timeout=10000)
            return True
        except Exception:
            return self.page.locator(self.loginSuccess).count() > 0

    def get_logged_in_user(self) -> str:
        """Returns the logged-in text (e.g. 'Logged in as <username>')."""
        try:
            loc = self.page.locator(self.loginSuccess).first
            loc.wait_for(state="visible", timeout=5000)
            return loc.inner_text().strip()
        except Exception:
            return ""

    def is_login_failed(self) -> bool:
        """Checks if login error message is displayed for invalid credentials."""
        try:
            self.page.locator(self.errorMessage).first.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    def get_error_message(self) -> str:
        """Returns the text of the error message upon failed login."""
        try:
            loc = self.page.locator(self.errorMessage).first
            loc.wait_for(state="visible", timeout=5000)
            return loc.inner_text().strip()
        except Exception:
            return ""

    def is_at_home_or_products_page(self) -> bool:
        """Verifies that user has reached an authenticated home or products page."""
        url = self.page.url
        is_logged_in = self.page.locator(self.loginSuccess).count() > 0
        return is_logged_in and ("/login" not in url or url.endswith(".com/") or "/products" in url)

    def logout(self):
        """Logs out the user and waits for login page to reload cleanly."""
        try:
            logout_loc = self.page.locator(self.logoutBtn).first
            if logout_loc.is_visible():
                logout_loc.click()
                self.page.wait_for_url("**/login", timeout=5000)
        except Exception:
            pass

    # Aliases for exact Java compatibility
    isLoginPageDisplayed = is_login_page_displayed
    isLoginSuccessful = is_login_successful
    getLoggedInUser = get_logged_in_user
    isLoginFailed = is_login_failed
    getErrorMessage = get_error_message
    isAtHomeOrProductsPage = is_at_home_or_products_page
