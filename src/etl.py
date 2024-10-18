"""
Method and script to run the complete ETL, through a call or command line
"""

import sys
import os
import csv
import argparse
import logging
import asyncio
from dotenv import load_dotenv
from src.extract.search import search_and_extract_links
from src.extract.contacts import process_link
from src.transform.links import get_base_links
from src.load.save import save_csv

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
    except Exception as e:
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ScrapContacts",
        description="Scrap contacts info from page of a specific category",
    )
    parser.add_argument(
        "search_term", type=str, help="Term used during the search for the links"
    )
    parser.add_argument(
        "-o", "--output", type=str, help="Output CSV file name", default="contacts.csv"
    )
    parser.add_argument(
        "-n", "--number", type=int, help="Number of results expected", default=10
    )
    parser.add_argument(
        "-e",
        "--exclude",
        metavar="S",
        type=str,
        nargs="+",
        help="List of sites to exclude from search",
        default=[],
    )

    args = parser.parse_args()

    asyncio.run(etl_contacts(args.search_term, args.output, args.number, args.exclude))
