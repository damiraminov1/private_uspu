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
        r.html.render(timeout=30, sleep=10)
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
    def get_content(url: str, group: str, day: dict) -> dict:
        while True:
            try:
                soup = Parser._get_soup(url=url + group)
                stud_r = soup.find('div', attrs={'class': 'stud-r'})
                items = stud_r.find_all('div', attrs={'class': 'rasp-item'})[
                    Parser.get_available_days(url, group).index(day)]  # paste here day
                lessons_count = len(items.find_all('span', attrs={'class': 'para-time'}))
                lessons = list()
                for i in range(lessons_count):
                    data = items.find_all('p')[i].getText().split('\n')  # list with lesson, auditorium, teacher, subgroup
                    lessons.append({
                        'time': items.find_all('span', attrs={'class': 'para-time'})[i].getText(),
                        # paste here para time by index,
                        'content': data
                    })
                result = {
                    'update': stud_r.find('script').get_text().split(r"$('.stud-r .rasp-update').html('")[1][:-8],
                    'lessons': lessons
                }
                return result
            except BaseException as e:
                time.sleep(5)
                print(e)


# EXAMPLES
# print(Parser.get_available_days(url=Config.URL, group='РиА-1931'))
# print(Parser.get_content(url=Config.URL, group='РиА-1931', day={'date': '15 февраля', 'week': 'Ср'}))

data = 'TECHNICAL INFO \n'
data += datetime.today().strftime("%d-%b-%Y (%H:%M:%S.%f)")
data += 'TECHNICAL INFO \n'
days = Parser.get_available_days(url=Config.URL, group='РиА-1931')
for day in days:
    data += f'{day["date"]} {day["week"]} \n\n'
    lessons = Parser.get_content(url=Config.URL, group="РиА-1931", day=day)["lessons"]
    for lesson in lessons:
        data += f'{lesson["time"]} \n'
        for info in lesson["content"]:
            data += f'{info} \n'.lstrip()
    data += '='*55

with open('content.pkl', 'wb') as f:
    pickle.dump(data, f)
