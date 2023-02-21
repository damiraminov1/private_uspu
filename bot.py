import datetime

from aiogram.utils import executor
from aiogram import Bot, Dispatcher, types

from config import Config

bot = Bot(token=Config.TOKEN)
dp = Dispatcher(bot)


def td_format(td_object: datetime) -> str:
    seconds = int(td_object.total_seconds())
    periods = [
        ('year', 60 * 60 * 24 * 365),
        ('month', 60 * 60 * 24 * 30),
        ('day', 60 * 60 * 24),
        ('hour', 60 * 60),
        ('minute', 60),
        ('second', 1)
    ]

    strings = []
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return ", ".join(strings)


def user_has_permission(user_id: int) -> bool:
    if user_id == int(Config.OWN_ID) or user_id == int(Config.USER_ID):
        return True


def get_start_markup() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    schedule_button = types.KeyboardButton('Расписание')
    markup.add(schedule_button)
    return markup


@dp.message_handler(commands='start')
async def start(message: types.Message):
    if user_has_permission(message.from_user.id):
        await message.reply(
            'Привет, Ксюшик❤️! Любое твое сообщение или кнопка - расписание',
            reply_markup=get_start_markup())


@dp.message_handler(content_types='text')
async def callback_handler(callback: types.CallbackQuery):
    if callback and user_has_permission(callback.from_user.id):
        try:
            with open("DATA.txt", "r") as text_file:
                loaded_str = text_file.read()
            tech_time = datetime.datetime.strptime(loaded_str.split('TECHNICAL INFO \n')[1], '%d-%b-%Y (%H:%M:%S.%f)')
            now = datetime.datetime.now()
            delta = now - tech_time
            warning_notification = delta >= datetime.timedelta(minutes=20)
            if warning_notification:
                await bot.send_message(
                    chat_id=callback.from_user.id,
                    text=f"WARNING: РАСПИСАНИЕ ПОСЛЕДНИЙ РАЗ ОБНОВЛЯЛОСЬ: {td_format(delta)} ВРЕМЕНИ НАЗАД."
                         f" АКТУАЛЬНОСТЬ РАСПИСАНИЯ ПОД ВОПРОСОМ, НАПИШИ ДАМИРУ ↓ https://t.me/damiraminov1"
                )
                await bot.send_message(
                    chat_id=callback.from_user.id,
                    text=f"А пока, посмотри пожалуйста, расписание самостоятельно:"
                         f" https://uspu.ru/education/eios/schedule/?group_name=РиА-1931"
                )
            data = loaded_str.split('TECHNICAL INFO \n')[2].split('=' * 55)
            for message in data:
                if message:
                    await bot.send_message(chat_id=callback.from_user.id, text=message)
        except BaseException:
            await bot.send_message(chat_id=callback.from_user.id,
                                   text="Подожди 10 минут, если не заработает,"
                                        " то пиши Дамиру ↓ https://t.me/damiraminov1")
