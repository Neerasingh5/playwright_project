# Automation Exercise - Playwright Python POM Project

This project is a 1-to-1 conversion of the Selenium Java (TestNG) Page Object Model (POM) project to **Playwright with Python**.

The project structure, method names, locators, and test flows are kept identical to the original Selenium project for simplicity and ease of maintenance.

---

## 📁 Project Structure

```
Automation_Testing_POM/
├── config.properties                              # Configuration (browser, URLs, credentials)
├── requirements.txt                               # Python dependencies
├── pytest.ini                                     # PyTest configuration
├── run_tests.py                                   # Quick test runner script
├── CSVFiles/
│   └── AutomationExercise_Valid_Login_Users.csv   # Data-driven test data
├── pages/
│   ├── __init__.py
│   ├── login_page.py                              # LoginPage POM
│   ├── inventory_page.py                          # InventoryPage POM
│   ├── cart_page.py                               # CartPage POM
│   └── checkout_page.py                           # CheckoutPage POM
├── utility/
│   ├── __init__.py
│   ├── config_reader.py                           # Reads config.properties
│   ├── csv_helper.py                              # Reads CSV row by row
│   ├── helper.py                                  # Launches / closes browser (Edge, Chrome, Firefox)
│   ├── random_helper.py                           # Generates dynamic products, quantities, notes & card details
│   └── screenshot_helper.py                       # Captures timestamped screenshots
├── test_cases/
│   ├── __init__.py
│   ├── test_csv_login.py                          # Data-Driven Login Test (DDTLoginTest)
│   └── test_product_purchase.py                   # End-to-end purchase flow test
└── screenshots/                                   # Auto-created directory for test screenshots
```

---

## 🚀 Setup Instructions

### 1. Install Dependencies
Make sure you have Python 3.8+ installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Install Playwright Browsers (if not already installed)
```bash
python -m playwright install
```

---

## 🧪 Running Tests

### Option 1: Run with the test runner script
```bash
python run_tests.py
```

### Option 2: Run with PyTest
Run all tests:
```bash
pytest
```

Run only CSV Login test:
```bash
pytest test_cases/test_csv_login.py -s
```

Run only Product Purchase test:
```bash
pytest test_cases/test_product_purchase.py -s
```

### Option 3: Run directly with Python
```bash
python test_cases/test_csv_login.py
python test_cases/test_product_purchase.py
```

---

## ⚙️ Configuration (`config.properties`)

You can modify settings directly in `config.properties`:
```properties
browser=Edge
url=https://automationexercise.com/
loginUrl=https://automationexercise.com/login
productsUrl=https://automationexercise.com/products
username=neerajsingh41150@gmail.com
password=Neeraj@123
```

Supported `browser` values:
- `Edge`, `Microsoft Edge`, `EG`
- `Chrome`, `Google Chrome`, `GC`
- `Firefox`, `Mozilla Firefox`, `MF`
- `Chromium`
