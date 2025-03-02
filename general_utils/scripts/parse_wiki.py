import requests
from bs4 import BeautifulSoup
from mysql.connector import MySQLConnection, Error

from general_utils import read_db_config


def get_cities():
    db_config = read_db_config()
    try:
        with MySQLConnection(**db_config) as conn:
            with conn.cursor() as curr:
                query = "SELECT city FROM cities"
                curr.execute(query)
                cities = curr.fetchall()  # Fetch all results
                return [city[0] for city in cities]  # Extract city names into a list
    except Error as e:
        print(f"Ошибка при работе с базой данных: {e}")


def save_result(cities_and_regions):
    # Получаем конфигурацию подключения к базе данных
    db_config = read_db_config()
    try:
        with MySQLConnection(**db_config) as conn:
            with conn.cursor() as curr:
                # Вставляем данные
                query = "INSERT INTO cities (city, region) VALUES (%s, %s)"
                curr.executemany(query, cities_and_regions)

                # Сохраняем изменения
                conn.commit()

                print(f"Сохранено {curr.rowcount} записей в базу данных.")
    except Error as e:
        print(f"Ошибка при работе с базой данных: {e}")


def parse_cities_and_regions(url):
    response = requests.get(url)
    response.raise_for_status()  # Проверяем успешность запроса

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'standard'})  # Таблица со списком городов

    cities_and_regions = []

    if not table:
        print("Таблица не найдена на странице.")
        return cities_and_regions

    rows = table.find_all('tr')  # Строки таблицы

    for row in rows[1:]:  # Пропускаем заголовок таблицы
        cells = row.find_all('td')
        if len(cells) >= 2:  # Убедимся, что есть хотя бы две колонки
            city = cells[2].text.strip().lower()  # Название города
            region = cells[3].text.strip()  # Регион
            if city not in saved_cities:
                cities_and_regions.append((city, region))

    return cities_and_regions


# url = 'https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%B3%D0%BE%D1%80%D0%BE%D0%B4%D0%BE%D0%B2_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B8'
# cities_and_regions = parse_cities_and_regions(url)
saved_cities = get_cities()
cities_and_regions = []
with open('cities_and_regions.txt', encoding='utf-8') as file:
    for line in file:
        city, region = line.strip().split(':')
        if city.lower() not in saved_cities:
            cities_and_regions.append((city.lower(), region))
save_result(cities_and_regions)
