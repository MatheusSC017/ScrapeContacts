import os
from selenium import webdriver
from extract.search import search_and_extract_links
from extract.contacts import extract_contacts_with_timeout
from transform.links import get_base_links

search_term = "Empresas de Software"
api_key = os.environ.get("API_KEY")
search_engine_id = os.environ.get("SEARCH_ENGINE_ID")

# extracted_links = search_and_extract_links(search_term, api_key, search_engine_id, 5)
# base_links = get_base_links(extracted_links)

driver = webdriver.Firefox()

for link in ['https://portal.fazenda.sp.gov.br/', 'https://abes.com.br/', 'https://www.econodata.com.br/']:
    emails, phones = extract_contacts_with_timeout(link, driver, timeout=15)

    print(link)

    print("Emails found:")
    for email in emails:
        print(f'Email: {email}')

    print("\nPhone numbers found:")
    for phone in phones:
        print(f'Phone: {phone}')

driver.quit()


