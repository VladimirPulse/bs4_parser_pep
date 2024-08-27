import csv
import logging
import re
from urllib.parse import urljoin

from prettytable import PrettyTable
import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from src.constants import BASE_DIR

MAIN_PEP_URL = 'https://peps.python.org/'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
# def whats_new(session):
#     whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
#     response = get_response(session, whats_new_url)
#     if response is None:
#         return
#     soup = BeautifulSoup(response.text, 'lxml')
#     main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
#     div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
#     sections_by_python = div_with_ul.find_all('li', attrs={'class': 'toctree-l1'})
#     results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
#     for section in tqdm(sections_by_python):
#         version_a_tag = section.find('a')
#         version_link = urljoin(whats_new_url, version_a_tag['href'])
#         response = get_response(session, version_link)
#         if response is None:
#             continue  
#         soup = BeautifulSoup(response.text, 'lxml')
#         h1 = find_tag(soup, 'h1')
#         dl = find_tag(soup, 'dl')
#         dl_text = dl.text.replace('\n', ' ')
#         results.append(
#             (version_link, h1.text, dl_text)
#         )
#     return results

# def latest_versions(session):
#     response = get_response(session, MAIN_DOC_URL)
#     if response is None:
#         return
#     soup = BeautifulSoup(response.text, 'lxml')
#     sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
#     ul_tags = sidebar.find_all('ul')
#     for ul in ul_tags:
#         if 'All versions' in ul.text:
#             a_tags = ul.find_all('a')
#             break
#     else:
#         raise Exception('Не найден список c версиями Python')
#     results = [('Ссылка на документацию', 'Версия', 'Статус')]
#     pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
#     for a_tag in a_tags:
#         link = a_tag['href']
#         text_match = re.search(pattern, a_tag.text)
#         if text_match is not None:  
#             version, status = text_match.groups()
#         else:  
#             version, status = a_tag.text, ''  
#         results.append(
#             (link, version, status)
#         )
#     return results

# def download(session):
#     downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
#     response = get_response(session, downloads_url)
#     if response is None:
#         return
#     soup = BeautifulSoup(response.text, 'lxml')
#     main_tag = find_tag(soup, 'div', attrs={'role': 'main'})
#     table_tag = find_tag(main_tag, 'table', attrs={'class': 'docutils'})
#     pdf_a4_tag = find_tag(table_tag, 'a', attrs={'href': re.compile(r'.+pdf-a4\.zip$')})
#     pdf_a4_link = pdf_a4_tag['href']
#     archive_url = urljoin(downloads_url, pdf_a4_link)
#     filename = archive_url.split('/')[-1]
#     downloads_dir = BASE_DIR / 'downloads'
#     downloads_dir.mkdir(exist_ok=True)
#     archive_path = downloads_dir / filename
#     response = session.get(archive_url)
#     with open(archive_path, 'wb') as file:
#         file.write(response.content)
#     print(filename)
#     logging.info(f'Архив был загружен и сохранён: {archive_path}')

#Начало нового кода

def pep_status_versions(pep_url):
    session = requests_cache.CachedSession()
    session.cache.clear()
    pep_url = urljoin(MAIN_PEP_URL, pep_url) 
    response = session.get(pep_url)
    response.encoding = 'utf-8'
    # import pdb; pdb.set_trace()
    soup = BeautifulSoup(response.text, 'lxml')
    dl_tag = soup.find('dl', attrs={'class': 'rfc2822 field-list simple'})
    status_value = dl_tag.select_one('dt:-soup-contains("Status")').find_next_sibling().string
    return status_value

def pep_data():
    session = requests_cache.CachedSession()
    response = session.get(MAIN_PEP_URL)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    table_tag = soup.find_all('table', {'class': 'pep-zero-table docutils align-default'})
    result = []
    for row in table_tag:
        first_column_tag = row.find_all('a', {'class': 'pep reference internal'})
        href_list = [tag['href'] for tag in first_column_tag]
        result += href_list
    status_counts = {}
    total_peps = 0
    mismatched_statuses = []
    for pep_url in tqdm(result[:10]):
        if pep_url != 'pep-0000/':
            page_status = pep_status_versions(pep_url)

            first_column_tag = soup.find('a', {'href': pep_url})
            preview_status = first_column_tag.find_previous('td').text[1:]
            if page_status not in EXPECTED_STATUS.get(preview_status, []):
                mismatched_statuses.append({
                    'PEP': pep_url,
                    'Page Status': page_status,
                    'Expected Statuses': EXPECTED_STATUS.get(preview_status, [])
                })
            if page_status in status_counts:
                status_counts[page_status] += 1
            else:
                status_counts[page_status] = 1
            total_peps += 1
    if mismatched_statuses:
        print("Несовпадающие статусы:")
        for mismatch in mismatched_statuses:
            print(f"PEP: {mismatch['PEP']}")
            print(f"Статус в карточке: {mismatch['Page Status']}")
            print(f"Ожидаемые статусы: {mismatch['Expected Statuses']}")
            print()

    result_dir = BASE_DIR / 'results'
    result_dir.mkdir(exist_ok=True)
    archive_path = result_dir / 'pep_status.csv'

    with open(archive_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Status', 'Count'])
        for status, count in status_counts.items():
            writer.writerow([status, count])
        writer.writerow(['Total', total_peps])
        
    # import pdb; pdb.set_trace()
 # Добавляем одну строку списком.
    print(status_counts)
    print(f'Total PEPs: {total_peps}')


    # pep_url = div_tag.find('a', {'class': 'pep reference internal'})['href']
    # status_tag = div_tag.find('abbr')
    # result = {}
    # result.update(pep_url, status_tag)
    # pdf_a4_link = pdf_a4_tag['href']
#     archive_url = urljoin(DOWNLOADS_URL, pdf_a4_link)
#     filename = archive_url.split('/')[-1]
#     # Сформируйте путь до директории downloads.
#     downloads_dir = BASE_DIR / 'downloads'
# # Создайте директорию.
#     downloads_dir.mkdir(exist_ok=True)
# # Получите путь до архива, объединив имя файла с директорией.
#     archive_path = downloads_dir / filename
#     response = session.get(archive_url)
# # В бинарном режиме открывается файл на запись по указанному пути.
#     with open(archive_path, 'wb') as file:
#     # Полученный ответ записывается в файл.
#         file.write(response.content)
#     print(filename)
    # print(table_tag.prettify())

def main():
    # Запускаем функцию с конфигурацией логов.
    # pep_status_versions()
    pep_data()

if __name__ == '__main__':
    main() 