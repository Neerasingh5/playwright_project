import random
import re
import time
from playwright.sync_api import Page
from pages.inventory_page import InventoryPage


class ProductsPage(InventoryPage):
    """
    Page Object for the Products page.
    Contains brand randomization, search, and cart methods.
    """

    def __init__(self, driver: Page):
        super().__init__(driver)

        # Brand locators (left sidebar on Products page)
        self.brandLinks   = ".brands-name ul li a"
        self.brandTitle   = ".features_items .title"

        # Search locators
        self.searchInput  = "#search_product"
        self.searchBtn    = "#submit_search"

        # Product info cards
        self.productNames = ".features_items .productinfo p"

    # ------------------------------------------------------------------
    # BRAND RANDOMIZATION
    # ------------------------------------------------------------------

    def select_random_brand(self) -> str:
        """
        Reads available brands from the left sidebar,
        randomly picks ONE using Python's random module,
        clicks it, and returns the brand name.
        """
        # Wait for brands to appear
        self.page.locator(self.brandLinks).first.wait_for(state="visible", timeout=15000)

        brands = self.page.locator(self.brandLinks)
        count = brands.count()

        if count == 0:
            raise RuntimeError("No brands found on the Products page.")

        # Pick a random index
        index = random.randint(0, count - 1)

        brand = brands.nth(index)
        raw_name = brand.inner_text()

        # Clean up text like "(6)\nPOLO" → "POLO"
        brand_name = re.sub(r'\(\d+\)', '', raw_name).strip()

        # Click the brand
        brand.scroll_into_view_if_needed()
        try:
            brand.click(timeout=5000)
        except Exception:
            brand.evaluate("el => el.click()")

        # Wait for brand page to load
        try:
            self.page.wait_for_url("**/brand_products/**", timeout=10000)
        except Exception:
            pass

        # Wait for page title to appear
        try:
            self.page.locator(self.brandTitle).first.wait_for(state="visible", timeout=10000)
        except Exception:
            pass

        print(f"Selected Brand: '{brand_name}'")
        return brand_name

    def is_brand_page_displayed(self, brand_name: str = "") -> bool:
        """Returns True if the brand products page is shown with the correct brand name in the header."""
        if "/brand_products/" not in self.page.url:
            return False
        if brand_name:
            header = self.get_brand_page_title()
            return brand_name.upper() in header.upper()
        return True

    def get_brand_page_title(self) -> str:
        """Returns the page header text, e.g. 'BRAND - POLO PRODUCTS'."""
        try:
            loc = self.page.locator(self.brandTitle).first
            loc.wait_for(state="visible", timeout=8000)
            return loc.inner_text().strip()
        except Exception:
            return ""

    def get_brand_product_names(self) -> list:
        """Returns list of product names shown on the brand page."""
        try:
            self.page.locator(self.productNames).first.wait_for(state="visible", timeout=10000)
            return [el.inner_text().strip() for el in self.page.locator(self.productNames).all()]
        except Exception:
            return []

    def is_brand_displayed(self, brand_name: str = "") -> bool:
        """Helper to verify selected brand page is displayed."""
        return self.is_brand_page_displayed(brand_name)

    def select_random_product(self) -> str:
        """
        Selects a random product from the products displayed for the selected brand.
        Clicks the product to open details, and returns product name.
        """
        # Product links for current brand
        products = self.page.locator(".features_items .productinfo p")
        count = products.count()

        if count == 0:
            raise RuntimeError("No products found for the selected brand.")

        # Pick random index
        index = random.randint(0, count - 1)

        product = products.nth(index)
        product_name = product.inner_text().strip()

        # Click the product details link corresponding to this product
        details_links = self.page.locator(self.productDetailsLinks)
        product_link = details_links.nth(index)
        product_link.scroll_into_view_if_needed()
        try:
            product_link.click(timeout=5000)
        except Exception:
            product_link.evaluate("el => el.click()")

        # Wait for product detail page to load
        try:
            self.page.locator(self.addToCart_btn).first.wait_for(state="visible", timeout=10000)
        except Exception:
            pass

        print(f"Selected Product: '{product_name}'")
        return product_name

    def add_to_cart(self):
        """Adds product to cart from product details page and dismisses modal."""
        super().add_to_cart()

    # ------------------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------------------

    def search_product(self, product_name: str):
        """
        Searches for a product using the search bar.
        If search input is not on current page, navigates to /products first.
        """
        # Brand page does not have search bar — go back to Products
        if self.page.locator(self.searchInput).count() == 0:
            self.click_products()

        search_box = self.page.locator(self.searchInput).first
        search_box.wait_for(state="visible", timeout=10000)
        search_box.fill(product_name)

        self.page.locator(self.searchBtn).first.click()

        # Wait for results to appear
        try:
            self.page.locator(self.brandTitle).first.wait_for(state="visible", timeout=10000)
        except Exception:
            pass

        print(f"Searched for: '{product_name}'")

    def is_search_result_displayed(self) -> bool:
        """Returns True if 'SEARCHED PRODUCTS' header is shown."""
        try:
            title = self.get_brand_page_title()
            return "SEARCHED PRODUCTS" in title.upper()
        except Exception:
            return False

    def get_searched_products(self) -> list:
        """Returns list of product names from the search results."""
        return self.get_brand_product_names()

    # ------------------------------------------------------------------
    # ADD TO CART (from search results)
    # ------------------------------------------------------------------

    def add_first_searched_product_to_cart(self) -> str:
        """
        Clicks on the first product from search results,
        adds it to cart, and dismisses the modal.
        Returns the product name.
        """
        products = self.get_searched_products()
        prod_name = products[0] if products else "Searched Product"

        # Click View Product link
        details_link = self.page.locator(self.productDetailsLinks).first
        if details_link.is_visible():
            details_link.click()
            self.page.locator(self.addToCart_btn).first.wait_for(state="visible", timeout=10000)
            self.add_to_cart()
        else:
            self.safe_click(self.addToCartFromCard)
            self.continue_shopping()

        return prod_name
