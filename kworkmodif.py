import requests
from bs4 import BeautifulSoup
import json
import re
from openpyxl import Workbook

def parse_article(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        article = soup.find('article', class_='text-box')
        if article:
            title = article.find('h1').text.strip()
            content = article.text.strip()
            return title, content
    except Exception as e:
        print(f"Ошибка при парсинге статьи: {url}")
        print(e)
    return None, None

def clean_filename(filename):
    # Заменяем запрещенные символы на дефис
    return re.sub(r'[\\/:*?"<>|]', '-', filename)

def main():
    # URL-адрес страницы для парсинга
    url = "https://www.cfin.ru/finanalysis/"

    # Получаем список ссылок на страницы с тематическими разделами и книгами
    articles_data = []
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        thematic_links_box = soup.find('div', class_='links-box-i').find('ul')
        thematic_links = thematic_links_box.find_all('a', href=True)
        for thematic_link in thematic_links:
            thematic_url = requests.compat.urljoin(url, thematic_link['href'])
            print(f"Обрабатываем ссылку: {thematic_url}")
            
            # Получаем список ссылок на статьи
            response = requests.get(thematic_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            articles_links_box = soup.find('div', class_='links-box-i').find('ul')
            articles_links = articles_links_box.find_all('a', href=True)
            for article_link in articles_links:
                article_url = requests.compat.urljoin(thematic_url, article_link['href'])
                print(f"Парсим статью: {article_url}")
                title, content = parse_article(article_url)
                if title and content:
                    clean_title = clean_filename(title)
                    article_data = {
                        'url': article_url,
                        'title': title,
                        'content': content
                    }
                    articles_data.append(article_data)
                    print(f"Статья '{title}' успешно спарсена.")
    except Exception as e:
        print(f"Ошибка при получении ссылок: {url}")
        print(e)

    # Сохраняем результаты в один файл JSON
    with open('articles.json', 'w', encoding='utf-8') as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=4)
        print("Все статьи успешно сохранены в файле 'articles.json'.")

    # Записываем данные в Excel-файл
    wb = Workbook()
    ws = wb.active
    ws.append(["URL", "Title"])
    for article in articles_data:
        ws.append([article['url'], article['title']])
    wb.save("articles.xlsx")
    print("Данные успешно сохранены в Excel-файле 'articles.xlsx'.")

if __name__ == "__main__":
    main()
