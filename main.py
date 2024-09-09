import os
from selenium import webdriver
from extract.search import search_and_extract_links
from extract.contacts import extract_contacts_with_timeout
from transform.links import get_base_links

search_term = "Energia solar"
api_key = os.environ.get("API_KEY")
search_engine_id = os.environ.get("SEARCH_ENGINE_ID")

extracted_links = search_and_extract_links(search_term, api_key, search_engine_id, 10)
base_links = get_base_links(extracted_links)

driver = webdriver.Firefox()

with open('contacts.txt', 'w') as file:
    for link in base_links:
        emails, phones = extract_contacts_with_timeout(link, driver, timeout=15)

        file.write(f"{link},{emails},{phones}\n")

driver.quit()
