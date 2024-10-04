import re
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from multiprocessing import Process, Queue

logging.basicConfig(filename='extraction.log', level=logging.INFO)


def process_link(link):
    logging.info(f"Processing {link}")
    driver = webdriver.Firefox()
    try:
        emails, phones = extract_contacts_with_timeout(link, driver, timeout=20)
        logging.info(f"Found {len(emails)} emails and {len(phones)} phones for {link}")
        return emails, phones
    except Exception as e:
        logging.error(f"Error extracting from {link}: {e}")
        return [], []
    finally:
        driver.quit()


def extract_contacts_with_timeout(link, driver, timeout=20):
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


def extract_contacts_worker(link, driver, queue):
    try:
        driver.set_page_load_timeout(20)
        driver.get(link)

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_pause_time = 2

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break
            last_height = new_height

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        text_content = soup.text

        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
        phone_pattern = re.compile(r'\+?(?:\d{2})?\s*(?:\d{2})?\s*\d?\s*[\d]{4}[\s-]*[\d]{4}')

        emails = email_pattern.findall(text_content)
        phones = phone_pattern.findall(text_content)

        queue.put((list(set(emails)), list(set(phones))))

    except TimeoutException:
        print(f"Timeout while loading {link}")
        queue.put(([], []))
    except Exception as e:
        print(f"Error: {e}")
        queue.put(([], []))
