from playwright.sync_api import Page

class LoginPage:

    def __init__(self, driver: Page):
        self.driver = driver
        self.page = driver

        # Locators - Automation Exercise login page
        self.txtUsername = "input[data-qa='login-email']"
        self.txtPassword = "input[data-qa='login-password']"
        self.btnLogin = "button[data-qa='login-button']"

        # Used to verify successful login
        self.loginSuccess = "//a[contains(normalize-space(.),'Logged in as')]"

    # Login Method - same method structure as the original project
    def login(self, username: str, password: str):
        self.page.fill(self.txtUsername, username)
        self.page.fill(self.txtPassword, password)
        self.page.click(self.btnLogin)

    # Verify Login Success
    def is_login_successful(self) -> bool:
        try:
            self.page.locator(self.loginSuccess).wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return self.page.locator(self.loginSuccess).count() > 0

    # Alias for exact Java compatibility
    isLoginSuccessful = is_login_successful
