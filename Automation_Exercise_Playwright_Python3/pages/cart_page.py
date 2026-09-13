import random
from playwright.sync_api import Page

class CartPage:

    def __init__(self, driver: Page):
        self.driver = driver
        self.page = driver

        # Automation Exercise locators
        self.removeProduct_btn = "(//a[contains(@class,'cart_quantity_delete')])[1]"
        self.allDeleteButtons = "a.cart_quantity_delete"
        self.checkout_btn = "a.check_out"
        self.continueShopping_btn = "a[href='/products']"

    def safe_click(self, selector: str):
        loc = self.page.locator(selector).first
        loc.wait_for(state="attached", timeout=15000)
        loc.scroll_into_view_if_needed()
        try:
            loc.click(timeout=5000)
        except Exception:
            loc.evaluate("element => element.click()")

    def remove_product(self):
        self.safe_click(self.removeProduct_btn)

    def remove_random_product(self) -> bool:
        """Dynamically removes a randomly chosen product from the cart if items exist."""
        try:
            buttons = self.page.locator(self.allDeleteButtons).all()
            if not buttons:
                return False
            chosen = random.choice(buttons)
            chosen.scroll_into_view_if_needed()
            try:
                chosen.click(timeout=5000)
            except Exception:
                chosen.evaluate("element => element.click()")
            return True
        except Exception:
            return False

    def checkout(self):
        self.safe_click(self.checkout_btn)
        # Ensure navigation to /checkout
        if "/checkout" not in self.page.url:
            try:
                self.page.wait_for_url("**/checkout", timeout=5000)
            except Exception:
                # Force click or direct JS click if first click was swallowed
                try:
                    self.page.locator(self.checkout_btn).first.click(force=True)
                    self.page.wait_for_url("**/checkout", timeout=5000)
                except Exception:
                    pass

    def continue_shopping(self):
        self.safe_click(self.continueShopping_btn)

    def is_cart_displayed(self) -> bool:
        return "/view_cart" in self.page.url

    # Aliases for exact Java compatibility
    safeClick = safe_click
    removeProduct = remove_product
    removeRandomProduct = remove_random_product
    continueShopping = continue_shopping
    isCartDisplayed = is_cart_displayed
