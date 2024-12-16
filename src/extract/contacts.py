import asyncio
import json
import logging
import os
import re

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

if os.path.exists(".env"):
    load_dotenv(".env")
logging.basicConfig(filename="extraction.log", level=logging.INFO)

DEFAULT_SCROLL_PAUSE = 1
DEFAULT_TIMEOUT = 20
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
PHONE_PATTERN = re.compile(r"\+?(?:\d{2})?\s*(?:\d{2})?\s*\d?\s*[\d]{4}[\s-]*[\d]{4}")


async def process_link(link):
    if not validate_link(link):
        return [], []

    logging.info(f"Processing {link}")

    openai_api_key = os.environ.get("OPENAI_KEY")
    if not openai_api_key:
        logging.error("OPENAI_KEY environment variable not set.")
        return
    openai_client = OpenAI(api_key=openai_api_key)

    try:
        html_content = await extract_page_content(link, DEFAULT_TIMEOUT)
        if not html_content:
            logging.warning(f"No content extracted from {link}")
            return [], []

        emails, phones = await extract_contacts_worker(html_content, openai_client)
        logging.info(f"Found {len(emails)} emails and {len(phones)} phones for {link}")
        return emails, phones
    except (PlaywrightTimeoutError, OpenAIError) as e:
        logging.error(f"Error processing {link}: {e}")
        return [], []


def validate_link(link):
    if not link.startswith(("http://", "https://")):
        logging.error(f"Invalid link format: {link}")
        return False
    return True


async def extract_page_content(link, timeout):
    async with async_playwright() as context_manager:
        browser = await context_manager.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            page.set_default_navigation_timeout(timeout * 1000)
            response = await page.goto(link)

            if response and response.status != 200:
                logging.warning(f"Page returned non-200 status: {response.status}")
                return None

            await scroll_to_bottom(page, DEFAULT_SCROLL_PAUSE)
            return await page.content()
        finally:
            await browser.close()


async def scroll_to_bottom(page, scroll_pause_time):
    last_height = await page.evaluate("document.body.scrollHeight")
    while True:
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(scroll_pause_time)
        new_height = await page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


async def extract_contacts_worker(html_content, openai_client):
    soup = BeautifulSoup(html_content, "html.parser")
    text_content = soup.get_text()

    emails = refine_with_openai(EMAIL_PATTERN, text_content, "emails", openai_client)
    phones = refine_with_openai(PHONE_PATTERN, text_content, "phones", openai_client)

    return emails, phones


def refine_with_openai(pattern, text, contact_type, openai_client):
    matches = parse_contacts(pattern, text)
    refined_matches = []
    for match in matches:
        context = extract_context(text, match)
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"Identify {contact_type} in the following context and return in JSON format.",
                    },
                    {"role": "user", "content": context},
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )

            response = json.loads(response.model_dump_json())["choices"][0]["message"][
                "content"
            ]
            refined_matches.extend(list(json.loads(response).values())[0])
        except OpenAIError as e:
            logging.warning(f"OpenAI error while refining {contact_type}: {e}")

    return list(set(refined_matches))


def parse_contacts(pattern, text):
    return pattern.finditer(text)


def extract_context(text, match):
    start, end = match.start(), match.end()
    context_start = max(0, start - 100)
    context_end = min(len(text), end + 100)
    return text[context_start:context_end]
