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
        self.orderSuccess = "//*[contains(normalize-space(.),'Congratulations! Your order has been confirmed!')]"
        self.downloadInvoice = "//a[contains(normalize-space(.),'Download Invoice')]"
        self.continueButton = "a[data-qa='continue-button']"

    def safe_click(self, selector: str):
        loc = self.page.locator(selector).first
        loc.wait_for(state="attached", timeout=15000)
        loc.scroll_into_view_if_needed()
        try:
            loc.click(timeout=5000)
        except Exception:
            loc.evaluate("element => element.click()")

    def enter_customer_details(
        self,
        fname: str = None,
        lname: str = None,
        zip_code: str = None,
        comment: str = None
    ) -> dict:
        """
        Enters customer details and order notes.
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

    def click_continue(self):
        self.safe_click(self.placeOrder)

    def click_finish(self, card_details: dict = None):
        """
        Fills payment details and places the order.
        Uses randomized realistic card details if none are provided.
        """
        if not card_details:
            card_details = RandomHelper.get_random_card_details()

        self.page.locator(self.cardName).first.wait_for(state="visible", timeout=15000)
        self.page.locator(self.cardName).first.fill(card_details["name"])
        self.page.locator(self.cardNumber).first.fill(card_details["number"])
        self.page.locator(self.cvc).first.fill(card_details["cvc"])
        self.page.locator(self.expiryMonth).first.fill(card_details["expiry_month"])
        self.page.locator(self.expiryYear).first.fill(card_details["expiry_year"])

        print(f"Payment Details: Name='{card_details['name']}', Card=****{card_details['number'][-4:]}, Expiry={card_details['expiry_month']}/{card_details['expiry_year']}")

        self.safe_click(self.payButton)
        self.page.locator(self.orderSuccess).first.wait_for(state="visible", timeout=15000)

    def click_generate_pdf(self):
        self.safe_click(self.downloadInvoice)

    def click_back_home(self):
        self.safe_click(self.continueButton)

    def is_order_successful(self) -> bool:
        try:
            return self.page.locator(self.orderSuccess).first.is_visible()
        except Exception:
            return False

    # Aliases for exact Java compatibility
    safeClick = safe_click
    enterCustomerDetails = enter_customer_details
    clickContinue = click_continue
    clickFinish = click_finish
    clickGeneratePDF = click_generate_pdf
    clickBackHome = click_back_home
    isOrderSuccessful = is_order_successful
