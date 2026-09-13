import random

class RandomHelper:
    """Reusable utility for safe and realistic test data randomization."""

    CUSTOMER_FIRST_NAMES = [
        "Neeraj", "Aarav", "Rohan", "Priya", "Vikram",
        "Ananya", "Rahul", "Neha", "Siddharth", "Pooja"
    ]

    CUSTOMER_LAST_NAMES = [
        "Singh", "Sharma", "Verma", "Singh", "Patel",
        "Gupta", "Mehta", "Chopra", "Kumar", "Joshi"
    ]

    DELIVERY_COMMENTS = [
        "Please leave the package at the front door.",
        "Ring the doorbell upon delivery.",
        "Preferred delivery time is between 2:00 PM and 5:00 PM.",
        "Please call on arrival before delivering.",
        "Fragile contents - please handle with extra care.",
        "Please leave with the security guard if not available.",
        "Gift package, please do not include price tag inside."
    ]

    @classmethod
    def get_random_quantity(cls, min_qty: int = 1, max_qty: int = 3) -> int:
        """Returns a random product quantity."""
        return random.randint(min_qty, max_qty)

    @classmethod
    def pick_random_index(cls, total_count: int, exclude_indices: list = None) -> int:
        """
        Picks a random index from 0 to total_count - 1.
        Optionally excludes specific indices (e.g. to ensure picking a different product).
        """
        if total_count <= 0:
            return 0
        if exclude_indices is None:
            exclude_indices = []

        available_indices = [i for i in range(total_count) if i not in exclude_indices]
        if not available_indices:
            # If all are excluded, fallback to any random index
            return random.randint(0, total_count - 1)

        return random.choice(available_indices)

    @classmethod
    def get_random_customer(cls) -> dict:
        """Generates realistic customer details."""
        fname = random.choice(cls.CUSTOMER_FIRST_NAMES)
        lname = random.choice(cls.CUSTOMER_LAST_NAMES)
        zip_code = f"{random.randint(110001, 600099)}"
        return {
            "first_name": fname,
            "last_name": lname,
            "zip_code": zip_code
        }

    @classmethod
    def get_random_order_comment(cls, fname: str = None, lname: str = None, zip_code: str = None) -> str:
        """Generates a realistic order comment with delivery instructions."""
        instruction = random.choice(cls.DELIVERY_COMMENTS)
        if fname and lname and zip_code:
            return f"Order for {fname} {lname} ({zip_code}) - {instruction}"
        return instruction

    @classmethod
    def get_random_card_details(cls, customer_name: str = None) -> dict:
        """Generates realistic card payment details with future expiry and valid format."""
        if not customer_name:
            customer_name = f"{random.choice(cls.CUSTOMER_FIRST_NAMES)} {random.choice(cls.CUSTOMER_LAST_NAMES)}"

        # 16-digit test card number (standard mock card prefix)
        card_num_suffix = f"{random.randint(100000000000, 999999999999)}"
        card_number = f"4111{card_num_suffix}"
        cvc = f"{random.randint(100, 999)}"
        expiry_month = f"{random.randint(1, 12):02d}"
        expiry_year = f"{random.randint(2028, 2035)}"

        return {
            "name": customer_name,
            "number": card_number,
            "cvc": cvc,
            "expiry_month": expiry_month,
            "expiry_year": expiry_year
        }
