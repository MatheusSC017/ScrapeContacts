import os
from extract.search import search_and_extract_links
from extract.contacts import process_link
from transform.links import get_base_links

search_term = "Energia solar"
api_key = os.environ.get("API_KEY")
search_engine_id = os.environ.get("SEARCH_ENGINE_ID")

extracted_links = search_and_extract_links(search_term, api_key, search_engine_id, 10)
base_links = get_base_links(extracted_links)

with open('contacts.txt', 'w') as file:
    for link in base_links:
        emails, phones = process_link(link)
        file.write(f"{link},{emails},{phones}\n")
