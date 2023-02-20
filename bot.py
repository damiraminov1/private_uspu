import os
import pickle
import datetime

from aiogram.utils import exceptions, executor
from aiogram import Bot, Dispatcher, types

from config import Config


bot = Bot(token=Config.TOKEN)
dp = Dispatcher(bot)


def user_has_permission(user_id: int) -> bool:
    if user_id == Config.OWN_ID or user_id == Config.USER_ID:
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
        with open("DATA.txt", "r") as text_file:
            loaded_str = text_file.read()
        tech_time = datetime.datetime.strptime(loaded_str.split('TECHNICAL INFO \n')[1], '%d-%b-%Y (%H:%M:%S.%f)')
        now = datetime.datetime.now()
        delta = now - tech_time
        warning_notification = delta >= datetime.timedelta(minutes=7)
        if warning_notification:
            await bot.send_message(
                chat_id=callback.from_user.id,
                text=f"WARNING: РАСПИСАНИЕ ПОСЛЕДНИЙ РАЗ ОБНОВЛЯЛОСЬ: {delta} ВРЕМЕНИ НАЗАД."
                     f" АКТУАЛЬНОСТЬ РАСПИСАНИЯ ПОД ВОПРОСОМ, НАПИШИ ДАМИРУ ↓ https://t.me/damiraminov1"
            )
            await bot.send_message(
                chat_id=callback.from_user.id,
                text=f"А пока, посмотри пожалуйста, расписание самостоятельно:"
                     f" https://uspu.ru/education/eios/schedule/?group_name=РиА-1931"
            )
        data = loaded_str.split('TECHNICAL INFO \n')[2].split('='*55)
        for message in data:
            if message:
                await bot.send_message(chat_id=callback.from_user.id, text=message)
