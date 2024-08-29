import csv
import logging
import re
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import (configure_argument_parser, configure_logging,
                     pep_status_logging)
from constants import (BASE_DIR, DOWNLOADS, EXPECTED_STATUS, MAIN_DOC_URL,
                       MAIN_PEP_URL, PEP_STATUS, RESULTS)
from exceptions import IsNoneRespons
from outputs import control_output
from utils import find_tag, generate_soup


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = generate_soup(session, whats_new_url)
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'})
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    messege_error = []
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        try:
            soup = generate_soup(session, version_link)
        except IsNoneRespons:
            messege_error.append(f'Не получен ответ на {version_link}')
            continue
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    if messege_error:
        logging.exception('\n'.join(messege_error))
    return results


def latest_versions(session):
    soup = generate_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise IsNoneRespons('Не найден список c версиями Python')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = generate_soup(session, downloads_url)
    main_tag = find_tag(soup, 'div', attrs={'role': 'main'})
    table_tag = find_tag(main_tag, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a', attrs={'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOADS
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def page_pep_status(pep_url):
    session = requests_cache.CachedSession()
    pep_url = urljoin(MAIN_PEP_URL, pep_url)
    soup = generate_soup(session, pep_url)
    dl_tag = soup.find('dl', attrs={'class': 'rfc2822 field-list simple'})
    status_value = dl_tag.select_one(
        'dt:-soup-contains("Status")').find_next_sibling().string
    return status_value


def pep(session):
    soup = generate_soup(session, MAIN_PEP_URL)
    table_tag = soup.find_all(
        'table', {'class': 'pep-zero-table docutils align-default'})
    result = []
    for row in table_tag:
        first_column_tag = row.find_all(
            'a', {'class': 'pep reference internal'})
        href_list = [tag['href'] for tag in first_column_tag]
        result += href_list
    status_counts = {}
    total_peps = 0
    mismatched_statuses = []
    messege_error = []
    for pep_url in tqdm(result):
        if pep_url != 'pep-0000/':
            try:
                page_status = page_pep_status(pep_url)
            except IsNoneRespons:
                messege_error.append(f'Не получен ответ на {pep_url}')
                continue
            first_column_tag = find_tag(soup, 'a', {'href': pep_url})
            preview_status = first_column_tag.find_previous('abbr').text[1:]
            if page_status not in EXPECTED_STATUS.get(preview_status, []):
                mismatched_statuses.append({
                    'PEP': pep_url,
                    'Page Status': page_status,
                    'Expected Statuses': EXPECTED_STATUS.get(
                        preview_status, [])
                })
            status_counts[page_status] = status_counts.get(page_status, 0) + 1
            total_peps += 1
    if messege_error:
        logging.exception('\n'.join(messege_error))
    if mismatched_statuses:
        pep_status_logging(mismatched_statuses)
    result_dir = BASE_DIR / RESULTS
    result_dir.mkdir(exist_ok=True)
    archive_path = result_dir / PEP_STATUS
    with open(archive_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Status', 'Count'])
        for status, count in status_counts.items():
            writer.writerow([status, count])
        writer.writerow(['Total', total_peps])


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    try:
        configure_logging()
        logging.info('Парсер запущен!')
        arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
        args = arg_parser.parse_args()
        logging.info(f'Аргументы командной строки: {args}')
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
    except ValueError as e:
        logging.error(f"Произошла ошибка: {e}")
        raise ValueError("Ошибка при обработке входных данных")
    except TypeError as e:
        logging.error(f"Произошла ошибка: {e}")
        raise TypeError("Ошибка типа данных")
    except IOError as e:
        logging.error(f"Произошла ошибка: {e}")
        raise IOError("Ошибка при работе с файлом")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        raise Exception("Неизвестная ошибка")
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
