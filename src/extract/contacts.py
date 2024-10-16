import logging
import asyncio
from playwright.async_api import async_playwright
import re
from bs4 import BeautifulSoup

logging.basicConfig(filename="/tmp/extraction.log", level=logging.INFO)


async def process_link(link):
    logging.info(f"Processing {link}")
    try:
        async with async_playwright() as context_manager:
            browser = await context_manager.chromium.launch(headless=True)
            page = await browser.new_page()

            emails, phones = await extract_contacts_worker(link, page, timeout=20)
            logging.info(
                f"Found {len(emails)} emails and {len(phones)} phones for {link}"
            )

            await browser.close()

            return emails, phones
    except Exception as e:
        logging.error(f"Error extracting from {link}: {e}")
        return [], []


async def extract_contacts_worker(link, page, timeout):
    try:
        page.set_default_navigation_timeout(timeout * 1000)

        response = await page.goto(link)

        if response and response.status != 200:
            logging.info(f"Page not found: {link}")
            return [], []

        last_height = await page.evaluate("document.body.scrollHeight")
        scroll_pause_time = 1

        while True:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(scroll_pause_time)
            new_height = await page.evaluate("document.body.scrollHeight")

            if new_height == last_height:
                break
            last_height = new_height

        html_content = await page.content()
        soup = BeautifulSoup(html_content, "html.parser")
        text_content = soup.text

        email_pattern = re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
        )
        phone_pattern = re.compile(
            r"\+?(?:\d{2})?\s*(?:\d{2})?\s*\d?\s*[\d]{4}[\s-]*[\d]{4}"
        )

        emails = email_pattern.findall(text_content)
        phones = phone_pattern.findall(text_content)

        return list(set(emails)), list(set(phones))

    except Exception as e:
        logging.info(f"Error during extracting from {link}: {e}")
        return [], []
