from playwright.sync_api import Page
from utility.config_reader import ConfigReader
from utility.random_helper import RandomHelper

class InventoryPage:

    def __init__(self, driver: Page):
        self.driver = driver
        self.page = driver

        # Automation Exercise locators
        self.productsLink = "a[href='/products']"
        self.firstProduct = "a[href='/product_details/1']"
        self.secondProduct = "a[href='/product_details/2']"
        self.productDetailsLinks = "a[href^='/product_details/']"
        self.productTitle = ".product-information h2"
        self.quantityInput = "input#quantity"
        self.addToCart_btn = "button.cart"
        self.addToCartFromCard = "(//div[contains(@class,'product-overlay')]//a[contains(@class,'add-to-cart')])[1]"
        self.secondAddToCartFromCard = "(//div[contains(@class,'product-overlay')]//a[contains(@class,'add-to-cart')])[2]"
        self.continueShopping_btn = "button.btn-success"
        self.cartButton = "a[href='/view_cart']"

    def safe_click(self, selector: str):
        loc = self.page.locator(selector).first
        loc.wait_for(state="attached", timeout=15000)
        loc.scroll_into_view_if_needed()
        try:
            loc.click(timeout=5000)
        except Exception:
            # Fallback to direct JS click if overlay intercepts
            loc.evaluate("element => element.click()")

    def click_random_product(self, exclude_index: int = None) -> dict:
        """
        Dynamically picks a random product from all available products on the page.
        Guarantees different product selection if exclude_index is provided.
        """
        self.page.wait_for_selector(self.productDetailsLinks, state="visible", timeout=15000)
        links = self.page.locator(self.productDetailsLinks).all()
        total_count = len(links)

        exclude = [exclude_index] if exclude_index is not None else []
        selected_index = RandomHelper.pick_random_index(total_count, exclude_indices=exclude)

        target_link = links[selected_index]
        target_link.scroll_into_view_if_needed()
        try:
            target_link.click(timeout=5000)
        except Exception:
            target_link.evaluate("element => element.click()")

        # Wait for product detail page to display
        self.page.wait_for_selector(self.addToCart_btn, state="visible", timeout=15000)

        product_name = ""
        try:
            product_name = self.page.locator(self.productTitle).first.inner_text().strip()
        except Exception:
            product_name = f"Product_{selected_index + 1}"

        print(f"Selected Random Product [{selected_index + 1}/{total_count}]: {product_name}")
        return {
            "index": selected_index,
            "name": product_name
        }

    def set_quantity(self, qty: int):
        """Sets product quantity on product details page."""
        loc = self.page.locator(self.quantityInput).first
        loc.wait_for(state="visible", timeout=5000)
        loc.fill(str(qty))

    def set_random_quantity(self, min_qty: int = 1, max_qty: int = 3) -> int:
        """Dynamically generates and sets a random product quantity."""
        qty = RandomHelper.get_random_quantity(min_qty, max_qty)
        self.set_quantity(qty)
        print(f"Set Random Quantity: {qty}")
        return qty

    def click_backpack(self):
        """Original method retained; clicks first product or random if called."""
        self.safe_click(self.firstProduct)

    def click_bike_light(self):
        """Original method retained; clicks second product or random if called."""
        self.safe_click(self.secondProduct)

    def add_to_cart(self):
        self.safe_click(self.addToCart_btn)

        try:
            cont_btn = self.page.locator(self.continueShopping_btn).first
            cont_btn.wait_for(state="visible", timeout=5000)
            cont_btn.evaluate("element => element.click()")
        except Exception:
            pass

    def back_to_products(self):
        try:
            self.safe_click(self.productsLink)
            if "/products" not in self.page.url:
                self.page.goto(ConfigReader.get_property("productsUrl") or "https://automationexercise.com/products")
        except Exception:
            self.page.goto(ConfigReader.get_property("productsUrl") or "https://automationexercise.com/products")

    def click_cart(self):
        self.safe_click(self.cartButton)

    def click_products(self):
        try:
            self.safe_click(self.productsLink)
            if "/products" not in self.page.url:
                self.page.goto(ConfigReader.get_property("productsUrl") or "https://automationexercise.com/products")
        except Exception:
            self.page.goto(ConfigReader.get_property("productsUrl") or "https://automationexercise.com/products")

    def add_first_product_from_products_page(self):
        self.safe_click(self.addToCartFromCard)

    def add_second_product_from_products_page(self):
        self.safe_click(self.secondAddToCartFromCard)

    def continue_shopping(self):
        self.safe_click(self.continueShopping_btn)

    # Aliases for exact Java compatibility
    safeClick = safe_click
    clickBackpack = click_backpack
    clickBikeLight = click_bike_light
    clickRandomProduct = click_random_product
    setQuantity = set_quantity
    setRandomQuantity = set_random_quantity
    addToCart = add_to_cart
    backToProducts = back_to_products
    clickCart = click_cart
    clickProducts = click_products
    addFirstProductFromProductsPage = add_first_product_from_products_page
    addSecondProductFromProductsPage = add_second_product_from_products_page
    continueShopping = continue_shopping
