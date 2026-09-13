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
        self.cartTable = "#cart_info_table"
        self.cartRows = "#cart_info_table tbody tr"
        self.cartProductNames = "td.cart_description h4 a"

    def _normalize(self, text: str) -> str:
        """Helper to normalize text for comparison ignoring unicode dash/case anomalies."""
        import re
        cleaned = re.sub(r'[^\w\s]', ' ', text or "")
        return " ".join(cleaned.lower().split())

    def safe_click(self, selector: str):
        loc = self.page.locator(selector).first
        loc.wait_for(state="attached", timeout=15000)
        loc.scroll_into_view_if_needed()
        try:
            loc.click(timeout=5000)
        except Exception:
            loc.evaluate("element => element.click()")

    def is_cart_displayed(self) -> bool:
        """Verifies that the cart page is visible."""
        try:
            self.page.locator(self.cartTable).first.wait_for(state="visible", timeout=10000)
            return "/view_cart" in self.page.url
        except Exception:
            return "/view_cart" in self.page.url

    def get_cart_product_names(self) -> list:
        """Returns the list of product names currently present in the cart."""
        try:
            self.page.locator(self.cartTable).first.wait_for(state="visible", timeout=10000)
            elements = self.page.locator(self.cartProductNames).all()
            names = [el.inner_text().strip() for el in elements if el.inner_text().strip()]
            return names
        except Exception:
            return []

    def is_product_in_cart(self, product_name: str) -> bool:
        """
        Validates if the given product name exists in the cart.
        Uses exact, substring, and normalized matching for complete reliability.
        """
        cart_names = self.get_cart_product_names()
        if not cart_names:
            return False

        p_norm = self._normalize(product_name)
        for name in cart_names:
            name_norm = self._normalize(name)
            if product_name.lower() in name.lower() or name.lower() in product_name.lower():
                return True
            if p_norm and (p_norm in name_norm or name_norm in p_norm):
                return True
        return False

    def get_cart_items_count(self) -> int:
        """Returns the total number of distinct product line items in the cart."""
        try:
            self.page.locator(self.cartTable).first.wait_for(state="visible", timeout=10000)
            return len(self.page.locator(self.cartRows).all())
        except Exception:
            return 0

    def get_product_quantity(self, product_name: str) -> int:
        """Returns the integer quantity of a specified product from the cart table."""
        try:
            rows = self.page.locator(self.cartRows).all()
            p_norm = self._normalize(product_name)
            for row in rows:
                desc = row.locator("td.cart_description h4 a").first
                if desc.count() > 0:
                    row_name = desc.inner_text().strip()
                    if self._normalize(row_name) in p_norm or p_norm in self._normalize(row_name):
                        qty_text = row.locator("td.cart_quantity button").first.inner_text().strip()
                        return int(qty_text) if qty_text.isdigit() else 1
        except Exception:
            pass
        return 1

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
        # Ensure navigation to /checkout with Playwright wait
        try:
            self.page.wait_for_url("**/checkout", timeout=10000)
        except Exception:
            try:
                self.page.locator(self.checkout_btn).first.click(force=True)
                self.page.wait_for_url("**/checkout", timeout=10000)
            except Exception:
                pass

    def continue_shopping(self):
        self.safe_click(self.continueShopping_btn)

    # Aliases for exact Java compatibility
    safeClick = safe_click
    removeProduct = remove_product
    removeRandomProduct = remove_random_product
    continueShopping = continue_shopping
    isCartDisplayed = is_cart_displayed
    getCartProductNames = get_cart_product_names
    isProductInCart = is_product_in_cart
    getCartItemsCount = get_cart_items_count
    getProductQuantity = get_product_quantity
