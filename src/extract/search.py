from dotenv import load_dotenv
import requests
import os

load_dotenv()


def search_and_extract_links(search_term, api_key, search_engine_id, num_results=10):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': search_term,
        'num': num_results
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    extracted_links = []
    if response.json().get('items'):
        for item in response.json()['items']:
            extracted_links.append(item['link'])

    return extracted_links


if __name__ == "__main__":
    search_term = "Energia solar"
    api_key = os.environ.get("API_KEY")
    search_engine_id = os.environ.get("SEARCH_ENGINE_ID")

    extracted_links = search_and_extract_links(search_term, api_key, search_engine_id, 3)
    print(extracted_links)