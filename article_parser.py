"""Articles Parser"""
import sys
import pandas as pd
from newspaper import Article, Config
from newspaper.article import ArticleException
from console_progressbar import ProgressBar


HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel '
           'Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0',
           'Accept': 'text/html,application/xhtml+xml,'
           'application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Cookie': '__utma=40499190.288645356.1626172703.16261'
           '72703.1626172703.1; __utmc=40499190; __utmz=40499190.1627'
           '172703.1.1.utmcsr=(direct)|utmccn=(direct)|'
           'utmcmd=(none); __utmt=1; __qca=P0-462214369-16261727'
           '03831; _ga=GA1.2.288645356.1626172703; _gid=GA1.2.4211'
           '60026.1626172704; __aaxsc=1; coregval=ims; '
           'slogin=1626172892; slogin=1626172892; _gat_gtag_UA_1'
           '36162586_1=1; mnet_session_depth=10|1626172703923; '
           'aasd=10|1626172704511; __utmb=40499190.13.10.1626172703'}


def get_path_to_file() -> str:
    """Returns path to file from command-line arguments."""
    try:
        return sys.argv[1]
    except IndexError:
        print('Input filename requires!\n\n'
              'Example: python article_parser input.csv')
        sys.exit()


def get_article_text(url: str) -> str:
    """Retrieves the text of the article at the specified url."""
    config = Config()
    config.headers = HEADERS
    config.request_timeout = 7
    config.MAX_TEXT = 32766  # Excell cell limitation
    article = Article(url, config=config)
    try:
        article.download()
        article.parse()
    except ArticleException:
        return ''
    return article.text


def get_urls_from_csv(path_to_csv: str, encoding: str,
                      delimiter: str,
                      field_name: str) -> pd.core.series.Series:
    """Retrieves the URLs of articles from csv"""
    try:
        urls = pd.read_csv(path_to_csv, sep=delimiter,
                           encoding=encoding)[field_name]
    except FileNotFoundError:
        print('File not found!')
        sys.exit()
    return urls


def write_article_text_to_csv(path_to_csv: str, encoding: str,
                              delimiter: str, field_name: str,
                              articles: list) -> None:
    """Write parsed text of article to csv file."""
    try:
        csv_file = pd.read_csv(path_to_csv, sep=delimiter, encoding=encoding)
    except FileNotFoundError:
        print('File not found!')
        sys.exit()
    ser_article_text = pd.Series(data=articles)
    csv_file[field_name] = ser_article_text
    out_path_to_file, out_extension = path_to_csv.rsplit('.', 1)
    csv_file.to_csv(f'{out_path_to_file}_report.{out_extension}',
                    sep=delimiter, encoding=encoding)


if __name__ == '__main__':
    path = get_path_to_file()
    links = get_urls_from_csv(path, 'utf-16', '\t', 'URL')
    articles_text = []
    pb = ProgressBar(total=len(links), decimals=2, length=50)
    for index, link in enumerate(links):
        articles_text.append(get_article_text(link))
        pb.print_progress_bar(index+1)

    write_article_text_to_csv(path, 'utf-16', '\t', 'Body', articles_text)
