import os
from datetime import datetime
from playwright.sync_api import Page

class ScreenshotHelper:
    # Automatically increments screenshot number
    screenshot_count = 1

    @classmethod
    def capture_screenshot(cls, page: Page, step: str) -> str:
        # Create screenshots folder if it doesn't exist
        folder = "screenshots"
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        # Timestamp format matching Java SimpleDateFormat("yyyyMMdd_HHmmss")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Destination filename
        filename = f"{cls.screenshot_count}_{step}_{timestamp}.png"
        cls.screenshot_count += 1
        dest = os.path.join(folder, filename)

        # Capture screenshot
        try:
            page.screenshot(path=dest, full_page=False)
            print(f"Screenshot Saved : {os.path.abspath(dest)}")
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")

        return dest

    # Alias for exact Java compatibility
    captureScreenshot = capture_screenshot
