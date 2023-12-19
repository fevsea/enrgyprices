import unittest
from unittest.mock import patch, Mock

from bs4 import BeautifulSoup

import scraper


class TestFetchData(unittest.TestCase):
    DUMMY_WEBSITE = """<table class="table table-bordered"><caption class="table__title">Precio de la luz por horas</caption> <thead><tr><th>Hora</th> <th>Península,<br>Baleares y Canarias</th> <th>Ceuta y Melilla</th> </tr></thead><td class="nowrap">0.12365 €/kWh<br></td><tbody><tr><td class="nowrap"><strong>00h</strong></td> <td class="nowrap">0.12292 €/kWh<br></td> <td class="nowrap">0.12292 €/kWh</td> </tr><tr><td class="nowrap"><strong>01h</strong></td>  <td class="nowrap">0.12365 €/kWh</td> </tr><tr><td class="nowrap"><strong>02h</strong></td> <td class="nowrap">0.12054 €/kWh<br></td> <td class="nowrap">0.12054 €/kWh</td> </tr><tr><td class="nowrap"><strong>03h</strong></td> <td class="nowrap">0.12062 €/kWh<br></td> <td class="nowrap">0.12062 €/kWh</td> </tr><tr><td class="nowrap"><strong>04h</strong></td> <td class="nowrap">0.11965 €/kWh<br></td> <td class="nowrap">0.11965 €/kWh</td> </tr><tr><td class="nowrap"><strong>05h</strong></td> <td class="nowrap">0.12019 €/kWh<br></td> <td class="nowrap">0.12019 €/kWh</td> </tr><tr><td class="nowrap"><strong>06h</strong></td> <td class="nowrap">0.12507 €/kWh<br></td> <td class="nowrap">0.12507 €/kWh</td> </tr><tr><td class="nowrap"><strong>07h</strong></td> <td class="nowrap">0.14266 €/kWh<br></td> <td class="nowrap">0.14266 €/kWh</td> </tr><tr><td class="nowrap"><strong>08h</strong></td> <td class="nowrap">0.17136 €/kWh<br></td> <td class="nowrap">0.17136 €/kWh</td> </tr><tr><td class="nowrap"><strong>09h</strong></td> <td class="nowrap">0.16331 €/kWh<br></td> <td class="nowrap">0.16331 €/kWh</td> </tr><tr><td class="nowrap"><strong>10h</strong></td> <td class="nowrap">0.18959 €/kWh<br></td> <td class="nowrap">0.14372 €/kWh</td> </tr><tr><td class="nowrap"><strong>11h</strong></td> <td class="nowrap">0.1809 €/kWh<br></td> <td class="nowrap">0.1809 €/kWh</td> </tr><tr><td class="nowrap"><strong>12h</strong></td> <td class="nowrap">0.17387 €/kWh<br></td> <td class="nowrap">0.17387 €/kWh</td> </tr><tr><td class="nowrap"><strong>13h</strong></td> <td class="nowrap">0.17374 €/kWh<br></td> <td class="nowrap">0.17374 €/kWh</td> </tr><tr><td class="nowrap"><strong>14h</strong></td> <td class="nowrap">0.13624 €/kWh<br></td> <td class="nowrap">0.18218 €/kWh</td> </tr><tr><td class="nowrap"><strong>15h</strong></td> <td class="nowrap">0.13989 €/kWh<br></td> <td class="nowrap">0.13989 €/kWh</td> </tr><tr><td class="nowrap"><strong>16h</strong></td> <td class="nowrap">0.15446 €/kWh<br></td> <td class="nowrap">0.15446 €/kWh</td> </tr><tr><td class="nowrap"><strong>17h</strong></td> <td class="nowrap">0.16969 €/kWh<br></td> <td class="nowrap">0.16969 €/kWh</td> </tr><tr><td class="nowrap"><strong>18h</strong></td> <td class="nowrap">0.22807 €/kWh<br></td> <td class="nowrap">0.18193 €/kWh</td> </tr><tr><td class="nowrap"><strong>19h</strong></td> <td class="nowrap">0.26614 €/kWh<br></td> <td class="nowrap">0.26614 €/kWh</td> </tr><tr><td class="nowrap"><strong>20h</strong></td> <td class="nowrap">0.29447 €/kWh<br></td> <td class="nowrap">0.29447 €/kWh</td> </tr><tr><td class="nowrap"><strong>21h</strong></td> <td class="nowrap">0.24068 €/kWh<br></td> <td class="nowrap">0.24068 €/kWh</td> </tr><tr><td class="nowrap"><strong>22h</strong></td> <td class="nowrap">0.17277 €/kWh<br></td> <td class="nowrap">0.21888 €/kWh</td> </tr><tr><td class="nowrap"><strong>23h</strong></td> <td class="nowrap">0.16741 €/kWh<br></td> <td class="nowrap">0.16741 €/kWh</td> </tr></tbody></table>""".encode("utf8")
    
    @patch('scraper.requests.get')
    def test_fetch_data_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = self.DUMMY_WEBSITE
        mock_get.return_value = mock_response

        result = scraper.get_http_content("www.example.com", "2022-10-12")

        self.assertEqual(result, self.DUMMY_WEBSITE.decode("utf8"))

    @patch('scraper.requests.get')
    def test_fetch_data_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        with self.assertRaises(Exception):
            result = scraper.get_http_content(scraper.URL, "2022-10-12")


    def test_valid_price(self):
        self.assertEqual(scraper.parse_single_date_price(
            "\n\n\n\n\xa0\n00:00 - 01:00\n\n\n0.12292 €/kWh\n\n\n\n\n"
        ),
        0.12292)
        self.assertEqual(scraper.parse_single_date_price(
            "\n\n\n\n\xa0\n99:99 - 01:00\n\n\n0 €/kWh\n\n\n\n\n"
        ),
        0)

    def test_no_price(self):
        with self.assertRaises(ValueError):
            scraper.parse_single_date_price('Hello world!\n')

    def test_append_reading_to_data_middle(self):
        existing_data = ['2022-01-01, 12.3', '2022-01-03, 14.5']
        date = '2022-01-02'
        data = [13.4]
        new_data = scraper.append_reading_to_data(date, data, existing_data)
        self.assertEqual(new_data, ['2022-01-01, 12.3', '2022-01-02, 13.4', '2022-01-03, 14.5'])

    def test_append_reading_to_data_existing(self):
        existing_data = ['2022-01-01, 12.3', '2022-01-02, 14.5']
        date = '2022-01-02'
        data = [13.4]
        new_data = scraper.append_reading_to_data(date, data, existing_data)
        self.assertEqual(new_data, ['2022-01-01, 12.3', '2022-01-02, 13.4'])

    def test_append_reading_to_data_end(self):
        existing_data = ['2022-01-01, 12.3', '2022-01-02, 14.5']
        date = '2022-01-03'
        data = [13.4]
        new_data = scraper.append_reading_to_data(date, data, existing_data)
        self.assertEqual(new_data, ['2022-01-01, 12.3', '2022-01-02, 14.5', '2022-01-03, 13.4'])

    def test_append_reading_to_data_start(self):
        existing_data = ['2022-01-02, 12.3', '2022-01-03, 14.5']
        date = '2022-01-01'
        data = [13.4]
        new_data = scraper.append_reading_to_data(date, data, existing_data)
        self.assertEqual(new_data, ['2022-01-01, 13.4', '2022-01-02, 12.3', '2022-01-03, 14.5'])

if __name__ == '__main__':
    unittest.main()
