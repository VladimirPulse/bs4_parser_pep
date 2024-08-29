import logging

from bs4 import BeautifulSoup

from exceptions import IsNoneRespons, ParserFindTagException


def get_response(session, url, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except ConnectionError as e:
        raise IsNoneRespons(
            f'Ошибка при загрузке страницы {url}: {str(e)}'
        ) from e


def generate_soup(session, url):
    try:
        response = get_response(session, url)
        if response is None:
            raise IsNoneRespons("Возникла ошибка при загрузке страницы")
        return BeautifulSoup(response.text, 'lxml')
    except IsNoneRespons:
        raise


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
