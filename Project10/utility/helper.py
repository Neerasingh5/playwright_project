from playwright.sync_api import sync_playwright, Page
from utility.config_reader import ConfigReader


class Helper:
    """
    Simple browser launch/close utility.
    Each test calls start_browser() and close_browser() independently.
    """

    @classmethod
    def start_browser(cls, browser: str = None) -> Page:
        if browser is None:
            browser = ConfigReader.get_property("browser") or "Edge"

        browser_clean = browser.strip().lower()
        pw = sync_playwright().start()

        launch_args = ["--start-maximized"]

        if browser_clean in ["chrome", "gc", "google chrome"]:
            try:
                b = pw.chromium.launch(channel="chrome", headless=False, args=launch_args)
            except Exception:
                b = pw.chromium.launch(headless=False, args=launch_args)

        elif browser_clean in ["edge", "eg", "microsoft edge"]:
            try:
                b = pw.chromium.launch(channel="msedge", headless=False, args=launch_args)
            except Exception:
                b = pw.chromium.launch(headless=False, args=launch_args)

        elif browser_clean in ["firefox", "mf", "mozilla firefox"]:
            b = pw.firefox.launch(headless=False)

        else:
            print("Unsupported browser — launching default Chromium.")
            b = pw.chromium.launch(headless=False, args=launch_args)

        ctx = b.new_context(no_viewport=True)

        # Block ads that intercept clicks on Automation Exercise
        def block_ads(route):
            ad_domains = ["googlesyndication", "googleads", "doubleclick",
                          "adservice.google", "pagead2", "adnxs"]
            if any(ad in route.request.url for ad in ad_domains):
                route.abort()
            else:
                route.continue_()

        ctx.route("**/*", block_ads)

        page = ctx.new_page()

        url = ConfigReader.get_property("url")
        if url:
            page.goto(url, wait_until="domcontentloaded")

        # Store on page object so close_browser can clean up
        page._pw  = pw
        page._b   = b
        page._ctx = ctx

        return page

    @classmethod
    def close_browser(cls, driver: Page = None):
        try:
            if driver:
                ctx = getattr(driver, "_ctx", None)
                b   = getattr(driver, "_b",   None)
                pw  = getattr(driver, "_pw",  None)
                if ctx: ctx.close()
                if b:   b.close()
                if pw:  pw.stop()
        except Exception as e:
            print(f"Error closing browser: {e}")

    # Aliases
    startBrowser = start_browser
    closeBrowser = close_browser
