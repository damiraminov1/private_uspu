from datetime import datetime
import pickle
import time

from requests_html import HTMLSession
from bs4 import BeautifulSoup

from config import Config


class Parser:
    @staticmethod
    def _get_html(url):
        session = HTMLSession()
        r = session.get(url=url)
        r.html.render(timeout=60, sleep=60)
        if Parser._server_is_respond(r):
            return r.html.html
        else:
            raise ConnectionError('Status code = {code}'.format(code=r.status_code))

    @staticmethod
    def _server_is_respond(html) -> bool:
        return True if html.status_code == 200 else False

    @staticmethod
    def _get_soup(url: str) -> BeautifulSoup or str:
        try:
            soup = BeautifulSoup(Parser._get_html(url), 'html.parser')
            return soup
        except ConnectionError:
            return "Can't Parse!"

    @staticmethod
    def get_groups(url: str) -> list:
        soup = Parser._get_soup(url=url)
        groups = soup.find('select', attrs={'name': 'group_name'})
        return groups.text.split('\n')[2:-2]

    @staticmethod
    def get_available_days(url: str, group: str):
        while True:
            try:
                soup = Parser._get_soup(url=url + group)
                stud_r = soup.find('div', attrs={'class': 'stud-r'})
                items = stud_r.find_all('div', attrs={'class': 'rasp-item'})
                days = list()
                for item in range(len(items)):
                    days.append({
                        'date': items[item].find('span', attrs={'class': 'rasp-day'}).getText(),
                        'week': items[item].find('div', attrs={'class': 'rasp-week'}).getText()
                    })
                return days
            except BaseException as e:
                time.sleep(5)
                print(e)

    @staticmethod
    def get_content(url: str, group: str) -> dict:
        while True:
            try:
                soup = Parser._get_soup(url=url + group)
                stud_r = soup.find('div', attrs={'class': 'stud-r'})
                new_data = {
                    'update': stud_r.find('script').get_text().split(r"$('.stud-r .rasp-update').html('")[1][:-20],
                    'days': list()
                }
                days = stud_r.find_all('div', attrs={'class': 'rasp-item'})
                for raw_day in days:
                    lessons_raw = raw_day.find_all('span', attrs={'class': 'para-time'})
                    lessons = list()
                    for idx, x in enumerate(lessons_raw):
                        data = raw_day.find_all('p')[idx].getText().split('\n')
                        dd = f'{x.getText()} \n '
                        for element in data:
                            dd += f'{element.strip()} \n'
                        lessons.append(dd)
                    new_data['days'].append(lessons)
                return new_data
            except BaseException as e:
                time.sleep(5)
                print(e)

    @staticmethod
    def create_data() -> str:
        while True:
            try:
                data = 'TECHNICAL INFO \n'
                data += datetime.today().strftime("%d-%b-%Y (%H:%M:%S.%f)")
                data += 'TECHNICAL INFO \n'
                data_lst = Parser.get_content(url=Config.URL, group="РиА-1931")
                data += f'{data_lst["update"]} \n'
                data += '=' * 55
                for day in data_lst["days"]:
                    data += '\n'
                    for lesson in day:
                        correct_lesson = lesson.lstrip()
                        data += f'{correct_lesson}'
                    data += '=' * 55
                return data
            except:
                continue

# EXAMPLES
# print(Parser.get_available_days(url=Config.URL, group='РиА-1931'))
# print(datetime.now().strftime('%d-%b-%Y (%H:%M:%S.%f)'))
# print(Parser.get_content(url=Config.URL, group='РиА-1931'))
# print(datetime.now().strftime('%d-%b-%Y (%H:%M:%S.%f)'))


while True:
    data = Parser.create_data()
    with open("DATA.txt", "w") as text_file:
        text_file.write(data)
