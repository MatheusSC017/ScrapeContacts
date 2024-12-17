import os

import requests

GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"


def search_and_extract_links(search_term, api_key, search_engine_id, num_results=10):
    response = requests.get(
        GOOGLE_SEARCH_URL,
        params={
            "key": api_key,
            "cx": search_engine_id,
            "q": search_term,
            "num": num_results,
        },
    )

    if response.status_code == 200:
        extracted_links = [
            item["link"]
            for item in response.json().get("items", [])
            if item.get("link") is not None
        ]
        return extracted_links
    else:
        raise requests.RequestException(
            {
                "error": f"Page returned non-200 status: {response.status_code}, response: {response.content}"
            }
        )


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    search_term = "Energia solar"
    api_key = os.environ.get("API_KEY")
    search_engine_id = os.environ.get("SEARCH_ENGINE_ID")

    try:
        print(search_and_extract_links(search_term, api_key, search_engine_id, 3))
    except Exception as e:
        print(e)
