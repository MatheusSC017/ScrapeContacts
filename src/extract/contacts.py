import asyncio
import json
import logging
import os
import re

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from playwright.async_api import async_playwright

if os.path.exists("../.env"):
    load_dotenv("../.env")
logging.basicConfig(filename="/tmp/extraction.log", level=logging.INFO)


async def process_link(link):
    logging.info(f"Processing {link}")
    try:
        openai_client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))

        async with async_playwright() as context_manager:
            browser = await context_manager.chromium.launch(headless=True)
            page = await browser.new_page()

            emails, phones = await extract_contacts_worker(
                link, page, openai_client, timeout=20
            )
            logging.info(
                f"Found {len(emails)} emails and {len(phones)} phones for {link}"
            )

            await browser.close()

            return emails, phones
    except Exception as e:
        logging.error(f"Error extracting from {link}: {e}")
        return [], []
    except OpenAIError as e:
        logging.info(f"Error during extracting using OpenAI: {e}")


async def extract_contacts_worker(link, page, openai_client, timeout):
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

        emails = extract_from_context(
            email_pattern, text_content, "e-mails", openai_client
        )
        phones = extract_from_context(
            phone_pattern, text_content, "phones", openai_client
        )

        unique_emails = list(set([email for email in emails]))
        unique_phones = list(set([phone for phone in phones]))

        return unique_emails, unique_phones

    except Exception as e:
        logging.info(f"Error during extracting from {link}: {e}")
        return [], []


def extract_from_context(pattern, text, contact_type, openai_client):
    matches = []
    for match in pattern.finditer(text):
        start, end = match.start(), match.end()
        context_start = max(0, start - 100)
        context_end = min(len(text), end + 100)

        search_messages = [
            {
                "role": "system",
                "content": f"You're an assistant that will help to find {contact_type} in the text and return in json format",
            },
            {"role": "user", "content": text[context_start:context_end]},
        ]
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=search_messages,
            temperature=0,
            response_format={"type": "json_object"},
        )
        response = json.loads(response.model_dump_json())["choices"][0]["message"][
            "content"
        ]
        matches.extend(list(json.loads(response).values())[0])

    return matches
