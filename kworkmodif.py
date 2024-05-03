import requests
from bs4 import BeautifulSoup
import json
import re
from markdownify import markdownify as md

def parse_article(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        article = soup.find('article', class_='text-box')
        if article:
            # Получаем данные о статье
            domain = url.split('/')[2]
            content_type = response.headers.get('Content-Type')
            publication_date = response.headers.get('Date')
            title = article.find('h1').text.strip()
            lead_html = str(article.find('p'))  # Первый параграф в HTML
            lead_markdown = md(lead_html)  # Преобразуем lead_html в Markdown
            author = article.find('div', class_='author').text.strip() if article.find('div', class_='author') else None
            # Получаем контент в HTML и Markdown
            content_html = str(article) 
            content_html = re.sub(fr'<h1[^>]*>{title}</h1>', '', content_html, flags=re.IGNORECASE)
            content_markdown = md(content_html)  # Преобразуем content_html в Markdown

            return {
                'domain': domain,
                'url': url,
                'content_type': content_type,
                'publication_date': publication_date,
                'title': title,
                'lead_html': lead_html,
                'lead_markdown': lead_markdown,
                'content_html': content_html,
                'content_markdown': content_markdown,
                'author': author
            }
    except Exception as e:
        print(f"Ошибка при парсинге статьи: {url}")
        print(e)
    return None

def parse_page(url):
    articles_data = []
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Парсинг статей с текущей страницы
        thematic_articles = soup.find_all('div', class_='links-box-i')
        for thematic_article in thematic_articles:
            links = thematic_article.find_all('a', href=True)
            for link in links:
                article_url = requests.compat.urljoin(url, link['href'])
                print(f"Парсим статью: {article_url}")
                article_data = parse_article(article_url)
                if article_data:
                    articles_data.append(article_data)
                    print(f"Статья '{article_data['title']}' успешно спарсена.")
                    print(f"Обработано статей: {len(articles_data)}")

    except Exception as e:
        print(f"Ошибка при получении ссылок: {url}")
        print(e)
    return articles_data

def main():
    # Открываем файл с ссылками для парсинга
    with open('urls.txt', 'r') as file:
        urls = file.readlines()

    # Получаем список ссылок на страницы с тематическими разделами и книгами
    articles_data = []
    for url in urls:
        url = url.strip()  # Удаляем лишние символы (перевод строки, пробелы)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        sections = soup.find_all('div', class_='links-box-i')
        for section in sections:
            links = section.find_all('a', href=True)
            for link in links:
                section_url = requests.compat.urljoin(url, link['href'])
                articles_data += parse_page(section_url)

    print(f"Найдено {len(articles_data)} статей для парсинга.")

    # Сохраняем результаты в файл JSON с кодировкой UTF-8
    with open('articles.json', 'w', encoding='utf-8') as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=4)
        print("Все статьи успешно сохранены в файле 'articles.json'.")

if __name__ == "__main__":
    main()
