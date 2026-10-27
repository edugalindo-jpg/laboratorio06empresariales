"""Capture authenticated screenshots of the Django admin.

Usage (with the development server running)::

    python scripts/capture_admin.py

Credentials can be overridden with ADMIN_USER and ADMIN_PASSWORD.
"""

import base64
import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "http://127.0.0.1:8000"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "capturas"
USER = os.environ.get("ADMIN_USER", "admin")
PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin12345!")


def full_page_screenshot(driver, destination):
    metrics = driver.execute_cdp_cmd("Page.getLayoutMetrics", {})
    size = metrics["cssContentSize"]
    width = max(int(size["width"]), 1200)
    height = max(int(size["height"]), 800)
    data = driver.execute_cdp_cmd(
        "Page.captureScreenshot",
        {
            "format": "png",
            "captureBeyondViewport": True,
            "fromSurface": True,
            "clip": {
                "x": 0,
                "y": 0,
                "width": width,
                "height": height,
                "scale": 1,
            },
        },
    )
    destination.write_bytes(base64.b64decode(data["data"]))


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--window-size=1600,1200")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(f"{BASE_URL}/admin/login/?next=/admin/")
        driver.find_element(By.ID, "id_username").send_keys(USER)
        driver.find_element(By.ID, "id_password").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
        WebDriverWait(driver, 15).until(
            lambda browser: "/admin/login/" not in browser.current_url
        )

        pages = [
            ("news/article/", "05_admin_articulos.png"),
            ("news/category/", "06_admin_categorias.png"),
            ("news/author/", "07_admin_autores.png"),
        ]
        for route, filename in pages:
            driver.get(f"{BASE_URL}/admin/{route}")
            WebDriverWait(driver, 15).until(
                lambda browser: browser.find_elements(By.ID, "result_list")
            )
            full_page_screenshot(driver, OUTPUT_DIR / filename)
            print(f"Saved {filename}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
