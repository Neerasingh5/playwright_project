from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, Playwright
from utility.config_reader import ConfigReader

class Helper:
    _playwright: Playwright = None
    _browser: Browser = None
    _context: BrowserContext = None
    _page: Page = None

    @classmethod
    def start_browser(cls, browser: str = None) -> Page:
        if browser is None:
            browser = ConfigReader.get_property("browser") or "Edge"

        browser_clean = browser.strip().lower()
        cls._playwright = sync_playwright().start()

        launch_args = ["--start-maximized"]

        if browser_clean in ["chrome", "gc", "google chrome"]:
            try:
                cls._browser = cls._playwright.chromium.launch(
                    channel="chrome",
                    headless=False,
                    args=launch_args
                )
            except Exception:
                cls._browser = cls._playwright.chromium.launch(
                    headless=False,
                    args=launch_args
                )

        elif browser_clean in ["edge", "eg", "microsoft edge"]:
            try:
                cls._browser = cls._playwright.chromium.launch(
                    channel="msedge",
                    headless=False,
                    args=launch_args
                )
            except Exception:
                cls._browser = cls._playwright.chromium.launch(
                    headless=False,
                    args=launch_args
                )

        elif browser_clean in ["firefox", "mf", "mozilla firefox"]:
            cls._browser = cls._playwright.firefox.launch(headless=False)

        else:
            print("Sorry! Unsupported Browser, launching default Chromium.")
            cls._browser = cls._playwright.chromium.launch(
                headless=False,
                args=launch_args
            )

        cls._context = cls._browser.new_context(no_viewport=True)

        # Block intrusive ads/vignettes that intercept clicks on Automation Exercise
        def _block_ads(route):
            ad_keywords = [
                "googlesyndication",
                "googleads",
                "doubleclick",
                "adservice.google",
                "pagead2",
                "adnxs",
            ]
            if any(ad in route.request.url for ad in ad_keywords):
                route.abort()
            else:
                route.continue_()

        cls._context.route("**/*", _block_ads)

        cls._page = cls._context.new_page()

        url = ConfigReader.get_property("url")
        if url:
            cls._page.goto(url, wait_until="domcontentloaded")

        return cls._page

    @classmethod
    def close_browser(cls, driver: Page = None):
        try:
            if cls._context:
                cls._context.close()
            if cls._browser:
                cls._browser.close()
            if cls._playwright:
                cls._playwright.stop()
        except Exception as e:
            print(f"Error closing browser: {e}")
        finally:
            cls._page = None
            cls._context = None
            cls._browser = None
            cls._playwright = None

    # Aliases for exact Java compatibility
    startBrowser = start_browser
    closeBrowser = close_browser
