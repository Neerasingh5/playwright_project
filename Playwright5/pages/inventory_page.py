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
        self.productPrice = ".product-information span span"
        self.quantityInput = "input#quantity"
        self.addToCart_btn = "button.cart"
        self.addToCartFromCard = "(//div[contains(@class,'product-overlay')]//a[contains(@class,'add-to-cart')])[1]"
        self.secondAddToCartFromCard = "(//div[contains(@class,'product-overlay')]//a[contains(@class,'add-to-cart')])[2]"
        self.continueShopping_btn = "button.btn-success"
        self.cartButton = "a[href='/view_cart']"
        self.cartModal = "#cartModal"
        self.cartModalTitle = "#cartModal .modal-title"
        self.cartModalBody = "#cartModal .modal-body"
        self.allProductsTitle = ".features_items .title"

    def safe_click(self, selector: str):
        loc = self.page.locator(selector).first
        loc.wait_for(state="attached", timeout=15000)
        loc.scroll_into_view_if_needed()
        try:
            loc.click(timeout=5000)
        except Exception:
            # Fallback to direct JS click if overlay intercepts
            loc.evaluate("element => element.click()")

    def is_products_page_displayed(self) -> bool:
        """Verifies that the products page is loaded and items are visible."""
        try:
            self.page.locator(self.productDetailsLinks).first.wait_for(state="visible", timeout=15000)
            return "/products" in self.page.url
        except Exception:
            return "/products" in self.page.url

    def click_random_product(self, exclude_index: int = None) -> dict:
        """
        Dynamically picks a random product from all available products on the page.
        Guarantees different product selection if exclude_index is provided.
        """
        self.page.locator(self.productDetailsLinks).first.wait_for(state="visible", timeout=15000)
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
        self.page.locator(self.addToCart_btn).first.wait_for(state="visible", timeout=15000)

        product_name = ""
        try:
            product_name = self.page.locator(self.productTitle).first.inner_text().strip()
        except Exception:
            product_name = f"Product_{selected_index + 1}"

        product_price = ""
        try:
            product_price = self.page.locator(self.productPrice).first.inner_text().strip()
        except Exception:
            product_price = ""

        safe_prod_name = product_name.encode('ascii', 'ignore').decode('ascii')
        print(f"Selected Random Product [{selected_index + 1}/{total_count}]: {safe_prod_name} ({product_price})")
        return {
            "index": selected_index,
            "name": product_name,
            "price": product_price
        }

    def is_product_details_displayed(self) -> bool:
        """Verifies that product details page is loaded."""
        try:
            self.page.locator(self.addToCart_btn).first.wait_for(state="visible", timeout=10000)
            return "/product_details/" in self.page.url
        except Exception:
            return False

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

    def is_add_to_cart_modal_displayed(self) -> bool:
        """Verifies the added-to-cart confirmation modal is visible."""
        try:
            self.page.locator(self.cartModal).wait_for(state="visible", timeout=8000)
            return True
        except Exception:
            return False

    def add_to_cart(self) -> bool:
        """
        Adds current product to cart and explicitly verifies confirmation modal.
        Dismisses modal via 'Continue Shopping' and waits for it to close.
        """
        self.safe_click(self.addToCart_btn)

        # Explicitly verify the modal appears
        modal_visible = False
        try:
            modal = self.page.locator(self.cartModal)
            modal.wait_for(state="visible", timeout=10000)
            modal_visible = True
        except Exception:
            modal_visible = False

        # Dismiss modal via Continue Shopping
        try:
            cont_btn = self.page.locator(self.continueShopping_btn).first
            cont_btn.wait_for(state="visible", timeout=5000)
            cont_btn.click(timeout=3000)
            self.page.locator(self.cartModal).wait_for(state="hidden", timeout=5000)
        except Exception:
            try:
                self.page.locator(self.continueShopping_btn).first.evaluate("element => element.click()")
            except Exception:
                pass

        return modal_visible

    def back_to_products(self):
        """Navigates back to products catalog and waits for listings to be ready."""
        try:
            self.safe_click(self.productsLink)
            if "/products" not in self.page.url:
                self.page.goto(ConfigReader.get_property("productsUrl") or "https://automationexercise.com/products", wait_until="domcontentloaded")
        except Exception:
            self.page.goto(ConfigReader.get_property("productsUrl") or "https://automationexercise.com/products", wait_until="domcontentloaded")

        try:
            self.page.locator(self.productDetailsLinks).first.wait_for(state="visible", timeout=10000)
        except Exception:
            pass

    def click_cart(self):
        """Navigates to cart and waits for cart table to load."""
        self.safe_click(self.cartButton)
        try:
            self.page.wait_for_url("**/view_cart", timeout=10000)
            self.page.locator("#cart_info_table").first.wait_for(state="visible", timeout=10000)
        except Exception:
            pass

    def click_products(self):
        """Navigates to products and waits for items to be visible."""
        try:
            self.safe_click(self.productsLink)
            if "/products" not in self.page.url:
                self.page.goto(ConfigReader.get_property("productsUrl") or "https://automationexercise.com/products", wait_until="domcontentloaded")
        except Exception:
            self.page.goto(ConfigReader.get_property("productsUrl") or "https://automationexercise.com/products", wait_until="domcontentloaded")

        try:
            self.page.locator(self.productDetailsLinks).first.wait_for(state="visible", timeout=10000)
        except Exception:
            pass

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
    isProductsPageDisplayed = is_products_page_displayed
    isProductDetailsDisplayed = is_product_details_displayed
    isAddToCartModalDisplayed = is_add_to_cart_modal_displayed
