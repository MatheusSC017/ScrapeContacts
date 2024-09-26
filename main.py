import os
import csv
import argparse
import logging
from extract.search import search_and_extract_links
from extract.contacts import process_link
from transform.links import get_base_links


logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(
    prog="ScrapContacts",
    description="Scrap contacts info from page of a specific category"
)
parser.add_argument("search_term", type=str, help="Term used during the search for the links")
parser.add_argument("-o", "--output", type=str, help="Output CSV file name", default="contacts.csv")
parser.add_argument("-n", "--number", type=int, help="Number of results expected", default=10)
parser.add_argument("-e", "--exclude", metavar='S', type=str, nargs='+',
                    help="List of sites to exclude from search", default=[])

args = parser.parse_args()

api_key = os.environ.get("API_KEY")
search_engine_id = os.environ.get("SEARCH_ENGINE_ID")

try:
    extracted_links = search_and_extract_links(args.search_term, api_key, search_engine_id, args.number)
except Exception as e:
    logging.error(f"Error extracting links: {e}")
    exit(1)

base_links = get_base_links(extracted_links)

with open(args.output, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Link', 'Emails', 'Phones'])
    for link in base_links:
        if link not in args.exclude:
            try:
                emails, phones = process_link(link)
                writer.writerow([link, emails, phones])
            except Exception as e:
                logging.error(f"Error processing link {link}: {e}")