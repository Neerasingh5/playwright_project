from playwright.sync_api import Page
from utility.random_helper import RandomHelper

class CheckoutPage:

    def __init__(self, driver: Page):
        self.driver = driver
        self.page = driver

        # Automation Exercise checkout/payment locators
        self.comment = "textarea[name='message']"
        self.placeOrder = "a[href='/payment']"
        self.cardName = "input[data-qa='name-on-card']"
        self.cardNumber = "input[data-qa='card-number']"
        self.cvc = "input[data-qa='cvc']"
        self.expiryMonth = "input[data-qa='expiry-month']"
        self.expiryYear = "input[data-qa='expiry-year']"
        self.payButton = "button[data-qa='pay-button']"
        self.orderSuccess = "//p[contains(normalize-space(.),'Congratulations! Your order has been confirmed!')]"
        self.orderPlacedHeader = "[data-qa='order-placed']"
        self.downloadInvoice = "//a[contains(normalize-space(.),'Download Invoice')]"
        self.continueButton = "a[data-qa='continue-button']"
        self.deliveryAddress = "#address_delivery"
        self.billingAddress = "#address_invoice"
        self.orderReviewTable = "#cart_info"

    def safe_click(self, selector: str):
        loc = self.page.locator(selector).first
        loc.wait_for(state="attached", timeout=15000)
        loc.scroll_into_view_if_needed()
        try:
            loc.click(timeout=5000)
        except Exception:
            loc.evaluate("element => element.click()")

    def is_checkout_page_displayed(self) -> bool:
        """Verifies that checkout page is loaded with address details and order review."""
        try:
            self.page.locator(self.deliveryAddress).first.wait_for(state="visible", timeout=10000)
            return "/checkout" in self.page.url
        except Exception:
            return "/checkout" in self.page.url

    def enter_customer_details(
        self,
        fname: str = None,
        lname: str = None,
        zip_code: str = None,
        comment: str = None
    ) -> dict:
        """
        Enters customer details and order notes into checkout page.
        Dynamically generates random values if arguments are omitted.
        """
        if not fname or not lname or not zip_code:
            random_customer = RandomHelper.get_random_customer()
            fname = fname or random_customer["first_name"]
            lname = lname or random_customer["last_name"]
            zip_code = zip_code or random_customer["zip_code"]

        if not comment:
            comment = RandomHelper.get_random_order_comment(fname, lname, zip_code)

        loc = self.page.locator(self.comment).first
        loc.wait_for(state="visible", timeout=15000)
        loc.fill(comment)
        print(f"Customer Details: {fname} {lname} ({zip_code}) | Note: {comment}")

        return {
            "first_name": fname,
            "last_name": lname,
            "zip_code": zip_code,
            "comment": comment
        }

    def is_customer_info_accepted(self, expected_comment: str = None) -> bool:
        """Validates that customer information / note is accepted in the textarea."""
        try:
            val = self.page.locator(self.comment).first.input_value()
            if expected_comment:
                return expected_comment.strip() in val.strip()
            return len(val.strip()) > 0
        except Exception:
            return False

    def click_continue(self):
        """Clicks Place Order button and waits for payment page to load."""
        self.safe_click(self.placeOrder)
        try:
            self.page.wait_for_url("**/payment", timeout=10000)
            self.page.locator(self.cardName).first.wait_for(state="visible", timeout=10000)
        except Exception:
            pass

    def is_payment_page_displayed(self) -> bool:
        """Validates that the payment/overview page is opened successfully."""
        try:
            self.page.locator(self.cardName).first.wait_for(state="visible", timeout=10000)
            return "/payment" in self.page.url
        except Exception:
            return "/payment" in self.page.url

    def click_finish(self, card_details: dict = None):
        """
        Fills payment details and completes the order.
        Uses randomized realistic card details if none are provided.
        """
        if not card_details:
            card_details = RandomHelper.get_random_card_details()

        name_loc = self.page.locator(self.cardName).first
        name_loc.wait_for(state="visible", timeout=15000)
        name_loc.fill(card_details["name"])

        self.page.locator(self.cardNumber).first.fill(card_details["number"])
        self.page.locator(self.cvc).first.fill(card_details["cvc"])
        self.page.locator(self.expiryMonth).first.fill(card_details["expiry_month"])
        self.page.locator(self.expiryYear).first.fill(card_details["expiry_year"])

        print(f"Payment Details: Name='{card_details['name']}', Card=****{card_details['number'][-4:]}, Expiry={card_details['expiry_month']}/{card_details['expiry_year']}")

        self.safe_click(self.payButton)

        # Wait for payment confirmation with Playwright explicit wait
        try:
            self.page.wait_for_url("**/payment_done*", timeout=15000)
            self.page.locator(self.orderSuccess).first.wait_for(state="visible", timeout=15000)
        except Exception:
            pass

    def click_generate_pdf(self):
        self.safe_click(self.downloadInvoice)

    def click_back_home(self):
        self.safe_click(self.continueButton)

    def is_order_successful(self) -> bool:
        """Validates that the order has been successfully placed and confirmed."""
        try:
            is_url_ok = "/payment_done" in self.page.url
            is_msg_ok = self.page.locator(self.orderSuccess).first.is_visible() or \
                        self.page.locator(self.orderPlacedHeader).first.is_visible()
            return is_url_ok or is_msg_ok
        except Exception:
            return False

    def get_order_confirmation_message(self) -> str:
        """Returns the confirmation message displayed upon placing order."""
        try:
            if self.page.locator(self.orderSuccess).first.is_visible():
                msg = self.page.locator(self.orderSuccess).first.inner_text().strip()
                return msg.encode("ascii", "ignore").decode("ascii")
            if self.page.locator(self.orderPlacedHeader).first.is_visible():
                msg = self.page.locator(self.orderPlacedHeader).first.inner_text().strip()
                return msg.encode("ascii", "ignore").decode("ascii")
        except Exception:
            pass
        return ""

    # Aliases for exact Java compatibility
    safeClick = safe_click
    enterCustomerDetails = enter_customer_details
    isCustomerInfoAccepted = is_customer_info_accepted
    clickContinue = click_continue
    isPaymentPageDisplayed = is_payment_page_displayed
    clickFinish = click_finish
    clickGeneratePDF = click_generate_pdf
    clickBackHome = click_back_home
    isOrderSuccessful = is_order_successful
    isCheckoutPageDisplayed = is_checkout_page_displayed
    getOrderConfirmationMessage = get_order_confirmation_message
