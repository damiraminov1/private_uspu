import os.path
from pathlib import Path
from dotenv import load_dotenv

basedir = Path(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    TOKEN = os.environ.get('BOT_TOKEN')
    URL = 'https://uspu.ru/education/eios/schedule/?group_name='
    OWN_ID = os.environ.get('OWN_ID')
    USER_ID = os.environ.get('USER_ID')
