import csv
import logging
import os
import sys

from dotenv import load_dotenv

from src.extract.contacts import process_link
from src.extract.search import search_and_extract_links
from src.load.save import save_csv
from src.transform.links import get_base_links

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if os.path.exists(".env"):
    load_dotenv()
logging.basicConfig(filename="/tmp/extraction.log", level=logging.INFO)


async def etl_contacts(search_term, output_path, number_searches, exclude_links):
    api_key = os.environ.get("API_KEY")
    search_engine_id = os.environ.get("SEARCH_ENGINE_ID")

    try:
        extracted_links = search_and_extract_links(
            search_term, api_key, search_engine_id, number_searches
        )

        if "error" in extracted_links:
            raise Exception(extracted_links)
    except Exception as e:
        print("Error extracting links: %s", e)
        logging.error("Error extracting links: %s", e)
        exit(1)

    base_links = get_base_links(extracted_links)

    extracted_contacts = []
    for link in base_links:
        if link not in exclude_links:
            try:
                emails, phones = await process_link(link)
                extracted_contacts.append([link, emails, phones])
            except Exception as e:
                logging.error("Error processing link  %s: %s", link, e)

    # save_csv(extracted_contacts, output_path)

    return extracted_contacts


def read_cache(cached_filename):
    if os.path.isfile(f"cache/{cached_filename}.csv"):
        with open(
            f"cache/{cached_filename}.csv", "r", newline="", encoding="utf-8"
        ) as csvfile:
            contacts = csv.reader(csvfile, delimiter=" ", quotechar="|")
            return list(contacts)
    else:
        return []
