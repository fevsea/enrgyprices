import os
import pathlib

import requests
from bs4 import BeautifulSoup
import argparse
from base64 import b64decode
from datetime import datetime

URL = b64decode("aHR0cHM6Ly90YXJpZmFsdXpob3JhLmVzLw==").decode('utf-8')
FILENAME = "prices.csv"


def get_http_content(url: str, date: str) -> str:
    """
    Fetches data from a URL for a specific date.

    :param url: The URL to fetch the data from.
    :param date: The specific date for which the data is requested as a string in YYYY-MM-DD.
    :return: The fetched data as a decoded string.
    :raises Exception: If the HTTP response status code is not 200.
    """
    response = requests.get(url, params={"date": date})
    if response.status_code != 200:
        raise Exception(f"Status code {response.status_code} is not valid")
    return response.content.decode()


def parse_single_date_price(text: str) -> float:
    """
    Extracts the price from a given string. It must contain the format "\n0.12292 €/kWh\n*"

    :param text: The string from which to extract the price.
    :return: The extracted price as a float.
    :raises ValueError: If cannot extract the price.
    Example:
        >>> parse_single_date_price("\n\n\n\n\n00:00 - 01:00\n\n\n0.12292 €/kWh\n\n\n\n\n")
        0.12292
    """
    price_string = "".join([s for s in text.split("\n") if any(c.isdigit() for c in s) and ":" not in s])
    price = float(price_string.split(" ")[0])
    if type(price) != float:
        raise ValueError
    return price


def parse_website(html_content: str) -> list[float]:
    """
    Parse the website's HTML content and extract prices.

    This is not a generic function, is tailored to the actual website.

    :param html_content: The HTML content of the website.
    :return: A list of extracted prices.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    date_prices = []
    header = soup.find("p", {"class": "template-tlh__colors--hours-title"})
    for row in header.parent.find_all('div', class_='row'):
        line = row.get_text()
        price = parse_single_date_price(line)
        date_prices.append(price)
    return date_prices


def get_existing_data(filename: pathlib.Path) -> list[str]:
    """
    :param filename: The path to the file containing the existing data.
    :return: A list of strings representing the existing data.
    """
    if filename.exists():
        with open(filename, "r") as file:
            return file.read().splitlines()
    else:
        return ["date, " + ", ".join([str(hour) for hour in range(0, 24)])]


def binary_search_line_for_date(existing_data: list[str], date: datetime, low: int, high: int, up=True) -> [int, bool]:
    """
    :param existing_data: A list of existing data, sorted by date in ascending order.
    :param date: The date being searched for.
    :param low: The starting index of the search range.
    :param high: The ending index of the search range.
    :param up: Whether we expected the position to be up or down on the last iteration
    :return: A tuple containing the index of where the record should be inserted and if it exists
    """
    if high >= low:
        mid = (low + high) // 2
        mid_date = datetime.strptime(existing_data[mid].split(",")[0], '%Y-%m-%d')
        if mid_date == date:
            return mid, True
        elif mid_date < date:
            return binary_search_line_for_date(existing_data, date, mid + 1, high, True)
        else:
            return binary_search_line_for_date(existing_data, date, low, mid - 1, False)
    else:
        # The record is missing. Depending on whether we were expecting the data to be lower of higher than
        # the middle, we will return one index or the other
        if up:
            return high+1, False
        else:
            return low, False

def append_reading_to_data(date_str: str, data: list[float], existing_data) -> list[str]:
    """
    Append a reading to existing data.

    :param date_str: A string representing the date of the reading in the format 'YYYY-MM-DD'.
    :param data: A list of floating-point numbers representing the reading data.
    :param existing_data: A list of strings representing lines of the CSV.
    :return: A list of strings representing the updated data, with the new reading appended.

    Example:
    ```
    >>> append_reading_to_data('2022-01-01', [12.3, 45.6, 78.9], ['2021-12-31, 10.1, 20.2, 30.3', '2022-01-02, 15.5, 25.5, 35.5'])
    ['2021-12-31, 10.1, 20.2, 30.3', '2022-01-01, 12.3, 45.6, 78.9', '2022-01-02, 15.5, 25.5, 35.5']
    ```
    """
    date = datetime.strptime(date_str, '%Y-%m-%d')
    new_data = date_str + ", " + ", ".join([str(d) for d in data])

    line, exists = binary_search_line_for_date(existing_data, date, 0, len(existing_data) - 1)
    if exists:
        existing_data[line] = new_data
    else:
        existing_data.insert(line, new_data)
    return existing_data


def save_file(filename: pathlib.Path, data: list[str]) -> None:
    """
    Write data to a file

    :param filename: The path of the file to save the data.
    :param data: The list of strings to be written to the file.
    :return: None
    """
    joined_data = "\n".join(data)
    with open(filename, 'w') as f:
            f.write(joined_data)

def save_data(date: str, data: list[float], filename: pathlib.Path) -> None:
    """
    Merges and persist the new record

    :param date: The date of the data.
    :type date: str
    :param data: The list of data to be saved.
    :type data: list[float]
    :param filename: The path to the file where the data will be saved.
    :type filename: pathlib.Path
    :return: None
    """
    header, *existing_data = get_existing_data(filename)
    new_data = append_reading_to_data(date, data, existing_data)
    save_file(filename, [header] + new_data)


def main(path: pathlib.Path, date: str):
    """
    :param path: The path where the data will be saved.
    :param date: The date for which the data will be fetched and saved as string YYYY-MM-DD
    :return: None
    """
    html_content = get_http_content(URL, date)
    data = parse_website(html_content)
    save_data(date, data, path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gets the energy prices of a single day and updates the CSV")

    parser.add_argument('-f', '--filepath',
                        default=pathlib.Path.cwd() / FILENAME,
                        type=pathlib.Path,
                        help='Where to save the data. Expects a path of a csv file. If the CSV exists it must be ordered')

    parser.add_argument('-d', '--date',
                        default=datetime.today().strftime('%Y-%m-%d'),
                        type=str,
                        help='The date in "YYYY-MM-DD" format')

    args = parser.parse_args()
    main(args.filepath, args.date)