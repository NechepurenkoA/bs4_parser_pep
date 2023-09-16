import logging
import re
from urllib.parse import urljoin

from requests import Session
import requests_cache
from tqdm import tqdm

from constants import (
    BASE_DIR,
    MAIN_DOC_URL,
    PEP_URL,
    EXPECTED_STATUS,
    DOWNLOADS_POSTFIX,
    REGULAR_FOR_PYTHON
)
from configs import configure_argument_parser, configure_logging
from exceptions import ParserFindTagException
from outputs import control_output
from utils import find_tag, get_soup


def whats_new(session: Session) -> list[tuple[str, str, str]]:
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(session, whats_new_url)
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        soup = get_soup(session, version_link)
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session: Session) -> list[tuple[str, str, str]]:
    soup = get_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserFindTagException('Ничего не нашлось')
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for a_tag in a_tags:
        link = a_tag['href']
        if not re.search(REGULAR_FOR_PYTHON, a_tag.text):
            version = a_tag.text
            status = ''
        else:
            text_match = re.search(REGULAR_FOR_PYTHON, a_tag.text)
            version = text_match.group('version')
            status = text_match.group('status')
        results.append((link, version, status))

    return results


def download(session: Session) -> None:
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, downloads_url)
    table_tag = find_tag(soup, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag,
        'a',
        {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOADS_POSTFIX
    try:
        downloads_dir.mkdir(exist_ok=True)
    except (FileNotFoundError, OSError) as exc:
        logging.critical(f'Произошла ошибка при создании папки: {exc}')
        return
    archive_path = downloads_dir / filename
    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session: Session) -> list[tuple[str, str]]:
    soup = get_soup(session, PEP_URL)
    section_tag = find_tag(soup, 'section', {'id': 'numerical-index'})
    tbody_tag = find_tag(section_tag, 'tbody')
    tr_tags = tbody_tag.find_all('tr')
    st_sum = {}
    total = 0
    result = [('Статусы', 'Кол-во')]
    for tr in tr_tags:
        preview_st = find_tag(tr, 'td').text[1:]
        a_href = find_tag(tr, 'a')['href']
        link = urljoin(PEP_URL, a_href)
        pep_soup = get_soup(session, link)
        dt_tags = pep_soup.find_all('dt')
        for dt in dt_tags:
            if dt.text == 'Status:':
                total += 1
                status = dt.find_next_sibling().string
                if status in st_sum:
                    st_sum[status] += 1
                if status not in st_sum:
                    st_sum[status] = 1
                if status not in EXPECTED_STATUS[preview_st]:
                    msg = f"""
                        Несовпадающие статусы:
                        {link}
                        Статус в карточке: {status}
                        Ожидаемые статусы: {EXPECTED_STATUS[preview_st]}
                    """
                    logging.warning(msg)

    for status in st_sum:
        result.append((status, st_sum[status]))
    result.append(('Total', total))
    return result


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main() -> None:
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

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
