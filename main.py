links = [
    'https://abes.com.br/',
    'https://aws.amazon.com/pt/isv/',
    'https://www.econodata.com.br/maiores-empresas/todo-brasil/software-de-computador',
]

from selenium import webdriver
from bs4 import BeautifulSoup
import re

for link in links:
    driver = webdriver.Firefox()
    driver.get(link)

    html_content = driver.page_source

    soup = BeautifulSoup(html_content, 'html.parser')
    text_content = ' '.join(soup.stripped_strings)

    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
    phone_pattern = re.compile(r'\+?(?:\d{2})?\s*(?:\d{2})?\s*\d?\s*[\d]{4}[\s-]*[\d]{4}')

    emails = email_pattern.findall(text_content)
    phones = phone_pattern.findall(text_content)

    print("Emails found:")
    for email in emails:
        print(f'Email: {email}')

    print("\nPhone numbers found:")
    for phone in phones:
        print(f'Phone: {phone}')

    driver.quit()
