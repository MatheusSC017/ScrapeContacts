import re
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from multiprocessing import Process, Queue


def extract_contacts_worker(link, driver, queue):
    try:
        driver.set_page_load_timeout(10)  # Set page load timeout to 10 seconds
        driver.get(link)

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        text_content = soup.text

        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
        phone_pattern = re.compile(r'\+?(?:\d{2})?\s*(?:\d{2})?\s*\d?\s*[\d]{4}[\s-]*[\d]{4}')

        emails = email_pattern.findall(text_content)
        phones = phone_pattern.findall(text_content)

        queue.put((emails, phones))

    except TimeoutException:
        print(f"Timeout while loading {link}")
        queue.put(([], []))
    except Exception as e:
        print(f"Error: {e}")
        queue.put(([], []))


def extract_contacts_with_timeout(link, driver, timeout=15):
    queue = Queue()
    process = Process(target=extract_contacts_worker, args=(link, driver, queue))

    process.start()
    process.join(timeout=timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        print(f"Timeout while extracting contacts from {link}")
        return [], []

    return queue.get()
