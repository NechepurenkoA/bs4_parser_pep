import logging

from bs4 import BeautifulSoup
from requests import RequestException, Session, Response

from exceptions import ParserFindTagException
from constants import LXML


def get_soup(session: Session, url: str):
    response = get_response(session, url)
    soup = BeautifulSoup(response.text, features=LXML)
    return soup


def get_response(session: Session, url: str) -> Response:
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )
        raise RequestException


def find_tag(
        soup: BeautifulSoup,
        tag: str,
        attrs: dict[str: str] = None
) -> str:
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
