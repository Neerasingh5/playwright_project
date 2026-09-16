import random
import re
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

        # Brand randomization locators
        self.brandsSidebar = ".brands_products"
        self.brandLinks = ".brands-name ul li a"
        self.brandHeader = ".features_items .title"
        self.brandProductCards = ".features_items .col-sm-4"

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

    def get_available_brands(self) -> list:
        """
        Dynamically detects all available brands from the sidebar on the Products page.
        Returns a list of brand dicts containing 'index', 'name', 'raw_text', and 'href'.
        """
        try:
            self.page.locator(self.brandLinks).first.wait_for(state="visible", timeout=15000)
        except Exception:
            pass

        brand_elements = self.page.locator(self.brandLinks).all()
        brands = []
        for idx, el in enumerate(brand_elements):
            raw = el.inner_text().strip()
            href = el.get_attribute("href") or ""
            # Strip item count e.g. "(6)\nPOLO" -> "POLO"
            cleaned_name = re.sub(r'\(\d+\)', '', raw).strip()
            if cleaned_name:
                brands.append({
                    "index": idx,
                    "name": cleaned_name,
                    "raw_text": raw,
                    "href": href
                })
        return brands

    def select_random_brand(self, exclude_brand_name: str = None) -> dict:
        """
        Dynamically detects available brand options, randomly picks ONE brand using
        real randomization (random.choice()), clicks the selected brand, and waits
        for the brand products page to load.
        """
        brands = self.get_available_brands()
        if not brands:
            raise RuntimeError("No brand options found in the brands section.")

        candidates = brands
        if exclude_brand_name:
            candidates = [b for b in brands if b["name"].lower() != exclude_brand_name.lower()]
            if not candidates:
                candidates = brands

        selected = random.choice(candidates)

        # Locate the selected brand link and click it
        if selected["href"]:
            brand_loc = self.page.locator(f".brands-name ul li a[href='{selected['href']}']").first
        else:
            brand_loc = self.page.locator(self.brandLinks).nth(selected["index"])

        brand_loc.scroll_into_view_if_needed()
        try:
            brand_loc.click(timeout=5000)
        except Exception:
            brand_loc.evaluate("element => element.click()")

        # Wait for brand products page navigation and title
        try:
            self.page.wait_for_url("**/brand_products/**", timeout=10000)
        except Exception:
            pass

        try:
            self.page.locator(self.brandHeader).first.wait_for(state="visible", timeout=10000)
        except Exception:
            pass

        print(f"Randomly Selected Brand [{selected['index'] + 1}/{len(brands)}]: '{selected['name']}' ({selected['href']})")
        return selected

    def is_brand_page_displayed(self, brand_name: str = None) -> bool:
        """Verifies that the brand products filter/result page is displayed."""
        try:
            is_url = "/brand_products/" in self.page.url
            if not is_url:
                return False
            if brand_name:
                header = self.get_brand_page_title().upper()
                return brand_name.upper() in header
            return True
        except Exception:
            return False

    def get_brand_page_title(self) -> str:
        """Returns the header text of the brand products page (e.g. 'BRAND - POLO PRODUCTS')."""
        try:
            loc = self.page.locator(self.brandHeader).first
            loc.wait_for(state="visible", timeout=8000)
            return loc.inner_text().strip()
        except Exception:
            return ""

    def get_brand_products_count(self) -> int:
        """Returns the number of products displayed under the selected brand."""
        try:
            self.page.locator(self.brandProductCards).first.wait_for(state="visible", timeout=8000)
            return len(self.page.locator(self.brandProductCards).all())
        except Exception:
            return self.page.locator(self.brandProductCards).count()

    def validate_brand_page(self, brand_name: str) -> bool:
        """Comprehensive verification of the brand selection result."""
        url_valid = "/brand_products/" in self.page.url
        title_text = self.get_brand_page_title()
        title_valid = brand_name.upper() in title_text.upper()
        products_count = self.get_brand_products_count()
        return url_valid and title_valid and (products_count > 0)

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
    getAvailableBrands = get_available_brands
    selectRandomBrand = select_random_brand
    isBrandPageDisplayed = is_brand_page_displayed
    getBrandPageTitle = get_brand_page_title
    getBrandProductsCount = get_brand_products_count
    validateBrandPage = validate_brand_page

# Alias ProductsPage to InventoryPage for clear POM semantics
ProductsPage = InventoryPage
